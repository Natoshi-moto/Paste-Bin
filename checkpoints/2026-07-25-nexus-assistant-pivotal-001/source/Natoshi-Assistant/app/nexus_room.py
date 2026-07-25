#!/usr/bin/env python3
"""Cryptographic room spine for the NEXUS human/agent workspace.

This module deliberately separates three things that are easy to blur:

* confidential transport: ChaCha20-Poly1305 encrypted event payloads;
* shared ordered state: one deterministic reducer and one hash-linked head;
* evidence: Ed25519 event/checkpoint/observer signatures.

An observer receipt proves that a named observer saw a particular envelope.  It
does not prove that the payload was true, legally final, globally available, or
accepted by every possible observer.  This is the RoomFinal boundary.

The implementation is informed by the NEXUS Wallet v4 prototype whose archive
SHA-256 is 43ef6cbdb1208bd72c4a549c171c6b3ed10850d11f86209e244e83933a95c83e
and whose HTML member SHA-256 is
96311ae3c08e76ee9a0f633ff34d57e5acb4b06af3f8e7d7f600d670f0990ab2.
It does not execute or import code from that archive.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


ROOM_EVENT_SCHEMA = "nexus.room.event/v1"
ROOM_RECEIPT_SCHEMA = "nexus.room.observer-receipt/v1"
ROOM_CHECKPOINT_SCHEMA = "nexus.room.checkpoint/v1"
ROOM_REDUCER_VERSION = "nexus.room.reducer/v1"
ZERO_HASH = "0" * 64
MAX_CIPHERTEXT_BYTES = 1_048_576

EVENT_DOMAIN = b"NEXUS_ROOM_EVENT_V1\x00"
EVENT_SIGNATURE_DOMAIN = b"NEXUS_ROOM_EVENT_SIGNATURE_V1\x00"
STATE_DOMAIN = b"NEXUS_ROOM_STATE_V1\x00"
POLICY_DOMAIN = b"NEXUS_ROOM_POLICY_V1\x00"
ACCUMULATOR_DOMAIN = b"NEXUS_ROOM_ACCUMULATOR_V1\x00"
RECEIPT_DOMAIN = b"NEXUS_ROOM_OBSERVER_RECEIPT_V1\x00"
CHECKPOINT_DOMAIN = b"NEXUS_ROOM_CHECKPOINT_V1\x00"

ROOMFINAL_BOUNDARY = (
    "Policy-scoped evidence over trusted ordered room state; not permissionless "
    "consensus, legal settlement, universal truth, or universal finality."
)


class RoomProtocolError(ValueError):
    """Raised when an event cannot be deterministically admitted."""


class RoomCryptoError(RoomProtocolError):
    """Raised when envelope integrity, authenticity, or decryption fails."""


def _b64u(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64u_decode(value: str) -> bytes:
    if not isinstance(value, str):
        raise RoomProtocolError("base64url value must be a string")
    padding = "=" * ((4 - len(value) % 4) % 4)
    try:
        return base64.b64decode(
            value + padding,
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, TypeError) as error:
        raise RoomProtocolError("invalid base64url value") from error


def _validate_canonical_value(value: Any, *, depth: int = 0) -> None:
    if depth > 64:
        raise RoomProtocolError("canonical value exceeds maximum nesting depth")
    if value is None or isinstance(value, (bool, str)):
        if isinstance(value, str):
            try:
                value.encode("utf-8", errors="strict")
            except UnicodeEncodeError as error:
                raise RoomProtocolError("strings must be valid UTF-8") from error
        return
    if isinstance(value, int) and not isinstance(value, bool):
        if value < -(2**63) or value > (2**63 - 1):
            raise RoomProtocolError("integer is outside signed 64-bit range")
        return
    if isinstance(value, float):
        raise RoomProtocolError(
            "floating-point values are forbidden; use integer minor units"
        )
    if isinstance(value, list):
        for item in value:
            _validate_canonical_value(item, depth=depth + 1)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise RoomProtocolError("canonical object keys must be strings")
            _validate_canonical_value(key, depth=depth + 1)
            _validate_canonical_value(item, depth=depth + 1)
        return
    raise RoomProtocolError(
        f"unsupported canonical value type: {type(value).__name__}"
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return the exact UTF-8 bytes used by hashes and signatures."""

    _validate_canonical_value(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8", errors="strict")


def _domain_hash(domain: bytes, value: bytes) -> str:
    return hashlib.sha256(domain + value).hexdigest()


def _public_key_bytes(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _public_key_from_b64(value: str) -> Ed25519PublicKey:
    raw = _b64u_decode(value)
    if len(raw) != 32:
        raise RoomProtocolError("Ed25519 public key must be 32 bytes")
    try:
        return Ed25519PublicKey.from_public_bytes(raw)
    except ValueError as error:
        raise RoomProtocolError("invalid Ed25519 public key") from error


@dataclass(frozen=True)
class RoomIdentity:
    """An in-memory Ed25519 identity.

    The private key is intentionally never serialised by this module.  A real
    deployment should keep it in an OS keyring, hardware token, or isolated
    signing broker rather than browser ``localStorage``.
    """

    member_id: str
    public_key_b64: str
    _private_key: Ed25519PrivateKey = field(repr=False, compare=False)

    @classmethod
    def generate(cls) -> "RoomIdentity":
        private_key = Ed25519PrivateKey.generate()
        public_raw = _public_key_bytes(private_key.public_key())
        member_id = _domain_hash(b"NEXUS_ROOM_MEMBER_V1\x00", public_raw)[:32]
        return cls(member_id, _b64u(public_raw), private_key)

    def sign(self, domain: bytes, payload: bytes) -> str:
        return _b64u(self._private_key.sign(domain + payload))


@dataclass(frozen=True)
class RoomEpochKey:
    """A 256-bit symmetric key for one room epoch."""

    epoch: int
    _key: bytes = field(repr=False, compare=False)

    @classmethod
    def generate(cls, epoch: int = 1) -> "RoomEpochKey":
        if epoch < 1:
            raise RoomProtocolError("room epoch must be positive")
        return cls(epoch=epoch, _key=os.urandom(32))

    @classmethod
    def from_bytes(cls, key: bytes, *, epoch: int) -> "RoomEpochKey":
        if not isinstance(key, bytes) or len(key) != 32:
            raise RoomProtocolError("room epoch key must be exactly 32 bytes")
        if epoch < 1:
            raise RoomProtocolError("room epoch must be positive")
        return cls(epoch=epoch, _key=bytes(key))


@dataclass(frozen=True)
class DeterministicCommonsPolicy:
    """Opt-in, equal-rule scheduling for autonomous room participants.

    The political metaphor is not a security primitive.  The enforceable
    properties are explicit: all active members are sorted by stable ID, task
    assignment is round-robin, per-member concurrency is bounded, and no model
    receives an implicit administrator capability.
    """

    active_members: tuple[str, ...]
    assignment: str = "ROUND_ROBIN"
    max_active_tasks_per_member: int = 1
    hidden_admins: bool = False
    human_micromanagement_required: bool = False
    membership_mode: str = "OPT_IN_EPOCH_BOUND"
    policy_version: int = 1

    @classmethod
    def create(
        cls,
        members: Iterable[str],
        *,
        max_active_tasks_per_member: int = 1,
    ) -> "DeterministicCommonsPolicy":
        clean = tuple(sorted({str(item) for item in members if str(item)}))
        if not clean:
            raise RoomProtocolError("a room requires at least one active member")
        if max_active_tasks_per_member < 1:
            raise RoomProtocolError("task capacity must be positive")
        return cls(
            active_members=clean,
            max_active_tasks_per_member=max_active_tasks_per_member,
        )

    def payload(self) -> dict[str, Any]:
        return {
            "active_members": list(self.active_members),
            "assignment": self.assignment,
            "max_active_tasks_per_member": self.max_active_tasks_per_member,
            "hidden_admins": self.hidden_admins,
            "human_micromanagement_required": self.human_micromanagement_required,
            "membership_mode": self.membership_mode,
            "policy_version": self.policy_version,
        }

    @property
    def policy_sha256(self) -> str:
        return _domain_hash(POLICY_DOMAIN, canonical_json_bytes(self.payload()))

    def validate(self) -> None:
        if self.assignment != "ROUND_ROBIN":
            raise RoomProtocolError("only deterministic ROUND_ROBIN is supported")
        if self.hidden_admins:
            raise RoomProtocolError("hidden administrators are forbidden")
        if self.membership_mode != "OPT_IN_EPOCH_BOUND":
            raise RoomProtocolError("room membership must be opt-in and epoch-bound")
        if tuple(sorted(set(self.active_members))) != self.active_members:
            raise RoomProtocolError("active member IDs must be unique and sorted")


@dataclass
class RoomState:
    """Deterministic logical state shared by every validating room member."""

    room_id: str
    policy_sha256: str
    sequence: int = 0
    head_event_id: str = ZERO_HASH
    accumulator_root: str = ZERO_HASH
    allocation_cursor: int = 0
    transcript_count: int = 0
    tasks: dict[str, dict[str, Any]] = field(default_factory=dict)

    def logical_payload(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "policy_sha256": self.policy_sha256,
            "allocation_cursor": self.allocation_cursor,
            "transcript_count": self.transcript_count,
            "tasks": deepcopy(self.tasks),
        }

    @property
    def state_root(self) -> str:
        return _domain_hash(STATE_DOMAIN, canonical_json_bytes(self.logical_payload()))

    def clone(self) -> "RoomState":
        return RoomState(
            room_id=self.room_id,
            policy_sha256=self.policy_sha256,
            sequence=self.sequence,
            head_event_id=self.head_event_id,
            accumulator_root=self.accumulator_root,
            allocation_cursor=self.allocation_cursor,
            transcript_count=self.transcript_count,
            tasks=deepcopy(self.tasks),
        )


def _active_task_counts(state: RoomState) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task in state.tasks.values():
        if task.get("status") != "ACTIVE":
            continue
        member_id = str(task.get("assigned_to") or "")
        counts[member_id] = counts.get(member_id, 0) + 1
    return counts


def _next_assignee(
    state: RoomState,
    policy: DeterministicCommonsPolicy,
) -> str | None:
    counts = _active_task_counts(state)
    size = len(policy.active_members)
    for offset in range(size):
        index = (state.allocation_cursor + offset) % size
        member_id = policy.active_members[index]
        if counts.get(member_id, 0) < policy.max_active_tasks_per_member:
            state.allocation_cursor = (index + 1) % size
            return member_id
    return None


def apply_room_payload(
    state: RoomState,
    *,
    sender_id: str,
    payload: dict[str, Any],
    policy: DeterministicCommonsPolicy,
) -> None:
    """Apply one decrypted payload or fail without partially mutating state."""

    policy.validate()
    _validate_canonical_value(payload)
    if state.policy_sha256 != policy.policy_sha256:
        raise RoomProtocolError("state policy does not match the room epoch")
    if sender_id not in policy.active_members:
        raise RoomProtocolError("sender is not an active room member")

    kind = payload.get("kind")
    body = payload.get("body")
    if not isinstance(kind, str) or not isinstance(body, dict):
        raise RoomProtocolError("payload requires string kind and object body")

    if kind in {"MESSAGE", "CLAIM", "EVIDENCE_NOTE"}:
        text = body.get("text")
        if not isinstance(text, str) or not text.strip():
            raise RoomProtocolError(f"{kind} requires non-empty text")
        state.transcript_count += 1
        return

    if kind == "TASK_OFFER":
        task_id = body.get("task_id")
        summary = body.get("summary")
        if not isinstance(task_id, str) or not task_id:
            raise RoomProtocolError("TASK_OFFER requires task_id")
        if not isinstance(summary, str) or not summary.strip():
            raise RoomProtocolError("TASK_OFFER requires summary")
        if task_id in state.tasks:
            raise RoomProtocolError("task_id already exists")
        assignee = _next_assignee(state, policy)
        state.tasks[task_id] = {
            "task_id": task_id,
            "summary": summary,
            "offered_by": sender_id,
            "assigned_to": assignee,
            "status": "ACTIVE" if assignee else "QUEUED",
            "result_sha256": "",
        }
        return

    if kind == "TASK_RESULT":
        task_id = body.get("task_id")
        result_sha256 = body.get("result_sha256")
        task = state.tasks.get(str(task_id))
        if task is None:
            raise RoomProtocolError("TASK_RESULT references an unknown task")
        if task.get("status") != "ACTIVE":
            raise RoomProtocolError("TASK_RESULT requires an active task")
        if task.get("assigned_to") != sender_id:
            raise RoomProtocolError("only the assigned member may submit a result")
        if (
            not isinstance(result_sha256, str)
            or len(result_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in result_sha256)
        ):
            raise RoomProtocolError("TASK_RESULT requires a lowercase SHA-256")
        task["status"] = "COMPLETE"
        task["result_sha256"] = result_sha256
        return

    raise RoomProtocolError(f"unsupported room payload kind: {kind}")


@dataclass(frozen=True)
class RoomEvent:
    schema: str
    room_id: str
    sequence: int
    prev_event_id: str
    epoch: int
    sender_id: str
    sender_public_key: str
    message_class: str
    policy_sha256: str
    reducer_version: str
    pre_state_root: str
    post_state_root: str
    nonce: str
    ciphertext_sha256: str
    event_id: str
    signature: str
    ciphertext: str = field(repr=False)

    def aad_payload(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "room_id": self.room_id,
            "sequence": self.sequence,
            "prev_event_id": self.prev_event_id,
            "epoch": self.epoch,
            "sender_id": self.sender_id,
            "sender_public_key": self.sender_public_key,
            "message_class": self.message_class,
            "policy_sha256": self.policy_sha256,
            "reducer_version": self.reducer_version,
            "pre_state_root": self.pre_state_root,
            "post_state_root": self.post_state_root,
        }

    def core_payload(self) -> dict[str, Any]:
        return {
            **self.aad_payload(),
            "nonce": self.nonce,
            "ciphertext_sha256": self.ciphertext_sha256,
        }

    def lightweight_header(self) -> dict[str, Any]:
        """Return the observer-safe header without ciphertext or plaintext."""

        return {
            **self.core_payload(),
            "event_id": self.event_id,
            "signature": self.signature,
        }


def _event_id(core_payload: dict[str, Any]) -> str:
    return _domain_hash(EVENT_DOMAIN, canonical_json_bytes(core_payload))


def _verify_event_signature(event: RoomEvent) -> None:
    public_key = _public_key_from_b64(event.sender_public_key)
    expected_member = _domain_hash(
        b"NEXUS_ROOM_MEMBER_V1\x00",
        _b64u_decode(event.sender_public_key),
    )[:32]
    if expected_member != event.sender_id:
        raise RoomCryptoError("sender ID is not bound to the public key")
    try:
        public_key.verify(
            _b64u_decode(event.signature),
            EVENT_SIGNATURE_DOMAIN + bytes.fromhex(event.event_id),
        )
    except (InvalidSignature, ValueError) as error:
        raise RoomCryptoError("event signature is invalid") from error


def validate_room_event_envelope(event: RoomEvent) -> None:
    """Validate an encrypted event without possessing the room epoch key.

    This is the observer/storage boundary: it proves canonical envelope
    integrity and the sender signature, but it cannot prove plaintext meaning,
    reducer validity, room membership, or acceptance by a current room head.
    """

    if event.schema != ROOM_EVENT_SCHEMA:
        raise RoomProtocolError("unsupported room event schema")
    if not event.room_id or len(event.room_id) > 200:
        raise RoomProtocolError("room_id must contain 1..200 characters")
    if event.sequence < 1:
        raise RoomProtocolError("event sequence must be positive")
    if event.epoch < 1:
        raise RoomProtocolError("event epoch must be positive")
    if event.reducer_version != ROOM_REDUCER_VERSION:
        raise RoomProtocolError("unsupported room reducer version")
    if _event_id(event.core_payload()) != event.event_id:
        raise RoomCryptoError("event ID does not match canonical header bytes")
    _verify_event_signature(event)

    nonce = _b64u_decode(event.nonce)
    ciphertext = _b64u_decode(event.ciphertext)
    if len(nonce) != 12:
        raise RoomCryptoError("ChaCha20-Poly1305 nonce must be 12 bytes")
    if len(ciphertext) > MAX_CIPHERTEXT_BYTES + 16:
        raise RoomProtocolError("ciphertext exceeds maximum size")
    if hashlib.sha256(ciphertext).hexdigest() != event.ciphertext_sha256:
        raise RoomCryptoError("ciphertext hash does not match the header")


def _accumulate(previous_root: str, event_id: str) -> str:
    try:
        payload = bytes.fromhex(previous_root) + bytes.fromhex(event_id)
    except ValueError as error:
        raise RoomProtocolError("accumulator inputs must be SHA-256 values") from error
    return _domain_hash(ACCUMULATOR_DOMAIN, payload)


class RoomEngine:
    """Create and ingest one strictly ordered encrypted room transcript."""

    def __init__(
        self,
        *,
        room_id: str,
        policy: DeterministicCommonsPolicy,
        epoch_key: RoomEpochKey,
    ):
        if not room_id or len(room_id) > 200:
            raise RoomProtocolError("room_id must contain 1..200 characters")
        policy.validate()
        self.room_id = room_id
        self.policy = policy
        self.epoch_key = epoch_key
        self.state = RoomState(
            room_id=room_id,
            policy_sha256=policy.policy_sha256,
        )

    def create_event(
        self,
        *,
        identity: RoomIdentity,
        kind: str,
        body: dict[str, Any],
    ) -> RoomEvent:
        if identity.member_id not in self.policy.active_members:
            raise RoomProtocolError("identity is not an active room member")
        payload = {"kind": kind, "body": deepcopy(body)}
        plaintext = canonical_json_bytes(payload)
        if len(plaintext) > MAX_CIPHERTEXT_BYTES:
            raise RoomProtocolError("room payload exceeds maximum size")

        predicted = self.state.clone()
        apply_room_payload(
            predicted,
            sender_id=identity.member_id,
            payload=payload,
            policy=self.policy,
        )
        sequence = self.state.sequence + 1
        aad_payload = {
            "schema": ROOM_EVENT_SCHEMA,
            "room_id": self.room_id,
            "sequence": sequence,
            "prev_event_id": self.state.head_event_id,
            "epoch": self.epoch_key.epoch,
            "sender_id": identity.member_id,
            "sender_public_key": identity.public_key_b64,
            "message_class": kind,
            "policy_sha256": self.policy.policy_sha256,
            "reducer_version": ROOM_REDUCER_VERSION,
            "pre_state_root": self.state.state_root,
            "post_state_root": predicted.state_root,
        }
        aad = canonical_json_bytes(aad_payload)
        nonce = os.urandom(12)
        ciphertext = ChaCha20Poly1305(self.epoch_key._key).encrypt(
            nonce,
            plaintext,
            aad,
        )
        ciphertext_sha256 = hashlib.sha256(ciphertext).hexdigest()
        core_payload = {
            **aad_payload,
            "nonce": _b64u(nonce),
            "ciphertext_sha256": ciphertext_sha256,
        }
        event_id = _event_id(core_payload)
        signature = identity.sign(
            EVENT_SIGNATURE_DOMAIN,
            bytes.fromhex(event_id),
        )
        event = RoomEvent(
            **core_payload,
            event_id=event_id,
            signature=signature,
            ciphertext=_b64u(ciphertext),
        )
        self._commit_state(predicted, event)
        return event

    def ingest_event(self, event: RoomEvent) -> dict[str, Any]:
        validate_room_event_envelope(event)
        if event.room_id != self.room_id:
            raise RoomProtocolError("event belongs to another room")
        if event.epoch != self.epoch_key.epoch:
            raise RoomProtocolError("event belongs to another key epoch")
        if event.policy_sha256 != self.policy.policy_sha256:
            raise RoomProtocolError("event policy does not match this epoch")
        if event.sequence != self.state.sequence + 1:
            raise RoomProtocolError("event sequence is not the next room slot")
        if event.prev_event_id != self.state.head_event_id:
            raise RoomProtocolError("event does not extend the current room head")
        if event.pre_state_root != self.state.state_root:
            raise RoomProtocolError("event pre-state root does not match")
        if event.sender_id not in self.policy.active_members:
            raise RoomProtocolError("sender is not active in this room epoch")
        nonce = _b64u_decode(event.nonce)
        ciphertext = _b64u_decode(event.ciphertext)
        try:
            plaintext = ChaCha20Poly1305(self.epoch_key._key).decrypt(
                nonce,
                ciphertext,
                canonical_json_bytes(event.aad_payload()),
            )
        except InvalidTag as error:
            raise RoomCryptoError("ciphertext authentication failed") from error
        try:
            payload = json.loads(plaintext.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RoomProtocolError("decrypted payload is not canonical JSON") from error
        if canonical_json_bytes(payload) != plaintext:
            raise RoomProtocolError("decrypted payload bytes are not canonical")
        if payload.get("kind") != event.message_class:
            raise RoomProtocolError("encrypted kind does not match header class")

        predicted = self.state.clone()
        apply_room_payload(
            predicted,
            sender_id=event.sender_id,
            payload=payload,
            policy=self.policy,
        )
        if predicted.state_root != event.post_state_root:
            raise RoomProtocolError("event post-state root does not replay")
        self._commit_state(predicted, event)
        return payload

    def _commit_state(self, predicted: RoomState, event: RoomEvent) -> None:
        predicted.sequence = event.sequence
        predicted.head_event_id = event.event_id
        predicted.accumulator_root = _accumulate(
            self.state.accumulator_root,
            event.event_id,
        )
        self.state = predicted

    def checkpoint(self, *, sequencer: RoomIdentity) -> "RoomCheckpoint":
        if sequencer.member_id not in self.policy.active_members:
            raise RoomProtocolError("checkpoint signer is not an active member")
        return RoomCheckpoint.create(
            room_id=self.room_id,
            epoch=self.epoch_key.epoch,
            sequence=self.state.sequence,
            head_event_id=self.state.head_event_id,
            state_root=self.state.state_root,
            accumulator_root=self.state.accumulator_root,
            policy_sha256=self.policy.policy_sha256,
            signer=sequencer,
        )


@dataclass(frozen=True)
class ObserverReceipt:
    schema: str
    room_id: str
    sequence: int
    event_id: str
    observer_id: str
    observer_public_key: str
    previous_receipt_id: str
    ciphertext_retained: bool
    evidence_scope: str
    status_authority: str
    receipt_id: str
    signature: str

    @classmethod
    def create(
        cls,
        *,
        event: RoomEvent,
        observer: RoomIdentity,
        previous_receipt_id: str = ZERO_HASH,
        ciphertext_retained: bool = False,
    ) -> "ObserverReceipt":
        core = {
            "schema": ROOM_RECEIPT_SCHEMA,
            "room_id": event.room_id,
            "sequence": event.sequence,
            "event_id": event.event_id,
            "observer_id": observer.member_id,
            "observer_public_key": observer.public_key_b64,
            "previous_receipt_id": previous_receipt_id,
            "ciphertext_retained": bool(ciphertext_retained),
            "evidence_scope": "OBSERVED_ENVELOPE",
            "status_authority": "NONE",
        }
        receipt_id = _domain_hash(RECEIPT_DOMAIN, canonical_json_bytes(core))
        signature = observer.sign(RECEIPT_DOMAIN, bytes.fromhex(receipt_id))
        return cls(**core, receipt_id=receipt_id, signature=signature)

    def core_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("receipt_id")
        payload.pop("signature")
        return payload

    def verify(self) -> bool:
        if self.status_authority != "NONE":
            return False
        if self.evidence_scope != "OBSERVED_ENVELOPE":
            return False
        expected_id = _domain_hash(
            RECEIPT_DOMAIN,
            canonical_json_bytes(self.core_payload()),
        )
        if expected_id != self.receipt_id:
            return False
        try:
            public_key = _public_key_from_b64(self.observer_public_key)
            expected_observer = _domain_hash(
                b"NEXUS_ROOM_MEMBER_V1\x00",
                _b64u_decode(self.observer_public_key),
            )[:32]
            if expected_observer != self.observer_id:
                return False
            public_key.verify(
                _b64u_decode(self.signature),
                RECEIPT_DOMAIN + bytes.fromhex(self.receipt_id),
            )
        except (InvalidSignature, RoomProtocolError, ValueError):
            return False
        return True


@dataclass(frozen=True)
class RoomCheckpoint:
    schema: str
    room_id: str
    epoch: int
    sequence: int
    head_event_id: str
    state_root: str
    accumulator_root: str
    policy_sha256: str
    reducer_version: str
    signer_id: str
    signer_public_key: str
    reliance_scope: str
    checkpoint_id: str
    signature: str

    @classmethod
    def create(
        cls,
        *,
        room_id: str,
        epoch: int,
        sequence: int,
        head_event_id: str,
        state_root: str,
        accumulator_root: str,
        policy_sha256: str,
        signer: RoomIdentity,
    ) -> "RoomCheckpoint":
        core = {
            "schema": ROOM_CHECKPOINT_SCHEMA,
            "room_id": room_id,
            "epoch": epoch,
            "sequence": sequence,
            "head_event_id": head_event_id,
            "state_root": state_root,
            "accumulator_root": accumulator_root,
            "policy_sha256": policy_sha256,
            "reducer_version": ROOM_REDUCER_VERSION,
            "signer_id": signer.member_id,
            "signer_public_key": signer.public_key_b64,
            "reliance_scope": "ORDERED_ROOM_STATE_ONLY",
        }
        checkpoint_id = _domain_hash(
            CHECKPOINT_DOMAIN,
            canonical_json_bytes(core),
        )
        signature = signer.sign(CHECKPOINT_DOMAIN, bytes.fromhex(checkpoint_id))
        return cls(**core, checkpoint_id=checkpoint_id, signature=signature)

    def core_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("checkpoint_id")
        payload.pop("signature")
        return payload

    def verify(
        self,
        *,
        expected_policy_sha256: str,
        allowed_signers: Iterable[str],
    ) -> bool:
        if self.reliance_scope != "ORDERED_ROOM_STATE_ONLY":
            return False
        if self.policy_sha256 != expected_policy_sha256:
            return False
        if self.reducer_version != ROOM_REDUCER_VERSION:
            return False
        if self.signer_id not in set(allowed_signers):
            return False
        expected = _domain_hash(
            CHECKPOINT_DOMAIN,
            canonical_json_bytes(self.core_payload()),
        )
        if expected != self.checkpoint_id:
            return False
        try:
            public_key = _public_key_from_b64(self.signer_public_key)
            expected_signer = _domain_hash(
                b"NEXUS_ROOM_MEMBER_V1\x00",
                _b64u_decode(self.signer_public_key),
            )[:32]
            if expected_signer != self.signer_id:
                return False
            public_key.verify(
                _b64u_decode(self.signature),
                CHECKPOINT_DOMAIN + bytes.fromhex(self.checkpoint_id),
            )
        except (InvalidSignature, RoomProtocolError, ValueError):
            return False
        return True


def architecture_metaphor_map() -> dict[str, str]:
    """Stable UX/architecture vocabulary requested by the operator."""

    return {
        "lightbulb": "one bounded idea, task, or claim becoming inspectable",
        "circuit": "typed routes and capability-gated transformations",
        "fungus": "resilient distributed substrate with no privileged model node",
        "spores": "small content-addressed work packets that may fork and rejoin",
        "railway": "strict ordered stages, switch points, receipts, and stop signals",
        "space": "large context outside the cockpit, addressed rather than injected",
        "brain": "the room-level reducer and evidence graph, never one model",
        "neurons": "human or agent members emitting signed, bounded events",
    }
