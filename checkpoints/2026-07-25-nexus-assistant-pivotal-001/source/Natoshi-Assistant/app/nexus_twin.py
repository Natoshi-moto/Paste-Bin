#!/usr/bin/env python3
"""Typed twin-agent and evidence-plane primitives for NEXUS ASSISTANT.

The model roles in this module are deliberately non-authoritative:

* PILOT may produce the user-facing answer and action proposals.
* WITNESS may route, retrieve, comment, and dissent.
* deterministic host code owns validation, attachment, cancellation, and effects.

Evidence packets stay outside the chat transcript until the operator explicitly
attaches them (or a bounded, clearly labelled per-turn retrieval policy does).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from nexus_core import NEXUS_STATE_DIR, ModelRecord, redact_sensitive_text

try:
    import fcntl
except ImportError:  # pragma: no cover - NEXUS currently targets Linux.
    fcntl = None


TWIN_SCHEMA = "nexus.twin/v1"
EVIDENCE_SCHEMA = "nexus.evidence/v1"
EVIDENCE_STATE_PATH = NEXUS_STATE_DIR / "evidence_packets.json"
ATTACHMENT_TARGETS = {"NONE", "PILOT", "WITNESS", "BOTH"}
EVIDENCE_KINDS = {"SYSTEM_GREP", "NEWS_SEARCH", "BROWSER", "FILE", "MANUAL"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def _bounded_clean(value: Any, limit: int) -> str:
    text = redact_sensitive_text(" ".join(str(value or "").split()))
    return text[:limit]


@dataclass(frozen=True)
class EvidenceItem:
    """One inspectable locator/excerpt inside an evidence packet."""

    item_id: str
    kind: str
    title: str
    locator: str
    excerpt: str
    line: int | None = None
    excerpt_fingerprint: str = ""
    source_sha256: str = ""
    retrieved: bool = True
    inspected: bool = False

    @classmethod
    def create(
        cls,
        *,
        kind: str,
        title: str,
        locator: str,
        excerpt: str,
        line: int | None = None,
        source_sha256: str = "",
        retrieved: bool = True,
        inspected: bool = False,
    ) -> "EvidenceItem":
        clean_title = _bounded_clean(title, 240)
        clean_locator = _bounded_clean(locator, 1000)
        clean_excerpt = _bounded_clean(excerpt, 900)
        digest_input = (
            f"{kind}\0{clean_locator}\0{line or 0}\0{clean_excerpt}"
        )
        digest = _sha256_text(digest_input)
        return cls(
            item_id=f"item-{digest[:16]}",
            kind=_bounded_clean(kind, 40) or "SOURCE",
            title=clean_title or clean_locator or "untitled evidence",
            locator=clean_locator,
            excerpt=clean_excerpt,
            line=line if isinstance(line, int) and line > 0 else None,
            excerpt_fingerprint=digest,
            source_sha256=_bounded_clean(source_sha256, 128),
            retrieved=bool(retrieved),
            inspected=bool(inspected),
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidenceItem":
        return cls.create(
            kind=str(payload.get("kind") or "SOURCE"),
            title=str(payload.get("title") or ""),
            locator=str(payload.get("locator") or ""),
            excerpt=str(payload.get("excerpt") or ""),
            line=payload.get("line") if isinstance(payload.get("line"), int) else None,
            source_sha256=str(payload.get("source_sha256") or ""),
            retrieved=bool(payload.get("retrieved", True)),
            inspected=bool(payload.get("inspected", False)),
        )


@dataclass
class EvidencePacket:
    """A parked or explicitly attached context packet.

    `status_authority` is fixed to NONE: retrieval is candidate evidence, not a
    canonical decision, permission grant, or proof that an excerpt is true.
    """

    packet_id: str
    created_at: str
    kind: str
    query_redacted: str
    query_sha256: str
    items: list[EvidenceItem] = field(default_factory=list)
    exclusions: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    attachment: str = "NONE"
    semantic_class: str = "OBSERVED"
    evidence_class: str = "DRAFT"
    status_authority: str = "NONE"
    schema: str = EVIDENCE_SCHEMA

    @classmethod
    def create(
        cls,
        *,
        kind: str,
        query: str,
        items: Iterable[EvidenceItem],
        exclusions: Iterable[str] = (),
        errors: Iterable[str] = (),
    ) -> "EvidencePacket":
        packet_kind = str(kind).upper()
        if packet_kind not in EVIDENCE_KINDS:
            raise ValueError(f"unsupported evidence kind: {kind}")
        clean_query = _bounded_clean(query, 1200)
        query_digest = _sha256_text(clean_query)
        nonce = uuid.uuid4().hex[:8]
        created_at = _utc_now()
        packet_id = (
            f"ev-{created_at[:10].replace('-', '')}-"
            f"{query_digest[:8]}-{nonce}"
        )
        return cls(
            packet_id=packet_id,
            created_at=created_at,
            kind=packet_kind,
            query_redacted=clean_query,
            query_sha256=query_digest,
            items=list(items)[:40],
            exclusions=[_bounded_clean(item, 300) for item in exclusions][:30],
            errors=[_bounded_clean(item, 300) for item in errors][:20],
        )

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EvidencePacket":
        kind = str(payload.get("kind") or "").upper()
        attachment = str(payload.get("attachment") or "NONE").upper()
        if kind not in EVIDENCE_KINDS:
            raise ValueError("invalid evidence kind")
        if attachment not in ATTACHMENT_TARGETS:
            attachment = "NONE"
        items_payload = payload.get("items")
        if not isinstance(items_payload, list):
            items_payload = []
        clean_query = _bounded_clean(payload.get("query_redacted"), 1200)
        return cls(
            packet_id=_bounded_clean(payload.get("packet_id"), 100)
            or f"ev-recovered-{uuid.uuid4().hex[:12]}",
            created_at=_bounded_clean(payload.get("created_at"), 80) or _utc_now(),
            kind=kind,
            query_redacted=clean_query,
            query_sha256=_sha256_text(clean_query),
            items=[
                EvidenceItem.from_dict(item)
                for item in items_payload[:40]
                if isinstance(item, dict)
            ],
            exclusions=[
                _bounded_clean(item, 300)
                for item in (payload.get("exclusions") or [])[:30]
            ],
            errors=[
                _bounded_clean(item, 300)
                for item in (payload.get("errors") or [])[:20]
            ],
            attachment=attachment,
            semantic_class="OBSERVED",
            evidence_class="DRAFT",
            status_authority="NONE",
            schema=EVIDENCE_SCHEMA,
        )

    def summary(self) -> str:
        return (
            f"{self.packet_id} · {self.kind} · {len(self.items)} item(s) · "
            f"{self.attachment}"
        )


@dataclass(frozen=True)
class TwinEnvelope:
    """Small typed coordination envelope shared by the two model roles."""

    event_id: str
    turn_id: str
    generation: int
    created_at: str
    from_agent: str
    to_agent: str
    kind: str
    semantic_class: str
    payload_sha256: str
    refs: tuple[str, ...] = ()
    hop_count: int = 0
    hop_limit: int = 4
    status_authority: str = "NONE"
    schema: str = TWIN_SCHEMA

    @classmethod
    def create(
        cls,
        *,
        turn_id: str,
        generation: int,
        from_agent: str,
        to_agent: str,
        kind: str,
        semantic_class: str,
        payload: str,
        refs: Iterable[str] = (),
    ) -> "TwinEnvelope":
        if from_agent not in {"PILOT", "WITNESS", "HOST"}:
            raise ValueError("invalid sender")
        if to_agent not in {"PILOT", "WITNESS", "HOST"}:
            raise ValueError("invalid recipient")
        return cls(
            event_id=f"evt-{uuid.uuid4().hex}",
            turn_id=_bounded_clean(turn_id, 120),
            generation=max(0, int(generation)),
            created_at=_utc_now(),
            from_agent=from_agent,
            to_agent=to_agent,
            kind=_bounded_clean(kind, 80),
            semantic_class=_bounded_clean(semantic_class, 40),
            payload_sha256=_sha256_text(str(payload)),
            refs=tuple(_bounded_clean(ref, 120) for ref in refs)[:20],
        )


class EvidenceStore:
    """Thread-safe, atomic evidence packet store.

    Packets are never inserted into model chat history by this class. Consumers
    must ask for an explicit target rendering.
    """

    def __init__(self, path: Path = EVIDENCE_STATE_PATH):
        self.path = path
        self._lock = threading.RLock()
        self._packets: list[EvidencePacket] = []
        self._load()

    @contextmanager
    def _process_guard(self):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock_path = self.path.with_name(f".{self.path.name}.lock")
        with lock_path.open("a+b") as handle:
            try:
                os.chmod(lock_path, 0o600)
            except OSError:
                pass
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _load(self, *, replace_missing: bool = False) -> None:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            if replace_missing:
                self._packets = []
            return
        if not isinstance(payload, dict) or payload.get("schema") != EVIDENCE_SCHEMA:
            if replace_missing:
                self._packets = []
            return
        packets = payload.get("packets")
        if not isinstance(packets, list):
            if replace_missing:
                self._packets = []
            return
        recovered: list[EvidencePacket] = []
        for item in packets:
            if not isinstance(item, dict):
                continue
            try:
                recovered.append(EvidencePacket.from_dict(item))
            except (TypeError, ValueError):
                continue
        self._packets = recovered

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            os.chmod(self.path.parent, 0o700)
        except OSError:
            pass
        payload = {
            "schema": EVIDENCE_SCHEMA,
            "saved_at": _utc_now(),
            "packets": [asdict(packet) for packet in self._packets],
        }
        temp = self.path.with_name(
            f".{self.path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
        )
        try:
            temp.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            os.chmod(temp, 0o600)
            temp.replace(self.path)
        finally:
            try:
                temp.unlink()
            except FileNotFoundError:
                pass

    def add(self, packet: EvidencePacket) -> EvidencePacket:
        with self._lock:
            with self._process_guard():
                self._load(replace_missing=True)
                if not any(
                    current.packet_id == packet.packet_id
                    for current in self._packets
                ):
                    self._packets.append(packet)
                    self._save()
        return packet

    def list(self, *, newest_first: bool = True) -> list[EvidencePacket]:
        with self._lock:
            self._load()
            packets = list(self._packets)
        return list(reversed(packets)) if newest_first else packets

    def get(self, packet_id: str) -> EvidencePacket | None:
        with self._lock:
            self._load()
            return next(
                (packet for packet in self._packets if packet.packet_id == packet_id),
                None,
            )

    def attach(self, packet_id: str, target: str = "BOTH") -> EvidencePacket:
        normalized = str(target).upper()
        if normalized not in ATTACHMENT_TARGETS - {"NONE"}:
            raise ValueError("attachment target must be PILOT, WITNESS, or BOTH")
        with self._lock:
            with self._process_guard():
                self._load(replace_missing=True)
                packet = next(
                    (
                        current
                        for current in self._packets
                        if current.packet_id == packet_id
                    ),
                    None,
                )
                if packet is None:
                    raise KeyError(packet_id)
                packet.attachment = normalized
                self._save()
                return packet

    def detach(self, packet_id: str | None = None) -> int:
        changed = 0
        with self._lock:
            with self._process_guard():
                self._load(replace_missing=True)
                for packet in self._packets:
                    if packet_id is not None and packet.packet_id != packet_id:
                        continue
                    if packet.attachment != "NONE":
                        packet.attachment = "NONE"
                        changed += 1
                if changed:
                    self._save()
        return changed

    def attached_count(self) -> int:
        with self._lock:
            self._load()
            return sum(packet.attachment != "NONE" for packet in self._packets)

    def attached_packet_ids(self, target: str | None = None) -> list[str]:
        normalized = str(target).upper() if target else ""
        if normalized and normalized not in {"PILOT", "WITNESS"}:
            raise ValueError("attachment target must be PILOT or WITNESS")
        with self._lock:
            self._load()
            return [
                packet.packet_id
                for packet in self._packets
                if packet.attachment != "NONE"
                and (
                    not normalized
                    or packet.attachment in {normalized, "BOTH"}
                )
            ]

    def render_attached(self, target: str, *, max_chars: int = 9000) -> str:
        normalized = str(target).upper()
        if normalized not in {"PILOT", "WITNESS"}:
            raise ValueError("render target must be PILOT or WITNESS")
        with self._lock:
            self._load()
            packets = [
                packet
                for packet in reversed(self._packets)
                if packet.attachment in {normalized, "BOTH"}
            ]
        return render_evidence_packets(packets, max_chars=max_chars)


def evidence_packet_from_grep_lines(
    query: str,
    lines: Iterable[str],
    *,
    exclusions: Iterable[str] = (),
    errors: Iterable[str] = (),
) -> EvidencePacket:
    items: list[EvidenceItem] = []
    for raw_line in list(lines)[:40]:
        value = redact_sensitive_text(str(raw_line))[:1600]
        match = re.match(r"^(.*?):(\d+):(.*)$", value)
        if match:
            locator, line_text, excerpt = match.groups()
            line = int(line_text)
        else:
            locator, line, excerpt = "local-project-index", None, value
        items.append(
            EvidenceItem.create(
                kind="FILE_EXCERPT",
                title=Path(locator).name if locator else "project excerpt",
                locator=locator,
                line=line,
                excerpt=excerpt,
                retrieved=True,
                inspected=False,
            )
        )
    return EvidencePacket.create(
        kind="SYSTEM_GREP",
        query=query,
        items=items,
        exclusions=exclusions,
        errors=errors,
    )


def evidence_packet_from_news(
    query: str,
    results: Iterable[dict[str, Any]],
    *,
    errors: Iterable[str] = (),
) -> EvidencePacket:
    items = [
        EvidenceItem.create(
            kind="WEB_SOURCE",
            title=str(result.get("title") or "untitled source"),
            locator=str(result.get("url") or ""),
            excerpt=str(result.get("snippet") or ""),
            retrieved=True,
            inspected=False,
        )
        for result in list(results)[:20]
        if isinstance(result, dict)
    ]
    return EvidencePacket.create(
        kind="NEWS_SEARCH",
        query=query,
        items=items,
        exclusions=("web source text is untrusted input",),
        errors=errors,
    )


def render_evidence_packets(
    packets: Iterable[EvidencePacket],
    *,
    max_chars: int = 9000,
) -> str:
    sections: list[str] = []
    used = 0
    for packet in packets:
        header = "\n".join(
            [
            (
                f"PACKET {packet.packet_id} | {packet.kind} | "
                f"fetched {packet.created_at} | authority={packet.status_authority}"
            ),
            f"QUERY: {packet.query_redacted}",
            ]
        )
        if sections:
            header = "\n\n" + header
        if used + len(header) > max_chars:
            break
        chunks = [header]
        used += len(header)
        for item in packet.items:
            locator = item.locator
            if item.line:
                locator = f"{locator}:{item.line}"
            item_lines = [
                f"- [{item.kind}] {item.title}",
                f"  locator: {locator}",
                f"  retrieved: {str(item.retrieved).lower()}",
                f"  inspected: {str(item.inspected).lower()}",
                f"  excerpt_fingerprint: {item.excerpt_fingerprint}",
            ]
            if item.source_sha256:
                item_lines.append(f"  source_sha256: {item.source_sha256}")
            item_lines.append(f"  excerpt: {item.excerpt}")
            item_block = "\n" + "\n".join(item_lines)
            if used + len(item_block) > max_chars:
                break
            chunks.append(item_block)
            used += len(item_block)
        trailer_lines: list[str] = []
        if packet.exclusions:
            trailer_lines.append("EXCLUSIONS: " + "; ".join(packet.exclusions))
        if packet.errors:
            trailer_lines.append("ERRORS: " + "; ".join(packet.errors))
        if trailer_lines:
            trailer = "\n" + "\n".join(trailer_lines)
            if used + len(trailer) <= max_chars:
                chunks.append(trailer)
                used += len(trailer)
        sections.append("".join(chunks))
        if used >= max_chars:
            break
    return "".join(sections)


def requires_system_evidence(text: str) -> bool:
    """Conservative automatic Scout grep trigger for local/project questions."""
    value = " ".join(str(text).lower().split())
    if not value:
        return False
    local_subject = re.search(
        r"\b(?:my|our|this|local|system|machine|pc|filesystem|repo(?:sitory)?|"
        r"project|branch|commit|worktree|codebase|source|file|config|lab|nexus|"
        r"history|experiment|fork|implementation|script|service)\b",
        value,
    )
    retrieval_intent = re.search(
        r"\b(?:find|grep|search|locate|inspect|audit|check|trace|compare|review|"
        r"what|where|which|how|use|reuse|incorporate|implement|build|fix|debug|"
        r"history|everything)\b",
        value,
    )
    public_only = re.search(
        r"\b(?:weather|sports?|stock|crypto|headline|world\s+news)\b",
        value,
    )
    return bool(local_subject and retrieval_intent and not public_only)


def witness_ready(
    records: Iterable[ModelRecord],
    provider: str,
    model: str,
) -> bool:
    return any(
        record.provider == provider
        and record.model == model
        and record.state == "READY"
        for record in records
    )


def distinct_pilot_candidates(
    records: Iterable[ModelRecord],
    witness_provider: str,
    witness_model: str,
) -> list[ModelRecord]:
    return [
        record
        for record in records
        if (record.provider, record.model)
        != (witness_provider, witness_model)
    ]


def build_witness_review_messages(
    query: str,
    answer: str,
    evidence_context: str = "",
) -> list[dict[str, str]]:
    """Build a user-role-only, bounded post-answer WITNESS review request."""
    safe_query = _bounded_clean(query, 900)
    safe_answer = redact_sensitive_text(str(answer))[:5000]
    safe_evidence = redact_sensitive_text(str(evidence_context))[:3500]
    return [
        {
            "role": "user",
            "content": (
                "NEXUS WITNESS audit. Mechanically inspect the PILOT answer against "
                "the request and supplied evidence. Output exactly one short line "
                "(maximum 22 words) beginning CLEAR: or DISSENT:. Do not reveal "
                "hidden reasoning, answer the user, invent evidence, or authorize "
                "actions. If evidence is absent, only check scope and unsupported "
                "certainty.\n"
                f"REQUEST:\n{safe_query}\n"
                f"PILOT ANSWER:\n{safe_answer}\n"
                f"BOUNDED EVIDENCE:\n{safe_evidence or '[none supplied]'}\n"
                "/no_think"
            ),
        }
    ]
