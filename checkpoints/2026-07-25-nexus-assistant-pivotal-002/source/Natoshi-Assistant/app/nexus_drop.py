#!/usr/bin/env python3
"""Locally sealed, transport-independent Greywire-style NEXUS Drops.

A Drop separates the encrypted bytes from a tiny signed custody object:

``plaintext --local AEAD--> content-addressed ciphertext blob
                                  |
                                  v
                  single live custody capability
```

Moving the capability resembles moving one UTXO/satoshi: one live output is
consumed and exactly one successor is created.  This proves an ordered custody
claim and rejects a second spend in the same accepted history.  It does *not*
make digital data non-copyable after an authorised recipient decrypts it, and
it does not create money, settlement, or universal finality.

The encrypted Drop can be carried by a live kernel route, GitHub request,
Nostr, IRC, removable media, dial-up, or another future bearer.  The transport
never determines validity.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any

from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from nexus_room import ZERO_HASH, RoomProtocolError, canonical_json_bytes


DROP_SCHEMA = "nexus.greywire.drop/v1"
CUSTODY_OUTPUT_SCHEMA = "nexus.greywire.custody-output/v1"
CUSTODY_TRANSFER_SCHEMA = "nexus.greywire.custody-transfer/v1"
MAX_DROP_BYTES = 16 * 1024 * 1024

ENDPOINT_DOMAIN = b"NEXUS_DROP_ENDPOINT_V1\x00"
DROP_DOMAIN = b"NEXUS_DROP_V1\x00"
DROP_SIGNATURE_DOMAIN = b"NEXUS_DROP_SIGNATURE_V1\x00"
DROP_WRAP_DOMAIN = b"NEXUS_DROP_KEY_WRAP_V1\x00"
CUSTODY_OUTPUT_DOMAIN = b"NEXUS_DROP_CUSTODY_OUTPUT_V1\x00"
CUSTODY_TRANSFER_DOMAIN = b"NEXUS_DROP_CUSTODY_TRANSFER_V1\x00"
CUSTODY_SIGNATURE_DOMAIN = b"NEXUS_DROP_CUSTODY_SIGNATURE_V1\x00"

PROOF_BOUNDARY = (
    "Proves signed custody transitions and encrypted-content integrity; does not "
    "prove that decrypted bytes were not copied, that a claim is true, or that "
    "the transition is legal settlement."
)


class DropProtocolError(RoomProtocolError):
    pass


class DropCryptoError(DropProtocolError):
    pass


def _b64u(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64u_decode(value: str) -> bytes:
    if not isinstance(value, str):
        raise DropProtocolError("base64url value must be a string")
    padding = "=" * ((4 - len(value) % 4) % 4)
    try:
        return base64.b64decode(
            value + padding,
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, TypeError) as error:
        raise DropProtocolError("invalid base64url value") from error


def _raw_public_bytes(key: Ed25519PublicKey | X25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _sha256_domain(domain: bytes, payload: bytes) -> str:
    return hashlib.sha256(domain + payload).hexdigest()


def _ed25519_public(value: str) -> Ed25519PublicKey:
    raw = _b64u_decode(value)
    if len(raw) != 32:
        raise DropProtocolError("Ed25519 public key must be 32 bytes")
    try:
        return Ed25519PublicKey.from_public_bytes(raw)
    except ValueError as error:
        raise DropProtocolError("invalid Ed25519 public key") from error


def _x25519_public(value: str) -> X25519PublicKey:
    raw = _b64u_decode(value)
    if len(raw) != 32:
        raise DropProtocolError("X25519 public key must be 32 bytes")
    try:
        return X25519PublicKey.from_public_bytes(raw)
    except ValueError as error:
        raise DropProtocolError("invalid X25519 public key") from error


def _endpoint_id(signing_public_key: str, encryption_public_key: str) -> str:
    return _sha256_domain(
        ENDPOINT_DOMAIN,
        _b64u_decode(signing_public_key) + _b64u_decode(encryption_public_key),
    )[:32]


@dataclass(frozen=True)
class DropIdentity:
    """A local endpoint with independent signing and decryption keys."""

    endpoint_id: str
    signing_public_key: str
    encryption_public_key: str
    _signing_private_key: Ed25519PrivateKey = field(repr=False, compare=False)
    _encryption_private_key: X25519PrivateKey = field(repr=False, compare=False)

    @classmethod
    def generate(cls) -> "DropIdentity":
        signing = Ed25519PrivateKey.generate()
        encryption = X25519PrivateKey.generate()
        signing_public = _b64u(_raw_public_bytes(signing.public_key()))
        encryption_public = _b64u(_raw_public_bytes(encryption.public_key()))
        return cls(
            endpoint_id=_endpoint_id(signing_public, encryption_public),
            signing_public_key=signing_public,
            encryption_public_key=encryption_public,
            _signing_private_key=signing,
            _encryption_private_key=encryption,
        )

    def sign(self, domain: bytes, payload: bytes) -> str:
        return _b64u(self._signing_private_key.sign(domain + payload))


def _derive_wrap_key(
    *,
    private_key: X25519PrivateKey,
    peer_public_key: X25519PublicKey,
    aad: bytes,
) -> bytes:
    shared = private_key.exchange(peer_public_key)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=DROP_WRAP_DOMAIN + hashlib.sha256(aad).digest(),
    ).derive(shared)


@dataclass(frozen=True)
class SealedDrop:
    schema: str
    sender_id: str
    sender_signing_public_key: str
    sender_encryption_public_key: str
    recipient_id: str
    recipient_encryption_public_key: str
    media_type: str
    plaintext_size: int
    ciphertext_size: int
    payload_nonce: str
    ciphertext_sha256: str
    ephemeral_public_key: str
    wrap_nonce: str
    wrapped_key_sha256: str
    drop_id: str
    sender_signature: str
    wrapped_key: str = field(repr=False)
    ciphertext: str = field(repr=False)

    @classmethod
    def seal(
        cls,
        *,
        sender: DropIdentity,
        recipient_id: str,
        recipient_encryption_public_key: str,
        plaintext: bytes,
        media_type: str = "application/octet-stream",
    ) -> "SealedDrop":
        if not isinstance(plaintext, bytes):
            raise DropProtocolError("Drop plaintext must be bytes")
        if len(plaintext) > MAX_DROP_BYTES:
            raise DropProtocolError("Drop exceeds maximum plaintext size")
        if not media_type or len(media_type) > 200:
            raise DropProtocolError("media_type must contain 1..200 characters")
        recipient_public = _x25519_public(recipient_encryption_public_key)

        content_key = os.urandom(32)
        payload_nonce = os.urandom(12)
        payload_aad = canonical_json_bytes(
            {
                "schema": DROP_SCHEMA,
                "sender_id": sender.endpoint_id,
                "recipient_id": recipient_id,
                "media_type": media_type,
                "plaintext_size": len(plaintext),
            }
        )
        ciphertext = ChaCha20Poly1305(content_key).encrypt(
            payload_nonce,
            plaintext,
            payload_aad,
        )
        ephemeral_private = X25519PrivateKey.generate()
        ephemeral_public = _b64u(
            _raw_public_bytes(ephemeral_private.public_key())
        )
        wrap_nonce = os.urandom(12)
        wrap_aad_payload = {
            "schema": DROP_SCHEMA,
            "sender_id": sender.endpoint_id,
            "sender_signing_public_key": sender.signing_public_key,
            "sender_encryption_public_key": sender.encryption_public_key,
            "recipient_id": recipient_id,
            "recipient_encryption_public_key": recipient_encryption_public_key,
            "media_type": media_type,
            "plaintext_size": len(plaintext),
            "ciphertext_size": len(ciphertext),
            "payload_nonce": _b64u(payload_nonce),
            "ciphertext_sha256": hashlib.sha256(ciphertext).hexdigest(),
            "ephemeral_public_key": ephemeral_public,
            "wrap_nonce": _b64u(wrap_nonce),
        }
        wrap_aad = canonical_json_bytes(wrap_aad_payload)
        wrap_key = _derive_wrap_key(
            private_key=ephemeral_private,
            peer_public_key=recipient_public,
            aad=wrap_aad,
        )
        wrapped_key = ChaCha20Poly1305(wrap_key).encrypt(
            wrap_nonce,
            content_key,
            wrap_aad,
        )
        core_payload = {
            **wrap_aad_payload,
            "wrapped_key_sha256": hashlib.sha256(wrapped_key).hexdigest(),
        }
        drop_id = _sha256_domain(DROP_DOMAIN, canonical_json_bytes(core_payload))
        sender_signature = sender.sign(
            DROP_SIGNATURE_DOMAIN,
            bytes.fromhex(drop_id),
        )
        return cls(
            **core_payload,
            drop_id=drop_id,
            sender_signature=sender_signature,
            wrapped_key=_b64u(wrapped_key),
            ciphertext=_b64u(ciphertext),
        )

    def wrap_aad_payload(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "sender_id": self.sender_id,
            "sender_signing_public_key": self.sender_signing_public_key,
            "sender_encryption_public_key": self.sender_encryption_public_key,
            "recipient_id": self.recipient_id,
            "recipient_encryption_public_key": self.recipient_encryption_public_key,
            "media_type": self.media_type,
            "plaintext_size": self.plaintext_size,
            "ciphertext_size": self.ciphertext_size,
            "payload_nonce": self.payload_nonce,
            "ciphertext_sha256": self.ciphertext_sha256,
            "ephemeral_public_key": self.ephemeral_public_key,
            "wrap_nonce": self.wrap_nonce,
        }

    def core_payload(self) -> dict[str, Any]:
        return {
            **self.wrap_aad_payload(),
            "wrapped_key_sha256": self.wrapped_key_sha256,
        }

    def lightweight_manifest(self) -> dict[str, Any]:
        """Return the signed commitment without encrypted bulk bytes."""

        return {
            **self.core_payload(),
            "drop_id": self.drop_id,
            "sender_signature": self.sender_signature,
            "proof_boundary": PROOF_BOUNDARY,
        }

    def verify_manifest(self) -> bool:
        if self.schema != DROP_SCHEMA:
            return False
        if _endpoint_id(
            self.sender_signing_public_key,
            self.sender_encryption_public_key,
        ) != self.sender_id:
            return False
        expected_id = _sha256_domain(
            DROP_DOMAIN,
            canonical_json_bytes(self.core_payload()),
        )
        if expected_id != self.drop_id:
            return False
        try:
            _ed25519_public(self.sender_signing_public_key).verify(
                _b64u_decode(self.sender_signature),
                DROP_SIGNATURE_DOMAIN + bytes.fromhex(self.drop_id),
            )
        except (InvalidSignature, DropProtocolError, ValueError):
            return False
        return True

    def open(self, recipient: DropIdentity) -> bytes:
        if recipient.endpoint_id != self.recipient_id:
            raise DropCryptoError("Drop is not addressed to this endpoint")
        if recipient.encryption_public_key != self.recipient_encryption_public_key:
            raise DropCryptoError("recipient encryption key does not match")
        if not self.verify_manifest():
            raise DropCryptoError("Drop manifest signature or hash is invalid")
        ciphertext = _b64u_decode(self.ciphertext)
        wrapped_key = _b64u_decode(self.wrapped_key)
        if len(ciphertext) != self.ciphertext_size:
            raise DropCryptoError("ciphertext size does not match manifest")
        if hashlib.sha256(ciphertext).hexdigest() != self.ciphertext_sha256:
            raise DropCryptoError("ciphertext hash does not match manifest")
        if hashlib.sha256(wrapped_key).hexdigest() != self.wrapped_key_sha256:
            raise DropCryptoError("wrapped key hash does not match manifest")
        wrap_aad = canonical_json_bytes(self.wrap_aad_payload())
        wrap_key = _derive_wrap_key(
            private_key=recipient._encryption_private_key,
            peer_public_key=_x25519_public(self.ephemeral_public_key),
            aad=wrap_aad,
        )
        try:
            content_key = ChaCha20Poly1305(wrap_key).decrypt(
                _b64u_decode(self.wrap_nonce),
                wrapped_key,
                wrap_aad,
            )
            plaintext = ChaCha20Poly1305(content_key).decrypt(
                _b64u_decode(self.payload_nonce),
                ciphertext,
                canonical_json_bytes(
                    {
                        "schema": DROP_SCHEMA,
                        "sender_id": self.sender_id,
                        "recipient_id": self.recipient_id,
                        "media_type": self.media_type,
                        "plaintext_size": self.plaintext_size,
                    }
                ),
            )
        except InvalidTag as error:
            raise DropCryptoError("Drop authenticated decryption failed") from error
        if len(plaintext) != self.plaintext_size:
            raise DropCryptoError("plaintext size does not match manifest")
        return plaintext


@dataclass(frozen=True)
class CustodyOutput:
    schema: str
    drop_id: str
    transfer_index: int
    previous_output_id: str
    owner_id: str
    owner_signing_public_key: str
    owner_encryption_public_key: str
    salt: str
    output_id: str

    @classmethod
    def create(
        cls,
        *,
        drop_id: str,
        transfer_index: int,
        previous_output_id: str,
        owner_id: str,
        owner_signing_public_key: str,
        owner_encryption_public_key: str,
        salt: bytes | None = None,
    ) -> "CustodyOutput":
        if len(drop_id) != 64:
            raise DropProtocolError("drop_id must be a SHA-256 value")
        core = {
            "schema": CUSTODY_OUTPUT_SCHEMA,
            "drop_id": drop_id,
            "transfer_index": transfer_index,
            "previous_output_id": previous_output_id,
            "owner_id": owner_id,
            "owner_signing_public_key": owner_signing_public_key,
            "owner_encryption_public_key": owner_encryption_public_key,
            "salt": _b64u(salt or os.urandom(16)),
        }
        output_id = _sha256_domain(
            CUSTODY_OUTPUT_DOMAIN,
            canonical_json_bytes(core),
        )
        return cls(**core, output_id=output_id)

    def core_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("output_id")
        return payload

    def verify(self) -> bool:
        if _endpoint_id(
            self.owner_signing_public_key,
            self.owner_encryption_public_key,
        ) != self.owner_id:
            return False
        return self.output_id == _sha256_domain(
            CUSTODY_OUTPUT_DOMAIN,
            canonical_json_bytes(self.core_payload()),
        )


@dataclass(frozen=True)
class CustodyTransfer:
    schema: str
    drop_id: str
    consumes_output_id: str
    creates: CustodyOutput
    sender_id: str
    sender_signing_public_key: str
    transfer_id: str
    signature: str

    @classmethod
    def create(
        cls,
        *,
        current: CustodyOutput,
        sender: DropIdentity,
        new_owner: DropIdentity,
    ) -> "CustodyTransfer":
        if current.owner_id != sender.endpoint_id:
            raise DropProtocolError("sender does not own the custody output")
        if current.owner_signing_public_key != sender.signing_public_key:
            raise DropProtocolError("sender signing key does not match custody output")
        if current.owner_encryption_public_key != sender.encryption_public_key:
            raise DropProtocolError("sender encryption key does not match custody output")
        created = CustodyOutput.create(
            drop_id=current.drop_id,
            transfer_index=current.transfer_index + 1,
            previous_output_id=current.output_id,
            owner_id=new_owner.endpoint_id,
            owner_signing_public_key=new_owner.signing_public_key,
            owner_encryption_public_key=new_owner.encryption_public_key,
        )
        core = {
            "schema": CUSTODY_TRANSFER_SCHEMA,
            "drop_id": current.drop_id,
            "consumes_output_id": current.output_id,
            "creates": asdict(created),
            "sender_id": sender.endpoint_id,
            "sender_signing_public_key": sender.signing_public_key,
        }
        transfer_id = _sha256_domain(
            CUSTODY_TRANSFER_DOMAIN,
            canonical_json_bytes(core),
        )
        signature = sender.sign(
            CUSTODY_SIGNATURE_DOMAIN,
            bytes.fromhex(transfer_id),
        )
        return cls(
            schema=CUSTODY_TRANSFER_SCHEMA,
            drop_id=current.drop_id,
            consumes_output_id=current.output_id,
            creates=created,
            sender_id=sender.endpoint_id,
            sender_signing_public_key=sender.signing_public_key,
            transfer_id=transfer_id,
            signature=signature,
        )

    def core_payload(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "drop_id": self.drop_id,
            "consumes_output_id": self.consumes_output_id,
            "creates": asdict(self.creates),
            "sender_id": self.sender_id,
            "sender_signing_public_key": self.sender_signing_public_key,
        }


class DropCustodyLedger:
    """Small deterministic single-live-output custody state."""

    def __init__(self):
        self.outputs: dict[str, CustodyOutput] = {}
        self.consumed: set[str] = set()
        self.transfers: list[str] = []

    def register(self, *, drop: SealedDrop, owner: DropIdentity) -> CustodyOutput:
        if not drop.verify_manifest():
            raise DropCryptoError("cannot register an invalid Drop")
        if owner.endpoint_id != drop.sender_id:
            raise DropProtocolError("custody genesis must belong to the Drop sender")
        if owner.signing_public_key != drop.sender_signing_public_key:
            raise DropProtocolError("custody genesis signing key does not match Drop")
        if owner.encryption_public_key != drop.sender_encryption_public_key:
            raise DropProtocolError("custody genesis encryption key does not match Drop")
        if any(output.drop_id == drop.drop_id for output in self.outputs.values()):
            raise DropProtocolError("Drop already has a custody genesis")
        output = CustodyOutput.create(
            drop_id=drop.drop_id,
            transfer_index=0,
            previous_output_id=ZERO_HASH,
            owner_id=owner.endpoint_id,
            owner_signing_public_key=owner.signing_public_key,
            owner_encryption_public_key=owner.encryption_public_key,
            salt=bytes.fromhex(drop.drop_id)[:16],
        )
        self.outputs[output.output_id] = output
        return output

    def accept(self, transfer: CustodyTransfer) -> CustodyOutput:
        current = self.outputs.get(transfer.consumes_output_id)
        if current is None:
            raise DropProtocolError("consumed custody output is unknown")
        if transfer.consumes_output_id in self.consumed:
            raise DropProtocolError("custody output was already transferred")
        if not current.verify() or not transfer.creates.verify():
            raise DropProtocolError("custody output hash is invalid")
        if transfer.schema != CUSTODY_TRANSFER_SCHEMA:
            raise DropProtocolError("unsupported custody transfer schema")
        if current.drop_id != transfer.drop_id:
            raise DropProtocolError("transfer changes the Drop identity")
        if transfer.sender_id != current.owner_id:
            raise DropProtocolError("transfer sender is not the current owner")
        if transfer.sender_signing_public_key != current.owner_signing_public_key:
            raise DropProtocolError("transfer sender key is not the owner key")
        if transfer.creates.drop_id != current.drop_id:
            raise DropProtocolError("successor output changes the Drop identity")
        if transfer.creates.previous_output_id != current.output_id:
            raise DropProtocolError("successor output is not linked to consumed output")
        if transfer.creates.transfer_index != current.transfer_index + 1:
            raise DropProtocolError("successor transfer index is not monotonic")
        expected_id = _sha256_domain(
            CUSTODY_TRANSFER_DOMAIN,
            canonical_json_bytes(transfer.core_payload()),
        )
        if expected_id != transfer.transfer_id:
            raise DropProtocolError("custody transfer ID does not verify")
        try:
            _ed25519_public(transfer.sender_signing_public_key).verify(
                _b64u_decode(transfer.signature),
                CUSTODY_SIGNATURE_DOMAIN + bytes.fromhex(transfer.transfer_id),
            )
        except (InvalidSignature, DropProtocolError, ValueError) as error:
            raise DropCryptoError("custody transfer signature is invalid") from error

        self.consumed.add(current.output_id)
        self.outputs[transfer.creates.output_id] = transfer.creates
        self.transfers.append(transfer.transfer_id)
        return transfer.creates

    def live_output(self, drop_id: str) -> CustodyOutput | None:
        candidates = [
            output
            for output in self.outputs.values()
            if output.drop_id == drop_id and output.output_id not in self.consumed
        ]
        if len(candidates) > 1:
            raise DropProtocolError("ledger contains multiple live custody outputs")
        return candidates[0] if candidates else None
