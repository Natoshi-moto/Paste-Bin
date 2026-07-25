#!/usr/bin/env python3

from __future__ import annotations

import dataclasses
import hashlib
import unittest

from nexus_room import (
    ROOMFINAL_BOUNDARY,
    DeterministicCommonsPolicy,
    ObserverReceipt,
    RoomCheckpoint,
    RoomCryptoError,
    RoomEngine,
    RoomEpochKey,
    RoomIdentity,
    RoomProtocolError,
    canonical_json_bytes,
)


class CanonicalEncodingTests(unittest.TestCase):
    def test_nested_keys_have_one_byte_encoding(self):
        left = {"z": {"b": 2, "a": 1}, "a": [3, {"y": True, "x": None}]}
        right = {"a": [3, {"x": None, "y": True}], "z": {"a": 1, "b": 2}}
        self.assertEqual(canonical_json_bytes(left), canonical_json_bytes(right))

    def test_floats_are_rejected(self):
        with self.assertRaisesRegex(RoomProtocolError, "floating-point"):
            canonical_json_bytes({"amount": 0.1})


class EncryptedSharedRoomTests(unittest.TestCase):
    def setUp(self):
        self.alice = RoomIdentity.generate()
        self.bob = RoomIdentity.generate()
        self.observer = RoomIdentity.generate()
        self.policy = DeterministicCommonsPolicy.create(
            [self.bob.member_id, self.alice.member_id]
        )
        self.key = RoomEpochKey.generate(epoch=7)
        self.left = RoomEngine(
            room_id="room-test",
            policy=self.policy,
            epoch_key=self.key,
        )
        self.right = RoomEngine(
            room_id="room-test",
            policy=self.policy,
            epoch_key=self.key,
        )

    def test_two_replicas_replay_to_one_state(self):
        event = self.left.create_event(
            identity=self.alice,
            kind="MESSAGE",
            body={"text": "private lightbulb"},
        )
        payload = self.right.ingest_event(event)
        self.assertEqual(payload["body"]["text"], "private lightbulb")
        self.assertEqual(self.left.state.state_root, self.right.state.state_root)
        self.assertEqual(self.left.state.head_event_id, self.right.state.head_event_id)
        self.assertEqual(
            self.left.state.accumulator_root,
            self.right.state.accumulator_root,
        )

    def test_header_and_ciphertext_do_not_contain_plaintext(self):
        secret = "orchid-neuron-secret"
        event = self.left.create_event(
            identity=self.alice,
            kind="MESSAGE",
            body={"text": secret},
        )
        self.assertNotIn(secret, str(event.lightweight_header()))
        self.assertNotIn(secret, event.ciphertext)

    def test_ciphertext_tamper_is_rejected(self):
        event = self.left.create_event(
            identity=self.alice,
            kind="MESSAGE",
            body={"text": "chain me"},
        )
        replacement = ("A" if event.ciphertext[0] != "A" else "B") + event.ciphertext[1:]
        tampered = dataclasses.replace(event, ciphertext=replacement)
        with self.assertRaises(RoomCryptoError):
            self.right.ingest_event(tampered)

    def test_forked_previous_head_is_rejected(self):
        accepted = self.left.create_event(
            identity=self.alice,
            kind="MESSAGE",
            body={"text": "ordered"},
        )
        self.right.ingest_event(accepted)

        fork_source = RoomEngine(
            room_id="room-test",
            policy=self.policy,
            epoch_key=self.key,
        )
        fork_source.create_event(
            identity=self.bob,
            kind="MESSAGE",
            body={"text": "different slot one"},
        )
        forked = fork_source.create_event(
            identity=self.alice,
            kind="MESSAGE",
            body={"text": "validly signed but wrong parent"},
        )
        with self.assertRaisesRegex(RoomProtocolError, "current room head"):
            self.right.ingest_event(forked)

    def test_observer_receipt_is_evidence_not_authority(self):
        event = self.left.create_event(
            identity=self.alice,
            kind="MESSAGE",
            body={"text": "observer cannot read this"},
        )
        receipt = ObserverReceipt.create(
            event=event,
            observer=self.observer,
            ciphertext_retained=False,
        )
        self.assertTrue(receipt.verify())
        self.assertEqual(receipt.status_authority, "NONE")
        self.assertEqual(receipt.evidence_scope, "OBSERVED_ENVELOPE")
        self.assertNotIn("observer cannot read this", str(dataclasses.asdict(receipt)))

    def test_checkpoint_is_lightweight_and_scoped(self):
        self.left.create_event(
            identity=self.alice,
            kind="MESSAGE",
            body={"text": "one"},
        )
        checkpoint = self.left.checkpoint(sequencer=self.bob)
        self.assertIsInstance(checkpoint, RoomCheckpoint)
        self.assertTrue(
            checkpoint.verify(
                expected_policy_sha256=self.policy.policy_sha256,
                allowed_signers=self.policy.active_members,
            )
        )
        self.assertFalse(
            checkpoint.verify(
                expected_policy_sha256="f" * 64,
                allowed_signers=self.policy.active_members,
            )
        )
        self.assertEqual(checkpoint.reliance_scope, "ORDERED_ROOM_STATE_ONLY")
        self.assertNotIn("ciphertext", dataclasses.asdict(checkpoint))
        self.assertIn("not permissionless consensus", ROOMFINAL_BOUNDARY)


class DeterministicCommonsTests(unittest.TestCase):
    def setUp(self):
        self.members = [RoomIdentity.generate() for _ in range(3)]
        self.policy = DeterministicCommonsPolicy.create(
            [member.member_id for member in self.members],
            max_active_tasks_per_member=1,
        )
        self.by_id = {member.member_id: member for member in self.members}
        self.engine = RoomEngine(
            room_id="commons-room",
            policy=self.policy,
            epoch_key=RoomEpochKey.generate(),
        )

    def test_round_robin_assigns_without_hidden_admin(self):
        sender = self.members[0]
        for index in range(3):
            self.engine.create_event(
                identity=sender,
                kind="TASK_OFFER",
                body={"task_id": f"task-{index}", "summary": f"work {index}"},
            )
        assigned = [
            self.engine.state.tasks[f"task-{index}"]["assigned_to"]
            for index in range(3)
        ]
        self.assertEqual(assigned, list(self.policy.active_members))
        self.assertFalse(self.policy.hidden_admins)
        self.assertFalse(self.policy.human_micromanagement_required)
        self.assertEqual(self.policy.membership_mode, "OPT_IN_EPOCH_BOUND")

    def test_only_assignee_can_submit_result(self):
        self.engine.create_event(
            identity=self.members[0],
            kind="TASK_OFFER",
            body={"task_id": "task-a", "summary": "bounded work"},
        )
        assignee_id = self.engine.state.tasks["task-a"]["assigned_to"]
        wrong = next(item for item in self.members if item.member_id != assignee_id)
        with self.assertRaisesRegex(RoomProtocolError, "assigned member"):
            self.engine.create_event(
                identity=wrong,
                kind="TASK_RESULT",
                body={
                    "task_id": "task-a",
                    "result_sha256": hashlib.sha256(b"result").hexdigest(),
                },
            )

    def test_nonmember_has_no_implicit_admin_path(self):
        outsider = RoomIdentity.generate()
        with self.assertRaisesRegex(RoomProtocolError, "active room member"):
            self.engine.create_event(
                identity=outsider,
                kind="MESSAGE",
                body={"text": "override"},
            )


if __name__ == "__main__":
    unittest.main()
