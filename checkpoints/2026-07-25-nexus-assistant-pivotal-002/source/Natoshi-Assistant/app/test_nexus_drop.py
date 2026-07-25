#!/usr/bin/env python3

from __future__ import annotations

import dataclasses
import unittest

from nexus_drop import (
    PROOF_BOUNDARY,
    CustodyTransfer,
    DropCryptoError,
    DropCustodyLedger,
    DropIdentity,
    DropProtocolError,
    SealedDrop,
)


class SealedDropTests(unittest.TestCase):
    def setUp(self):
        self.alice = DropIdentity.generate()
        self.bob = DropIdentity.generate()
        self.mallory = DropIdentity.generate()
        self.plaintext = b"private spore over any future bearer"
        self.drop = SealedDrop.seal(
            sender=self.alice,
            recipient_id=self.bob.endpoint_id,
            recipient_encryption_public_key=self.bob.encryption_public_key,
            plaintext=self.plaintext,
            media_type="text/plain",
        )

    def test_only_recipient_opens_locally_sealed_drop(self):
        self.assertEqual(self.drop.open(self.bob), self.plaintext)
        with self.assertRaisesRegex(DropCryptoError, "not addressed"):
            self.drop.open(self.mallory)

    def test_lightweight_manifest_contains_commitment_not_bulk_bytes(self):
        manifest = self.drop.lightweight_manifest()
        self.assertNotIn("ciphertext", manifest)
        self.assertNotIn("wrapped_key", manifest)
        self.assertNotIn(self.plaintext.decode(), str(manifest))
        self.assertTrue(self.drop.verify_manifest())
        self.assertIn("does not prove", PROOF_BOUNDARY)

    def test_ciphertext_tamper_fails_closed(self):
        changed = ("A" if self.drop.ciphertext[0] != "A" else "B")
        tampered = dataclasses.replace(
            self.drop,
            ciphertext=changed + self.drop.ciphertext[1:],
        )
        with self.assertRaises(DropCryptoError):
            tampered.open(self.bob)

    def test_manifest_tamper_fails_signature_or_hash(self):
        tampered = dataclasses.replace(self.drop, media_type="text/html")
        self.assertFalse(tampered.verify_manifest())


class CustodyLedgerTests(unittest.TestCase):
    def setUp(self):
        self.alice = DropIdentity.generate()
        self.bob = DropIdentity.generate()
        self.carol = DropIdentity.generate()
        self.drop = SealedDrop.seal(
            sender=self.alice,
            recipient_id=self.carol.endpoint_id,
            recipient_encryption_public_key=self.carol.encryption_public_key,
            plaintext=b"content remains encrypted while custody moves",
        )
        self.ledger = DropCustodyLedger()
        self.genesis = self.ledger.register(drop=self.drop, owner=self.alice)

    def test_one_output_moves_like_one_satoshi(self):
        transfer = CustodyTransfer.create(
            current=self.genesis,
            sender=self.alice,
            new_owner=self.bob,
        )
        successor = self.ledger.accept(transfer)
        self.assertEqual(successor.owner_id, self.bob.endpoint_id)
        self.assertEqual(successor.drop_id, self.drop.drop_id)
        self.assertEqual(self.ledger.live_output(self.drop.drop_id), successor)
        self.assertIn(self.genesis.output_id, self.ledger.consumed)

    def test_second_transfer_of_same_output_is_rejected(self):
        first = CustodyTransfer.create(
            current=self.genesis,
            sender=self.alice,
            new_owner=self.bob,
        )
        second = CustodyTransfer.create(
            current=self.genesis,
            sender=self.alice,
            new_owner=self.carol,
        )
        self.ledger.accept(first)
        with self.assertRaisesRegex(DropProtocolError, "already transferred"):
            self.ledger.accept(second)

    def test_nonowner_cannot_create_transfer(self):
        with self.assertRaisesRegex(DropProtocolError, "does not own"):
            CustodyTransfer.create(
                current=self.genesis,
                sender=self.bob,
                new_owner=self.carol,
            )

    def test_transfer_replays_identically_on_two_ledgers(self):
        other = DropCustodyLedger()
        other_genesis = other.register(drop=self.drop, owner=self.alice)
        self.assertEqual(other_genesis.output_id, self.genesis.output_id)
        transfer = CustodyTransfer.create(
            current=self.genesis,
            sender=self.alice,
            new_owner=self.bob,
        )
        left = self.ledger.accept(transfer)
        right = other.accept(transfer)
        self.assertEqual(left, right)
        self.assertEqual(
            self.ledger.live_output(self.drop.drop_id),
            other.live_output(self.drop.drop_id),
        )


if __name__ == "__main__":
    unittest.main()
