#!/usr/bin/env python3
"""Encrypted, append-only local archive for opt-in LOOM chat records.

The archive preserves the exact caller-supplied bytes while keeping them
encrypted at rest with ChaCha20-Poly1305. Records are canonically encoded,
hash-linked, size-bounded, file-locked, fsynced, and permission-restricted.

This is local integrity/confidentiality evidence for the holder of the key. It
is not a public signature, proof of truth, proof that plaintext was never
copied, GitHub history, consensus, settlement, or authority.
"""

from __future__ import annotations

import base64
import fcntl
import hashlib
import json
import os
import stat
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from nexus_room import ZERO_HASH, canonical_json_bytes


LOOM_ARCHIVE_SCHEMA = "nexus.loom.sealed-record/v1"
LOOM_ARCHIVE_ID = "nexus-assistant-local-loom/v1"
LOOM_RECORD_DOMAIN = b"NEXUS_LOOM_SEALED_RECORD_V1\x00"
MAX_RAW_RECORD_BYTES = 2_097_152
MAX_ENCODED_RECORD_BYTES = 3_000_000
MAX_ARCHIVE_BYTES = 134_217_728
STATUS_AUTHORITY = "NONE"


class LoomArchiveError(ValueError):
    """The local archive or a requested transition is invalid."""


class LoomArchiveCryptoError(LoomArchiveError):
    """Authenticated decryption or a cryptographic commitment failed."""


def _b64u(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64u_decode(value: str) -> bytes:
    if not isinstance(value, str):
        raise LoomArchiveError("base64url field must be a string")
    padding = "=" * ((4 - len(value) % 4) % 4)
    try:
        return base64.b64decode(
            value + padding,
            altchars=b"-_",
            validate=True,
        )
    except (TypeError, ValueError) as error:
        raise LoomArchiveError("invalid base64url field") from error


def _record_id(core: dict) -> str:
    return hashlib.sha256(
        LOOM_RECORD_DOMAIN + canonical_json_bytes(core)
    ).hexdigest()


@dataclass(frozen=True)
class SealedLoomRecord:
    schema: str
    archive_id: str
    sequence: int
    previous_record_id: str
    session_id: str
    event_index: int
    created_at: str
    raw_sha256: str
    raw_byte_length: int
    privacy: str
    status_authority: str
    nonce: str
    ciphertext_sha256: str
    record_id: str
    ciphertext: str

    def aad_payload(self) -> dict:
        return {
            "schema": self.schema,
            "archive_id": self.archive_id,
            "sequence": self.sequence,
            "previous_record_id": self.previous_record_id,
            "session_id": self.session_id,
            "event_index": self.event_index,
            "created_at": self.created_at,
            "raw_sha256": self.raw_sha256,
            "raw_byte_length": self.raw_byte_length,
            "privacy": self.privacy,
            "status_authority": self.status_authority,
            "nonce": self.nonce,
        }

    def core_payload(self) -> dict:
        return {
            **self.aad_payload(),
            "ciphertext_sha256": self.ciphertext_sha256,
        }

    def validate_integrity(self) -> None:
        if self.schema != LOOM_ARCHIVE_SCHEMA:
            raise LoomArchiveError("unsupported LOOM archive schema")
        if self.archive_id != LOOM_ARCHIVE_ID:
            raise LoomArchiveError("record belongs to another archive profile")
        if self.sequence < 1 or self.event_index < 1:
            raise LoomArchiveError("record sequence and event index must be positive")
        if not self.session_id or len(self.session_id) > 160:
            raise LoomArchiveError("session_id must contain 1..160 characters")
        if not self.created_at or len(self.created_at) > 100:
            raise LoomArchiveError("created_at must contain 1..100 characters")
        if self.privacy != "LOCAL_ENCRYPTED":
            raise LoomArchiveError("archive privacy label must be LOCAL_ENCRYPTED")
        if self.status_authority != STATUS_AUTHORITY:
            raise LoomArchiveError("archive records cannot carry authority")
        nonce = _b64u_decode(self.nonce)
        ciphertext = _b64u_decode(self.ciphertext)
        if len(nonce) != 12:
            raise LoomArchiveError("ChaCha20-Poly1305 nonce must be 12 bytes")
        if self.raw_byte_length < 1 or self.raw_byte_length > MAX_RAW_RECORD_BYTES:
            raise LoomArchiveError("raw record length is outside the bound")
        if len(ciphertext) != self.raw_byte_length + 16:
            raise LoomArchiveCryptoError("ciphertext length does not match commitment")
        if hashlib.sha256(ciphertext).hexdigest() != self.ciphertext_sha256:
            raise LoomArchiveCryptoError("ciphertext hash does not match commitment")
        if _record_id(self.core_payload()) != self.record_id:
            raise LoomArchiveCryptoError("record ID does not match canonical bytes")


def _record_from_mapping(value: object) -> SealedLoomRecord:
    if not isinstance(value, dict):
        raise LoomArchiveError("archive line must contain one JSON object")
    expected = set(SealedLoomRecord.__dataclass_fields__)
    if set(value) != expected:
        raise LoomArchiveError("archive record fields do not match the schema")
    try:
        record = SealedLoomRecord(**value)
    except TypeError as error:
        raise LoomArchiveError("archive record types are invalid") from error
    record.validate_integrity()
    return record


def _decode_archive(data: bytes) -> tuple[SealedLoomRecord, ...]:
    if not data:
        return ()
    if not data.endswith(b"\n"):
        raise LoomArchiveError("archive has a truncated final record")
    records: list[SealedLoomRecord] = []
    expected_previous = ZERO_HASH
    for index, line in enumerate(data.splitlines(), start=1):
        if not line or len(line) > MAX_ENCODED_RECORD_BYTES:
            raise LoomArchiveError("archive contains an empty or oversized record")
        try:
            value = json.loads(line.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise LoomArchiveError("archive record is not valid UTF-8 JSON") from error
        if canonical_json_bytes(value) != line:
            raise LoomArchiveError("archive record bytes are not canonical")
        record = _record_from_mapping(value)
        if record.sequence != index:
            raise LoomArchiveError("archive sequence is not contiguous")
        if record.previous_record_id != expected_previous:
            raise LoomArchiveError("archive hash chain is broken")
        records.append(record)
        expected_previous = record.record_id
    return tuple(records)


@contextmanager
def _locked_file(
    path: Path,
    *,
    create: bool,
    exclusive: bool,
) -> Iterator[int]:
    flags = os.O_CLOEXEC | (os.O_RDWR if exclusive else os.O_RDONLY)
    if create:
        flags |= os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        mode = os.fstat(fd).st_mode
        if not stat.S_ISREG(mode):
            raise LoomArchiveError("archive path is not a regular file")
        if exclusive:
            os.fchmod(fd, 0o600)
        fcntl.flock(fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        yield fd
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def _read_fd(fd: int) -> bytes:
    size = os.fstat(fd).st_size
    if size > MAX_ARCHIVE_BYTES:
        raise LoomArchiveError("archive exceeds the local size ceiling")
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    remaining = size
    while remaining:
        chunk = os.read(fd, min(remaining, 1_048_576))
        if not chunk:
            raise LoomArchiveError("archive changed during locked read")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


class LoomSealedArchive:
    """Append and open exact local records using a caller-owned 256-bit key."""

    def __init__(self, path: Path | str, key: bytes):
        self.path = Path(path)
        if not isinstance(key, bytes) or len(key) != 32:
            raise LoomArchiveError("LOOM archive key must be exactly 32 bytes")
        self._key = bytes(key)

    def append(
        self,
        raw: bytes,
        *,
        session_id: str,
        event_index: int,
        created_at: str,
    ) -> SealedLoomRecord:
        if not isinstance(raw, bytes) or not raw:
            raise LoomArchiveError("raw LOOM record must be non-empty bytes")
        if len(raw) > MAX_RAW_RECORD_BYTES:
            raise LoomArchiveError("raw LOOM record exceeds the local size ceiling")
        if not session_id or len(session_id) > 160:
            raise LoomArchiveError("session_id must contain 1..160 characters")
        if event_index < 1:
            raise LoomArchiveError("event_index must be positive")
        if not created_at or len(created_at) > 100:
            raise LoomArchiveError("created_at must contain 1..100 characters")

        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            os.chmod(self.path.parent, 0o700)
        except OSError:
            pass
        with _locked_file(self.path, create=True, exclusive=True) as fd:
            existing = _read_fd(fd)
            records = _decode_archive(existing)
            prior_session_indexes = [
                record.event_index
                for record in records
                if record.session_id == session_id
            ]
            expected_event_index = (
                max(prior_session_indexes) + 1
                if prior_session_indexes
                else 1
            )
            if event_index != expected_event_index:
                raise LoomArchiveError(
                    "session event index is not the next contiguous value"
                )
            sequence = len(records) + 1
            previous = records[-1].record_id if records else ZERO_HASH
            nonce = os.urandom(12)
            aad_payload = {
                "schema": LOOM_ARCHIVE_SCHEMA,
                "archive_id": LOOM_ARCHIVE_ID,
                "sequence": sequence,
                "previous_record_id": previous,
                "session_id": session_id,
                "event_index": event_index,
                "created_at": created_at,
                "raw_sha256": hashlib.sha256(raw).hexdigest(),
                "raw_byte_length": len(raw),
                "privacy": "LOCAL_ENCRYPTED",
                "status_authority": STATUS_AUTHORITY,
                "nonce": _b64u(nonce),
            }
            ciphertext = ChaCha20Poly1305(self._key).encrypt(
                nonce,
                raw,
                canonical_json_bytes(aad_payload),
            )
            core = {
                **aad_payload,
                "ciphertext_sha256": hashlib.sha256(ciphertext).hexdigest(),
            }
            record = SealedLoomRecord(
                **core,
                record_id=_record_id(core),
                ciphertext=_b64u(ciphertext),
            )
            encoded = canonical_json_bytes(asdict(record)) + b"\n"
            if len(existing) + len(encoded) > MAX_ARCHIVE_BYTES:
                raise LoomArchiveError("append would exceed the archive size ceiling")
            os.lseek(fd, 0, os.SEEK_END)
            view = memoryview(encoded)
            while view:
                written = os.write(fd, view)
                if written <= 0:
                    raise LoomArchiveError("archive append did not complete")
                view = view[written:]
            os.fsync(fd)
            return record

    def records(self) -> tuple[SealedLoomRecord, ...]:
        if not self.path.exists():
            return ()
        with _locked_file(self.path, create=False, exclusive=False) as fd:
            return _decode_archive(_read_fd(fd))

    def open_record(self, record: SealedLoomRecord) -> bytes:
        record.validate_integrity()
        try:
            plaintext = ChaCha20Poly1305(self._key).decrypt(
                _b64u_decode(record.nonce),
                _b64u_decode(record.ciphertext),
                canonical_json_bytes(record.aad_payload()),
            )
        except InvalidTag as error:
            raise LoomArchiveCryptoError(
                "LOOM record authenticated decryption failed"
            ) from error
        if len(plaintext) != record.raw_byte_length:
            raise LoomArchiveCryptoError("opened record length does not match")
        if hashlib.sha256(plaintext).hexdigest() != record.raw_sha256:
            raise LoomArchiveCryptoError("opened record hash does not match")
        return plaintext
