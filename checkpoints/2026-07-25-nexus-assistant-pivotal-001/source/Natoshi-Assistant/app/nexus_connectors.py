#!/usr/bin/env python3
"""Inert connector declarations and a fail-closed fixture ingress pipeline.

This module deliberately contains no sockets, SDK clients, credential loading,
device access, subprocess execution, browser automation, or outbound effects.
It lets the cockpit describe future connectors and exercise deterministic,
in-memory quarantine transitions without implying that a live connector exists.

Layering is load-bearing:

* application protocols carry messages or workflow requests;
* bearers carry bytes and never grant application capabilities;
* source adapters turn explicitly selected local input into candidate evidence;
* the hardened gateway is an isolation boundary, not an authority;
* authority/evidence adapters can report scoped propositions but cannot promote
  them, authorize effects, or become canonical merely by being connected.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from nexus_core import redact_sensitive_text


CONNECTOR_SCHEMA = "nexus.connector-stub/v1"
INGRESS_SCHEMA = "nexus.connector-ingress/v1"
COMMONS_SCHEMA = "nexus.deterministic-commons/v1"
STATUS_AUTHORITY = "NONE"


class _TextEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class ConnectorLayer(_TextEnum):
    APPLICATION_PROTOCOL = "APPLICATION_PROTOCOL"
    BEARER = "BEARER"
    SOURCE_ADAPTER = "SOURCE_ADAPTER"
    GATEWAY = "GATEWAY"
    AUTHORITY_EVIDENCE = "AUTHORITY_EVIDENCE"


class ConnectorDirection(_TextEnum):
    INGRESS_ONLY = "INGRESS_ONLY"
    EGRESS_ONLY = "EGRESS_ONLY"
    DUPLEX = "DUPLEX"
    TRANSPORT_ONLY = "TRANSPORT_ONLY"
    CONTROL_BOUNDARY = "CONTROL_BOUNDARY"


class ConnectorState(_TextEnum):
    INERT_STUB = "INERT_STUB"


class ApprovalPolicy(_TextEnum):
    NONE = "NONE"
    ASK_ONCE = "ASK_ONCE"
    ALWAYS = "ALWAYS"
    HUMAN_ONLY = "HUMAN_ONLY"
    FORBIDDEN = "FORBIDDEN"


class RiskClass(_TextEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class CapabilityRule:
    """One future capability declaration.

    ``implemented`` means only that deterministic registry/fixture logic exists.
    No effectful capability is permitted to be implemented in this module.
    """

    capability: str
    approval: ApprovalPolicy
    risk: RiskClass
    effectful: bool
    implemented: bool = False
    requires: tuple[str, ...] = ()
    rationale: str = ""

    def __post_init__(self) -> None:
        if not self.capability or any(char.isspace() for char in self.capability):
            raise ValueError("capability IDs must be non-empty and contain no spaces")
        if self.effectful and self.implemented:
            raise ValueError("effectful connector capabilities must remain unimplemented")
        if self.effectful and self.approval is ApprovalPolicy.NONE:
            raise ValueError("effectful capabilities cannot have approval NONE")


@dataclass(frozen=True)
class CommonsPolicy:
    """Deterministic, explicit opt-in policy for future public projections."""

    participation: str = "OPT_IN"
    opted_in: bool = False
    license_id: str = ""
    allowed_artifact_kinds: tuple[str, ...] = ("SCRUBBED_DERIVATIVE",)
    deterministic_projection_only: bool = True
    include_raw: bool = False
    privacy_review_required: bool = True
    publish_approval_required: bool = True
    status_authority: str = STATUS_AUTHORITY
    schema: str = COMMONS_SCHEMA

    def __post_init__(self) -> None:
        if self.participation != "OPT_IN":
            raise ValueError("commons participation must remain explicit OPT_IN")
        if self.include_raw:
            raise ValueError("raw connector/session material cannot enter commons")
        if self.status_authority != STATUS_AUTHORITY:
            raise ValueError("commons metadata cannot carry status authority")

    def allows_public_projection(
        self,
        artifact_kind: str,
        *,
        privacy_review_ref: str = "",
        publish_approval_ref: str = "",
    ) -> bool:
        if not self.opted_in or not self.license_id.strip():
            return False
        if artifact_kind not in self.allowed_artifact_kinds:
            return False
        if self.privacy_review_required and not privacy_review_ref.strip():
            return False
        if self.publish_approval_required and not publish_approval_ref.strip():
            return False
        return self.deterministic_projection_only and not self.include_raw


@dataclass(frozen=True)
class QuarantineProfile:
    profile_id: str
    max_bytes: int
    allowed_content_types: tuple[str, ...]
    decode_mode: str
    allow_archives: bool = False
    allow_active_content: bool = False
    strip_metadata: bool = True
    prompt_fence_required: bool = True
    human_privacy_review_required: bool = True

    def __post_init__(self) -> None:
        if self.max_bytes <= 0:
            raise ValueError("quarantine max_bytes must be positive")
        if self.allow_archives or self.allow_active_content:
            raise ValueError("inert profiles cannot allow archives or active content")


TEXT_EVENT_PROFILE = QuarantineProfile(
    profile_id="text-event-v1",
    max_bytes=1_048_576,
    allowed_content_types=(
        "application/json",
        "application/x-ndjson",
        "text/plain",
    ),
    decode_mode="UTF8_OR_CANONICAL_JSON",
)

CHAT_EVENT_PROFILE = QuarantineProfile(
    profile_id="chat-event-v1",
    max_bytes=524_288,
    allowed_content_types=("application/json", "text/plain"),
    decode_mode="UTF8_OR_CANONICAL_JSON",
)

BROWSER_PROFILE = QuarantineProfile(
    profile_id="browser-capture-v1",
    max_bytes=2_097_152,
    allowed_content_types=(
        "application/json",
        "text/html",
        "text/plain",
    ),
    decode_mode="UTF8_UNTRUSTED",
)

OPAQUE_MEDIA_PROFILE = QuarantineProfile(
    profile_id="opaque-media-v1",
    max_bytes=67_108_864,
    allowed_content_types=(
        "application/octet-stream",
        "audio/ogg",
        "audio/wav",
        "image/jpeg",
        "image/png",
        "video/mp4",
    ),
    decode_mode="OPAQUE_HASH_ONLY",
)

ROOMFINAL_PROFILE = QuarantineProfile(
    profile_id="roomfinal-fixture-v1",
    max_bytes=4_194_304,
    allowed_content_types=("application/json", "application/x-ndjson"),
    decode_mode="CANONICAL_JSON_FIXTURE",
)


@dataclass(frozen=True)
class ConnectorStub:
    connector_id: str
    display_name: str
    layer: ConnectorLayer
    protocol_family: str
    direction: ConnectorDirection
    quarantine: QuarantineProfile | None
    capability_rules: tuple[CapabilityRule, ...]
    data_classes: tuple[str, ...]
    evidence_semantics: str
    non_claims: tuple[str, ...]
    bearer_bindings: tuple[str, ...] = ()
    gateway_required: bool = True
    regulatory_notes: tuple[str, ...] = ()
    commons_policy: CommonsPolicy = field(default_factory=CommonsPolicy)
    enabled: bool = False
    accepts_credentials: bool = False
    auto_start: bool = False
    background_polling: bool = False
    live_endpoints: tuple[str, ...] = ()
    implementation_state: ConnectorState = ConnectorState.INERT_STUB
    status_authority: str = STATUS_AUTHORITY
    schema: str = CONNECTOR_SCHEMA

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]{1,79}", self.connector_id):
            raise ValueError(f"invalid connector ID: {self.connector_id!r}")
        if self.enabled or self.accepts_credentials or self.auto_start:
            raise ValueError("connector stubs must be disabled and credential-free")
        if self.background_polling or self.live_endpoints:
            raise ValueError("connector stubs cannot poll or contain live endpoints")
        if self.implementation_state is not ConnectorState.INERT_STUB:
            raise ValueError("only INERT_STUB connector state is available")
        if self.status_authority != STATUS_AUTHORITY:
            raise ValueError("connectors cannot carry status authority")
        if any(rule.effectful and rule.implemented for rule in self.capability_rules):
            raise ValueError("effectful connector capabilities must remain inert")
        ids = [rule.capability for rule in self.capability_rules]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate capability in {self.connector_id}")
        if self.layer is ConnectorLayer.BEARER:
            if self.quarantine is not None:
                raise ValueError("bearers transport bytes; they do not parse payloads")
            if self.direction is not ConnectorDirection.TRANSPORT_ONLY:
                raise ValueError("bearers must use TRANSPORT_ONLY direction")
        if self.layer is ConnectorLayer.GATEWAY:
            if self.quarantine is not None:
                raise ValueError("the gateway is a boundary, not a payload parser")
            if self.direction is not ConnectorDirection.CONTROL_BOUNDARY:
                raise ValueError("gateway must use CONTROL_BOUNDARY direction")

    def capability(self, capability: str) -> CapabilityRule | None:
        return next(
            (
                rule
                for rule in self.capability_rules
                if rule.capability == capability
            ),
            None,
        )

    @property
    def implemented_capabilities(self) -> tuple[str, ...]:
        return tuple(
            rule.capability for rule in self.capability_rules if rule.implemented
        )

    def public_metadata(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["layer"] = self.layer.value
        payload["direction"] = self.direction.value
        payload["implementation_state"] = self.implementation_state.value
        for rule in payload["capability_rules"]:
            rule["approval"] = str(rule["approval"])
            rule["risk"] = str(rule["risk"])
        return payload


def _rule(
    capability: str,
    approval: ApprovalPolicy,
    risk: RiskClass,
    *,
    effectful: bool,
    implemented: bool = False,
    requires: Iterable[str] = (),
    rationale: str = "",
) -> CapabilityRule:
    return CapabilityRule(
        capability=capability,
        approval=approval,
        risk=risk,
        effectful=effectful,
        implemented=implemented,
        requires=tuple(requires),
        rationale=rationale,
    )


REGISTRY_INSPECT = _rule(
    "registry.inspect",
    ApprovalPolicy.NONE,
    RiskClass.LOW,
    effectful=False,
    implemented=True,
    rationale="Returns static, credential-free metadata only.",
)
FIXTURE_INGRESS = _rule(
    "fixture.ingress",
    ApprovalPolicy.NONE,
    RiskClass.LOW,
    effectful=False,
    implemented=True,
    rationale="Processes caller-supplied bytes in memory; performs no I/O.",
)
FIXTURE_STATUS = _rule(
    "fixture.status",
    ApprovalPolicy.NONE,
    RiskClass.LOW,
    effectful=False,
    implemented=True,
    rationale="Returns synthetic fixture state only; never probes hardware.",
)


def _chat_rules(prefix: str) -> tuple[CapabilityRule, ...]:
    return (
        REGISTRY_INSPECT,
        FIXTURE_INGRESS,
        _rule(
            f"{prefix}.connect",
            ApprovalPolicy.ALWAYS,
            RiskClass.HIGH,
            effectful=True,
        ),
        _rule(
            f"{prefix}.read",
            ApprovalPolicy.ASK_ONCE,
            RiskClass.MEDIUM,
            effectful=True,
        ),
        _rule(
            f"{prefix}.send",
            ApprovalPolicy.HUMAN_ONLY,
            RiskClass.CRITICAL,
            effectful=True,
        ),
    )


_CONNECTORS = (
    ConnectorStub(
        connector_id="nostr",
        display_name="Nostr event bridge",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="nostr-event",
        direction=ConnectorDirection.DUPLEX,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "nostr.read",
                ApprovalPolicy.ASK_ONCE,
                RiskClass.MEDIUM,
                effectful=True,
            ),
            _rule(
                "nostr.sign",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "nostr.publish",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
                requires=("nostr.sign", "online.send"),
            ),
            _rule(
                "online.send",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "PUBLIC", "PROVIDER_BOUND", "SECRET"),
        evidence_semantics=(
            "A valid event signature can support key-authorship and byte-integrity "
            "only; it does not establish truth, identity, permission, or settlement."
        ),
        non_claims=(
            "relay availability",
            "event truth",
            "operator authorization",
            "global ordering",
        ),
        bearer_bindings=("ip",),
    ),
    ConnectorStub(
        connector_id="roomfinal",
        display_name="RoomFinal evidence adapter",
        layer=ConnectorLayer.AUTHORITY_EVIDENCE,
        protocol_family="roomfinal-local-fixture",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=ROOMFINAL_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "roomfinal.import",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "roomfinal.submit",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "roomfinal.settle",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "SOURCE", "TEST", "RECEIPT"),
        evidence_semantics=(
            "A fixture may report replay, inclusion, consistency, or scoped "
            "client-final predicates. Semantic authority and global settlement "
            "remain outside the connector."
        ),
        non_claims=(
            "global consensus",
            "fair validator admission",
            "production key management",
            "canonical settlement",
        ),
        bearer_bindings=("fixture-only",),
    ),
    ConnectorStub(
        connector_id="irc",
        display_name="IRC bridge",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="irc",
        direction=ConnectorDirection.DUPLEX,
        quarantine=CHAT_EVENT_PROFILE,
        capability_rules=_chat_rules("irc"),
        data_classes=("UNTRUSTED_EXTERNAL", "PUBLIC", "PROVIDER_BOUND"),
        evidence_semantics="Nicknames and server delivery are source signals, not identity or truth.",
        non_claims=("real-world identity", "message truth", "send authorization"),
        bearer_bindings=("ip",),
    ),
    ConnectorStub(
        connector_id="discord",
        display_name="Discord app bridge",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="discord-api-events",
        direction=ConnectorDirection.DUPLEX,
        quarantine=CHAT_EVENT_PROFILE,
        capability_rules=_chat_rules("discord"),
        data_classes=("UNTRUSTED_EXTERNAL", "PROVIDER_BOUND", "SECRET"),
        evidence_semantics="Platform event provenance does not make message content trusted.",
        non_claims=("user consent", "message truth", "permission to post"),
        bearer_bindings=("ip",),
        regulatory_notes=("Official app/OAuth flows only; no user-token scraping or self-bots.",),
    ),
    ConnectorStub(
        connector_id="slack",
        display_name="Slack app bridge",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="slack-api-events",
        direction=ConnectorDirection.DUPLEX,
        quarantine=CHAT_EVENT_PROFILE,
        capability_rules=_chat_rules("slack"),
        data_classes=("UNTRUSTED_EXTERNAL", "PROVIDER_BOUND", "SECRET"),
        evidence_semantics="Webhook verification authenticates delivery metadata, not semantic truth.",
        non_claims=("workspace consent", "message truth", "permission to post"),
        bearer_bindings=("ip",),
        regulatory_notes=("Future implementation must use least-scope official app credentials.",),
    ),
    ConnectorStub(
        connector_id="winmx",
        display_name="WinMX protocol research fixture",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="winmx-legacy-research",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "winmx.peer-discovery",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "winmx.listen",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "winmx.share",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "winmx.download",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "RESEARCH_FIXTURE"),
        evidence_semantics="Only caller-supplied, offline fixture structure may be inspected.",
        non_claims=("safe peer", "safe file", "license to share", "network compatibility"),
        bearer_bindings=("fixture-only",),
        regulatory_notes=("No live peer discovery, listening, sharing, or downloads in the stub phase.",),
    ),
    ConnectorStub(
        connector_id="bittorrent",
        display_name="Private-swarm artifact research fixture",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="bittorrent-private-room-research",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=OPAQUE_MEDIA_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "bittorrent.manifest-import",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "bittorrent.private-rendezvous",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "bittorrent.chunk-receive",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "bittorrent.dht",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "bittorrent.pex",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "bittorrent.seed",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=(
            "UNTRUSTED_EXTERNAL",
            "ENCRYPTED",
            "OPAQUE",
            "RESEARCH_FIXTURE",
        ),
        evidence_semantics=(
            "A matching piece or manifest hash proves byte agreement with the "
            "selected manifest only; it does not prove authorship, safety, "
            "truth, admission, or permission to redistribute."
        ),
        non_claims=(
            "safe content",
            "publisher identity",
            "private membership",
            "malware absence",
            "license to share",
        ),
        bearer_bindings=("fixture-only",),
        regulatory_notes=(
            "No DHT, peer exchange, local discovery, public magnet, tracker, "
            "download, or seeding in the stub phase.",
        ),
    ),
    ConnectorStub(
        connector_id="mediawiki",
        display_name="Wikipedia / MediaWiki revision adapter",
        layer=ConnectorLayer.SOURCE_ADAPTER,
        protocol_family="mediawiki-revision-api",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "mediawiki.fetch-revision",
                ApprovalPolicy.ASK_ONCE,
                RiskClass.MEDIUM,
                effectful=True,
            ),
            _rule(
                "mediawiki.follow-eventstream",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "mediawiki.edit",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "mediawiki.execute-content",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "PUBLIC", "SOURCE", "ATTRIBUTION_BOUND"),
        evidence_semantics=(
            "A revision ID, parent ID, upstream hash, or patrol flag is source "
            "provenance only; it is not a publisher signature, truth guarantee, "
            "room acceptance, or permanent-history proof."
        ),
        non_claims=(
            "article truth",
            "content permanence",
            "publisher signature",
            "permission to republish",
            "safe embedded content",
        ),
        bearer_bindings=("ip",),
        regulatory_notes=(
            "Future reads must retain revision permalinks, attribution and "
            "license metadata. Editing remains forbidden in this stub.",
        ),
    ),
    ConnectorStub(
        connector_id="github",
        display_name="Staged GitHub request bridge",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="github-api-workflow",
        direction=ConnectorDirection.DUPLEX,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "github.read",
                ApprovalPolicy.ASK_ONCE,
                RiskClass.MEDIUM,
                effectful=True,
            ),
            _rule(
                "github.write",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "git.commit",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "git.push",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "github.merge",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "SOURCE", "RECEIPT", "SECRET"),
        evidence_semantics=(
            "A request/commit/check receipt proves only its recorded operation; "
            "merge or status badges do not establish semantic correctness."
        ),
        non_claims=("merge authority", "correctness", "independent review"),
        bearer_bindings=("ip",),
    ),
    ConnectorStub(
        connector_id="rss-atom",
        display_name="RSS / Atom feed adapter",
        layer=ConnectorLayer.SOURCE_ADAPTER,
        protocol_family="rss-atom",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "rss-atom.fetch",
                ApprovalPolicy.ASK_ONCE,
                RiskClass.MEDIUM,
                effectful=True,
            ),
            _rule(
                "rss-atom.subscribe",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "PUBLIC", "SOURCE"),
        evidence_semantics="Feed metadata and entries are untrusted candidate sources.",
        non_claims=("publisher identity", "article truth", "permission to republish"),
        bearer_bindings=("ip",),
    ),
    ConnectorStub(
        connector_id="email",
        display_name="Email handoff adapter",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="email-api-imap-smtp",
        direction=ConnectorDirection.DUPLEX,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "email.read",
                ApprovalPolicy.ASK_ONCE,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "email.send",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "email.attachment-open",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "PRIVATE", "SECRET", "PROVIDER_BOUND"),
        evidence_semantics="Transport headers and signatures are source signals, not message truth.",
        non_claims=("sender identity", "safe attachment", "permission to reply"),
        bearer_bindings=("ip",),
    ),
    ConnectorStub(
        connector_id="web-search",
        display_name="Public web-search source adapter",
        layer=ConnectorLayer.SOURCE_ADAPTER,
        protocol_family="search-api",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "web-search.query",
                ApprovalPolicy.ASK_ONCE,
                RiskClass.MEDIUM,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "PUBLIC", "PROVIDER_BOUND"),
        evidence_semantics="Search results are locators and excerpts requiring source inspection.",
        non_claims=("freshness", "ranking neutrality", "page truth", "citation support"),
        bearer_bindings=("ip",),
    ),
    ConnectorStub(
        connector_id="webhook",
        display_name="Explicit webhook ingress adapter",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="https-webhook",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "webhook.listen",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "webhook.reply",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "PROVIDER_BOUND", "SECRET"),
        evidence_semantics="A verified delivery signature binds bytes to a configured key only.",
        non_claims=("semantic truth", "operator approval", "safe replay"),
        bearer_bindings=("ip",),
    ),
    ConnectorStub(
        connector_id="greywire-drop",
        display_name="Greywire encrypted Drop carrier",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="nexus-greywire-drop",
        direction=ConnectorDirection.DUPLEX,
        quarantine=OPAQUE_MEDIA_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "greywire-drop.receive",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "greywire-drop.send",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "greywire-drop.decrypt",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "ENCRYPTED", "PRIVATE", "RECEIPT"),
        evidence_semantics=(
            "A signed Drop proves manifest integrity and an accepted custody "
            "transition; it does not prove plaintext truth or non-copyability."
        ),
        non_claims=("global ordering", "settlement", "plaintext non-copyability"),
        bearer_bindings=("ip", "local-file", "removable-media", "future-bearer"),
    ),
    ConnectorStub(
        connector_id="removable-media",
        display_name="Quarantine-first removable-media adapter",
        layer=ConnectorLayer.SOURCE_ADAPTER,
        protocol_family="explicit-removable-media",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=OPAQUE_MEDIA_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "removable-media.select",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "removable-media.mount",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "removable-media.execute",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "LOCAL_ONLY", "ENCRYPTED"),
        evidence_semantics="Only hashes and explicit safe derivatives may leave quarantine.",
        non_claims=("safe device", "safe filesystem", "safe file", "trusted publisher"),
        bearer_bindings=("local-device",),
    ),
    ConnectorStub(
        connector_id="codex-app-server",
        display_name="Local Codex app-server handoff",
        layer=ConnectorLayer.APPLICATION_PROTOCOL,
        protocol_family="codex-app-server",
        direction=ConnectorDirection.DUPLEX,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "codex-app-server.connect",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "codex-app-server.execute",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "codex-app-server.auto-approve",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "LOCAL_ONLY", "SOURCE", "RECEIPT"),
        evidence_semantics="Codex events and tool receipts remain candidate work evidence.",
        non_claims=("operator approval", "test success", "merge authority"),
        bearer_bindings=("private-local-ipc",),
    ),
    ConnectorStub(
        connector_id="chatgpt-handoff",
        display_name="Explicit ChatGPT browser handoff",
        layer=ConnectorLayer.SOURCE_ADAPTER,
        protocol_family="review-copy-paste",
        direction=ConnectorDirection.DUPLEX,
        quarantine=TEXT_EVENT_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "chatgpt-handoff.open",
                ApprovalPolicy.ALWAYS,
                RiskClass.MEDIUM,
                effectful=True,
            ),
            _rule(
                "chatgpt-handoff.copy",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "chatgpt-handoff.read-session",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "chatgpt-handoff.inject",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "PRIVATE", "PROVIDER_BOUND"),
        evidence_semantics="Only operator-reviewed copied text may become candidate evidence.",
        non_claims=("session access", "cookie access", "permission to submit"),
        bearer_bindings=("browser",),
    ),
    ConnectorStub(
        connector_id="browser",
        display_name="Explicit browser capture adapter",
        layer=ConnectorLayer.SOURCE_ADAPTER,
        protocol_family="browser-dom-screenshot-download",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=BROWSER_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "browser.capture",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "browser.navigate",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "browser.submit",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "PROVIDER_BOUND", "SECRET"),
        evidence_semantics="Captured DOM, pages, and downloads are untrusted source material.",
        non_claims=("page truth", "safe download", "permission to submit", "cookie access"),
        bearer_bindings=("ip",),
    ),
    ConnectorStub(
        connector_id="voice",
        display_name="Push-to-talk voice capture adapter",
        layer=ConnectorLayer.SOURCE_ADAPTER,
        protocol_family="explicit-audio-capture",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=OPAQUE_MEDIA_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "voice.capture",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "voice.always-on",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "voice.authenticate",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "LOCAL_ONLY", "BIOMETRIC_SENSITIVE"),
        evidence_semantics="Audio/transcription can be candidate source text; a voice is never approval.",
        non_claims=("speaker identity", "operator approval", "transcription correctness"),
        bearer_bindings=("local-device",),
    ),
    ConnectorStub(
        connector_id="media",
        display_name="Explicit media-file adapter",
        layer=ConnectorLayer.SOURCE_ADAPTER,
        protocol_family="selected-media-file",
        direction=ConnectorDirection.INGRESS_ONLY,
        quarantine=OPAQUE_MEDIA_PROFILE,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_INGRESS,
            _rule(
                "media.select",
                ApprovalPolicy.ALWAYS,
                RiskClass.MEDIUM,
                effectful=True,
            ),
            _rule(
                "media.decode",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "media.publish",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=("UNTRUSTED_EXTERNAL", "LOCAL_ONLY", "PROVIDER_BOUND"),
        evidence_semantics="The inert pipeline records only type, size, and hash for binary media.",
        non_claims=("safe codec", "identity", "copyright clearance", "publish permission"),
        bearer_bindings=("local-file",),
    ),
    ConnectorStub(
        connector_id="dial-up",
        display_name="Dial-up bearer",
        layer=ConnectorLayer.BEARER,
        protocol_family="dial-up-access",
        direction=ConnectorDirection.TRANSPORT_ONLY,
        quarantine=None,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_STATUS,
            _rule(
                "dial-up.connect",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "dial-up.configure",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=(),
        evidence_semantics="Bearer status can describe a link; it cannot authenticate payloads.",
        non_claims=("trusted network", "application permission", "content integrity"),
        gateway_required=True,
    ),
    ConnectorStub(
        connector_id="ham-radio",
        display_name="Ham-radio research bearer",
        layer=ConnectorLayer.BEARER,
        protocol_family="regulated-radio-bearer",
        direction=ConnectorDirection.TRANSPORT_ONLY,
        quarantine=None,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_STATUS,
            _rule(
                "ham-radio.receive",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "ham-radio.transmit",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "ham-radio.ptt",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=(),
        evidence_semantics="A radio frame is untrusted transport input, not identity or authority.",
        non_claims=("lawful transmission", "callsign authority", "private channel", "message truth"),
        regulatory_notes=(
            "Region-specific licensing, content, encryption, identification, and band rules are unresolved.",
        ),
    ),
    ConnectorStub(
        connector_id="starlink",
        display_name="Starlink access bearer",
        layer=ConnectorLayer.BEARER,
        protocol_family="commercial-satellite-access",
        direction=ConnectorDirection.TRANSPORT_ONLY,
        quarantine=None,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_STATUS,
            _rule(
                "starlink.connect",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "starlink.manage",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=(),
        evidence_semantics="Access availability says nothing about application trust or authority.",
        non_claims=("trusted route", "privacy", "application permission", "message truth"),
    ),
    ConnectorStub(
        connector_id="hardened-os-gateway",
        display_name="Hardened connector gateway boundary",
        layer=ConnectorLayer.GATEWAY,
        protocol_family="isolated-adapter-host",
        direction=ConnectorDirection.CONTROL_BOUNDARY,
        quarantine=None,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_STATUS,
            _rule(
                "gateway.spawn",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "gateway.forward",
                ApprovalPolicy.ALWAYS,
                RiskClass.HIGH,
                effectful=True,
            ),
            _rule(
                "gateway.root",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "gateway.sudo",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=(),
        evidence_semantics="Isolation status is a control observation, not semantic authority.",
        non_claims=("perfect isolation", "payload truth", "root authority", "settlement authority"),
        gateway_required=False,
    ),
    ConnectorStub(
        connector_id="tails-companion-gateway",
        display_name="Tails companion gateway research boundary",
        layer=ConnectorLayer.GATEWAY,
        protocol_family="separate-hardened-companion",
        direction=ConnectorDirection.CONTROL_BOUNDARY,
        quarantine=None,
        capability_rules=(
            REGISTRY_INSPECT,
            FIXTURE_STATUS,
            _rule(
                "tails-companion.start",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "tails-companion.forward",
                ApprovalPolicy.HUMAN_ONLY,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "tails-companion.modify-tails",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
            _rule(
                "tails-companion.sudo",
                ApprovalPolicy.FORBIDDEN,
                RiskClass.CRITICAL,
                effectful=True,
            ),
        ),
        data_classes=(),
        evidence_semantics="A companion boundary may report isolation state only.",
        non_claims=("Tails endorsement", "anonymity", "perfect isolation", "root authority"),
        gateway_required=False,
        regulatory_notes=(
            "Prefer a separate companion/gateway over modifying the Tails trust base.",
        ),
    ),
)


CONNECTOR_REGISTRY: Mapping[str, ConnectorStub] = MappingProxyType(
    {entry.connector_id: entry for entry in _CONNECTORS}
)


MUST_REMAIN_UNIMPLEMENTED = (
    "live sockets, relay subscriptions, listeners, webhooks, and background polling",
    "credential entry, token/key persistence, cookie access, and signer custody",
    "outbound send, publish, sign, upload, download, commit, push, and merge",
    "browser navigation/submission and always-on microphone/camera capture",
    "archive extraction, active-content execution, codecs, and binary auto-open",
    "modem, radio/PTT, Starlink, kernel, root, sudo, or hardware control",
    "RoomFinal settlement/consensus import and WinMX live networking",
    "automatic evidence promotion, policy mutation, or agent self-authorization",
)


def connector_stub(connector_id: str) -> ConnectorStub:
    try:
        return CONNECTOR_REGISTRY[str(connector_id)]
    except KeyError as error:
        raise KeyError(f"unknown connector stub: {connector_id}") from error


def validate_registry() -> tuple[str, ...]:
    """Return violations instead of silently accepting a less-inert registry."""

    problems: list[str] = []
    for connector_id, entry in CONNECTOR_REGISTRY.items():
        if connector_id != entry.connector_id:
            problems.append(f"{connector_id}: registry key mismatch")
        if entry.enabled or entry.accepts_credentials or entry.live_endpoints:
            problems.append(f"{connector_id}: live configuration present")
        if entry.auto_start or entry.background_polling:
            problems.append(f"{connector_id}: automatic execution present")
        for rule in entry.capability_rules:
            if rule.effectful and rule.implemented:
                problems.append(
                    f"{connector_id}: effectful capability implemented: "
                    f"{rule.capability}"
                )
    return tuple(problems)


class IngressState(_TextEnum):
    RECEIVED_UNTRUSTED = "RECEIVED_UNTRUSTED"
    LIMITS_VALIDATED = "LIMITS_VALIDATED"
    QUARANTINED = "QUARANTINED"
    SOURCE_SIGNAL_CHECKED = "SOURCE_SIGNAL_CHECKED"
    SAFE_DERIVATIVE = "SAFE_DERIVATIVE"
    POLICY_CLASSIFIED = "POLICY_CLASSIFIED"
    SCRUBBED = "SCRUBBED"
    HUMAN_ADMITTED = "HUMAN_ADMITTED"
    EVIDENCE_RECORDED = "EVIDENCE_RECORDED"
    ROUTE_ELIGIBLE = "ROUTE_ELIGIBLE"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    DEAD_LETTER = "DEAD_LETTER"


_TERMINAL_STATES = {
    IngressState.REJECTED,
    IngressState.EXPIRED,
    IngressState.DEAD_LETTER,
    IngressState.ROUTE_ELIGIBLE,
}

_NEXT_STATE = {
    IngressState.RECEIVED_UNTRUSTED: IngressState.LIMITS_VALIDATED,
    IngressState.LIMITS_VALIDATED: IngressState.QUARANTINED,
    IngressState.QUARANTINED: IngressState.SOURCE_SIGNAL_CHECKED,
    IngressState.SOURCE_SIGNAL_CHECKED: IngressState.SAFE_DERIVATIVE,
    IngressState.SAFE_DERIVATIVE: IngressState.POLICY_CLASSIFIED,
    IngressState.POLICY_CLASSIFIED: IngressState.SCRUBBED,
    IngressState.SCRUBBED: IngressState.HUMAN_ADMITTED,
    IngressState.HUMAN_ADMITTED: IngressState.EVIDENCE_RECORDED,
    IngressState.EVIDENCE_RECORDED: IngressState.ROUTE_ELIGIBLE,
}


class InvalidIngressTransition(ValueError):
    pass


@dataclass(frozen=True)
class IngressTransition:
    previous: str
    current: IngressState
    reason: str
    receipt_sha256: str
    status_authority: str = STATUS_AUTHORITY


@dataclass(frozen=True)
class IngressRecord:
    ingress_id: str
    connector_id: str
    observed_at: str
    content_type: str
    byte_length: int
    raw_sha256: str
    source_locator: str
    state: IngressState
    raw_payload: bytes = field(repr=False, compare=False)
    source_signal: str = ""
    safe_derivative: str = field(default="", repr=False)
    safe_derivative_sha256: str = ""
    data_classes: tuple[str, ...] = ()
    scrubbed_derivative: str = field(default="", repr=False)
    scrubbed_sha256: str = ""
    scrub_redactions: int = 0
    privacy_review_required: bool = True
    human_approval_ref: str = ""
    evidence_ref: str = ""
    rejection_reason: str = ""
    transitions: tuple[IngressTransition, ...] = ()
    status_authority: str = STATUS_AUTHORITY
    schema: str = INGRESS_SCHEMA

    def public_snapshot(self) -> dict[str, Any]:
        """Return metadata only; raw and derivative content are intentionally absent."""

        return {
            "schema": self.schema,
            "ingress_id": self.ingress_id,
            "connector_id": self.connector_id,
            "observed_at": self.observed_at,
            "content_type": self.content_type,
            "byte_length": self.byte_length,
            "raw_sha256": self.raw_sha256,
            "source_locator": self.source_locator,
            "state": self.state.value,
            "source_signal": self.source_signal,
            "safe_derivative_sha256": self.safe_derivative_sha256,
            "data_classes": list(self.data_classes),
            "scrubbed_sha256": self.scrubbed_sha256,
            "scrub_redactions": self.scrub_redactions,
            "privacy_review_required": self.privacy_review_required,
            "human_approval_ref": self.human_approval_ref,
            "evidence_ref": self.evidence_ref,
            "rejection_reason": self.rejection_reason,
            "status_authority": self.status_authority,
            "transitions": [
                {
                    "previous": item.previous,
                    "current": item.current.value,
                    "reason": item.reason,
                    "receipt_sha256": item.receipt_sha256,
                    "status_authority": item.status_authority,
                }
                for item in self.transitions
            ],
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_text(payload: str) -> str:
    return _sha256_bytes(payload.encode("utf-8", errors="strict"))


def _clean_locator(value: str) -> str:
    return redact_sensitive_text(" ".join(str(value).split()))[:1000]


def _receipt_digest(
    record: IngressRecord,
    previous: str,
    current: IngressState,
    reason: str,
) -> str:
    prior = (
        record.transitions[-1].receipt_sha256
        if record.transitions
        else record.raw_sha256
    )
    material = "\0".join(
        (
            record.ingress_id,
            prior,
            previous,
            current.value,
            reason,
        )
    )
    return _sha256_text(material)


def _transition(
    record: IngressRecord,
    target: IngressState,
    *,
    reason: str,
    **changes: Any,
) -> IngressRecord:
    if record.state in _TERMINAL_STATES:
        raise InvalidIngressTransition(
            f"{record.state.value} is terminal; cannot enter {target.value}"
        )
    if target not in {
        _NEXT_STATE.get(record.state),
        IngressState.REJECTED,
        IngressState.EXPIRED,
        IngressState.DEAD_LETTER,
    }:
        raise InvalidIngressTransition(
            f"illegal transition {record.state.value} -> {target.value}"
        )
    clean_reason = redact_sensitive_text(" ".join(str(reason).split()))[:500]
    receipt = IngressTransition(
        previous=record.state.value,
        current=target,
        reason=clean_reason,
        receipt_sha256=_receipt_digest(
            record,
            record.state.value,
            target,
            clean_reason,
        ),
    )
    return replace(
        record,
        state=target,
        transitions=record.transitions + (receipt,),
        **changes,
    )


def capture_fixture(
    connector_id: str,
    payload: str | bytes,
    *,
    content_type: str = "text/plain",
    source_locator: str = "caller-supplied-fixture",
    observed_at: str | None = None,
) -> IngressRecord:
    """Capture caller-supplied fixture bytes without opening any external source."""

    connector = connector_stub(connector_id)
    fixture_rule = connector.capability("fixture.ingress")
    if not fixture_rule or not fixture_rule.implemented:
        raise ValueError(f"{connector_id} does not accept payload fixtures")
    if connector.quarantine is None:
        raise ValueError(f"{connector_id} is not a payload parser")
    if not isinstance(payload, (str, bytes)):
        raise TypeError("fixture payload must be str or bytes")
    raw = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
    if len(raw) > 67_108_864:
        raise ValueError("fixture exceeds absolute in-memory safety ceiling")
    normalized_type = str(content_type).split(";", 1)[0].strip().lower()
    digest = _sha256_bytes(raw)
    locator = _clean_locator(source_locator)
    ingress_material = (
        f"{connector.connector_id}\0{normalized_type}\0{locator}\0{digest}"
    )
    ingress_id = f"ing-{_sha256_text(ingress_material)[:24]}"
    record = IngressRecord(
        ingress_id=ingress_id,
        connector_id=connector.connector_id,
        observed_at=observed_at or _utc_now(),
        content_type=normalized_type,
        byte_length=len(raw),
        raw_sha256=digest,
        source_locator=locator,
        state=IngressState.RECEIVED_UNTRUSTED,
        raw_payload=raw,
    )
    initial = IngressTransition(
        previous="NONE",
        current=IngressState.RECEIVED_UNTRUSTED,
        reason="Caller-supplied fixture captured as volatile untrusted bytes.",
        receipt_sha256=_receipt_digest(
            record,
            "NONE",
            IngressState.RECEIVED_UNTRUSTED,
            "Caller-supplied fixture captured as volatile untrusted bytes.",
        ),
    )
    return replace(record, transitions=(initial,))


def validate_limits(record: IngressRecord) -> IngressRecord:
    connector = connector_stub(record.connector_id)
    profile = connector.quarantine
    if profile is None:
        return reject_ingress(record, "Connector has no payload quarantine profile.")
    if record.byte_length > profile.max_bytes:
        return reject_ingress(
            record,
            f"Payload exceeds {profile.profile_id} byte ceiling.",
        )
    if record.content_type not in profile.allowed_content_types:
        return reject_ingress(
            record,
            f"Content type {record.content_type or '[empty]'} is not allowlisted.",
        )
    return _transition(
        record,
        IngressState.LIMITS_VALIDATED,
        reason="Declared type and byte ceiling validated.",
    )


def quarantine_ingress(record: IngressRecord) -> IngressRecord:
    return _transition(
        record,
        IngressState.QUARANTINED,
        reason="Payload isolated from routing, effects, and model context.",
    )


def check_source_signal(
    record: IngressRecord,
    *,
    source_signal: str = "UNVERIFIED_FIXTURE",
) -> IngressRecord:
    allowed = {
        "UNVERIFIED_FIXTURE",
        "DECLARED_AUTH_SIGNAL",
        "NOT_APPLICABLE",
    }
    normalized = str(source_signal).upper()
    if normalized not in allowed:
        return reject_ingress(record, "Invalid or failed source signal.")
    return _transition(
        record,
        IngressState.SOURCE_SIGNAL_CHECKED,
        reason=(
            f"Source signal labelled {normalized}; no truth or authority inferred."
        ),
        source_signal=normalized,
    )


def derive_safe_ingress(record: IngressRecord) -> IngressRecord:
    connector = connector_stub(record.connector_id)
    profile = connector.quarantine
    if profile is None:
        return reject_ingress(record, "No safe derivative profile exists.")
    try:
        if profile.decode_mode == "OPAQUE_HASH_ONLY":
            derivative = (
                "[OPAQUE MEDIA FIXTURE — NOT DECODED]\n"
                f"content_type={record.content_type}\n"
                f"bytes={record.byte_length}\n"
                f"sha256={record.raw_sha256}"
            )
        else:
            text = record.raw_payload.decode("utf-8", errors="strict")
            if record.content_type in {
                "application/json",
                "application/x-ndjson",
            }:
                if record.content_type == "application/x-ndjson":
                    values = [
                        json.loads(line)
                        for line in text.splitlines()
                        if line.strip()
                    ]
                    derivative = "\n".join(
                        json.dumps(
                            value,
                            sort_keys=True,
                            separators=(",", ":"),
                            ensure_ascii=False,
                        )
                        for value in values
                    )
                else:
                    value = json.loads(text)
                    derivative = json.dumps(
                        value,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
            else:
                derivative = text.replace("\x00", "\uFFFD")
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return reject_ingress(record, "Payload could not produce a safe derivative.")
    return _transition(
        record,
        IngressState.SAFE_DERIVATIVE,
        reason=(
            f"Produced {profile.decode_mode} derivative without executing content."
        ),
        safe_derivative=derivative,
        safe_derivative_sha256=_sha256_text(derivative),
    )


def classify_ingress(
    record: IngressRecord,
    *,
    data_classes: Iterable[str] = ("UNTRUSTED_EXTERNAL",),
) -> IngressRecord:
    connector = connector_stub(record.connector_id)
    normalized = tuple(
        dict.fromkeys(str(value).strip().upper() for value in data_classes if str(value).strip())
    )
    if "UNTRUSTED_EXTERNAL" not in normalized:
        normalized = ("UNTRUSTED_EXTERNAL",) + normalized
    allowed = set(connector.data_classes)
    if not set(normalized).issubset(allowed):
        return reject_ingress(record, "Data classification is not allowed for connector.")
    return _transition(
        record,
        IngressState.POLICY_CLASSIFIED,
        reason="Data classes attached; content remains untrusted.",
        data_classes=normalized,
    )


_EXTRA_SECRET_PATTERNS = (
    re.compile(r"(?i)\bAuthorization\s*:\s*Bearer\s+\S+"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)\b(?:mongodb|postgres(?:ql)?|mysql)://[^/\s:@]+:[^@\s/]+@"),
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.I),
)


def secret_findings(text: str) -> tuple[str, ...]:
    findings: list[str] = []
    for index, pattern in enumerate(_EXTRA_SECRET_PATTERNS, start=1):
        if pattern.search(text):
            findings.append(f"extra-secret-pattern-{index}")
    keyword = re.search(
        (
            r"(?i)(?:api[_-]?key|access[_-]?token|password|passwd|secret|"
            r"private[_-]?key)\s*[:=]\s*(?!\[REDACTED)[^\s,;]{4,}"
        ),
        text,
    )
    if keyword:
        findings.append("credential-assignment")
    return tuple(findings)


def _scrub_known_secrets(text: str) -> tuple[str, int]:
    scrubbed = redact_sensitive_text(text)
    redactions = int(scrubbed != text)
    replacements = (
        (
            re.compile(r"(?i)(\bAuthorization\s*:\s*Bearer\s+)\S+"),
            r"\1[REDACTED]",
        ),
        (
            re.compile(r"(?i)(\bBearer\s+)[A-Za-z0-9._~+/=-]{12,}"),
            r"\1[REDACTED]",
        ),
        (
            re.compile(
                r"(?i)(\b(?:mongodb|postgres(?:ql)?|mysql)://[^/\s:@]+:)"
                r"[^@\s/]+(@)"
            ),
            r"\1[REDACTED]\2",
        ),
    )
    for pattern, replacement in replacements:
        scrubbed, count = pattern.subn(replacement, scrubbed)
        redactions += count
    return scrubbed, redactions


def scrub_known_secrets(text: str) -> tuple[str, int]:
    """Return a deterministic known-secret scrub without granting publish safety."""

    return _scrub_known_secrets(str(text))


def scrub_ingress(record: IngressRecord) -> IngressRecord:
    scrubbed, count = scrub_known_secrets(record.safe_derivative)
    residual = secret_findings(scrubbed)
    if residual:
        return reject_ingress(
            record,
            "Secret scrub failed closed: " + ", ".join(residual),
        )
    return _transition(
        record,
        IngressState.SCRUBBED,
        reason=(
            "Known secret patterns scrubbed; human privacy review still required."
        ),
        scrubbed_derivative=scrubbed,
        scrubbed_sha256=_sha256_text(scrubbed),
        scrub_redactions=count,
        privacy_review_required=True,
    )


def admit_ingress(
    record: IngressRecord,
    *,
    approval_ref: str,
    expected_scrubbed_sha256: str,
) -> IngressRecord:
    clean_approval = _clean_locator(approval_ref)
    if not clean_approval:
        raise InvalidIngressTransition("human admission requires an approval reference")
    if expected_scrubbed_sha256 != record.scrubbed_sha256:
        raise InvalidIngressTransition("stale or mismatched scrubbed derivative")
    return _transition(
        record,
        IngressState.HUMAN_ADMITTED,
        reason="Operator admitted the exact scrubbed derivative.",
        human_approval_ref=clean_approval,
    )


def record_ingress_evidence(
    record: IngressRecord,
    *,
    evidence_ref: str,
) -> IngressRecord:
    clean_ref = _clean_locator(evidence_ref)
    if not clean_ref:
        raise InvalidIngressTransition("evidence recording requires an exact reference")
    return _transition(
        record,
        IngressState.EVIDENCE_RECORDED,
        reason="Scrubbed derivative bound to a status-authority NONE evidence record.",
        evidence_ref=clean_ref,
    )


def make_ingress_route_eligible(record: IngressRecord) -> IngressRecord:
    if not record.human_approval_ref or not record.evidence_ref:
        raise InvalidIngressTransition(
            "route eligibility requires admission and evidence references"
        )
    return _transition(
        record,
        IngressState.ROUTE_ELIGIBLE,
        reason="Candidate may be selected by a bounded route; no authority granted.",
    )


def reject_ingress(record: IngressRecord, reason: str) -> IngressRecord:
    return _transition(
        record,
        IngressState.REJECTED,
        reason=reason,
        rejection_reason=redact_sensitive_text(" ".join(str(reason).split()))[:500],
        raw_payload=b"",
        safe_derivative="",
        scrubbed_derivative="",
    )


def prepare_fixture_ingress(
    connector_id: str,
    payload: str | bytes,
    *,
    content_type: str = "text/plain",
    source_locator: str = "caller-supplied-fixture",
    data_classes: Iterable[str] = ("UNTRUSTED_EXTERNAL",),
    observed_at: str | None = None,
) -> IngressRecord:
    """Run deterministic, in-memory preparation and stop before human admission."""

    record = capture_fixture(
        connector_id,
        payload,
        content_type=content_type,
        source_locator=source_locator,
        observed_at=observed_at,
    )
    steps = (
        validate_limits,
        quarantine_ingress,
        check_source_signal,
        derive_safe_ingress,
    )
    for step in steps:
        record = step(record)
        if record.state in _TERMINAL_STATES:
            return record
    record = classify_ingress(record, data_classes=data_classes)
    if record.state in _TERMINAL_STATES:
        return record
    return scrub_ingress(record)


def render_ingress_for_route(record: IngressRecord) -> str:
    """Render only an admitted evidence derivative, never volatile raw bytes."""

    if record.state is not IngressState.ROUTE_ELIGIBLE:
        raise InvalidIngressTransition("ingress is not route eligible")
    return json.dumps(
        {
            "schema": "nexus.untrusted-route-context/v1",
            "ingress_id": record.ingress_id,
            "connector_id": record.connector_id,
            "semantic_class": "SOURCE",
            "evidence_class": "DRAFT",
            "status_authority": STATUS_AUTHORITY,
            "content_label": "UNTRUSTED_SCRUBBED_DERIVATIVE",
            "content_sha256": record.scrubbed_sha256,
            "evidence_ref": record.evidence_ref,
            "content": record.scrubbed_derivative,
            "non_claims": list(connector_stub(record.connector_id).non_claims),
        },
        sort_keys=True,
        ensure_ascii=False,
    )


if validate_registry():  # pragma: no cover - import-time construction guard.
    raise RuntimeError("invalid inert connector registry: " + "; ".join(validate_registry()))
