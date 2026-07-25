import json
import unittest

from nexus_forge import (
    ReviewSeat,
    approve_loom_scrub,
    capture_loom_session,
    scrub_loom_session,
)
from nexus_forge_runtime import run_ordered_forge_review


class OrderedForgeRuntimeTests(unittest.TestCase):
    def test_callback_is_invoked_deepseek_then_distinct_higher_model(self):
        session = capture_loom_session(
            "operator: exact session",
            sealed_archive_ref="loom-record:fixture",
        )
        session = scrub_loom_session(session)
        session = approve_loom_scrub(
            session,
            approval_ref="fixture-approval",
            expected_scrubbed_sha256=session.scrubbed_sha256,
            allowed_provider_families=("deepseek", "openai"),
        )
        deepseek = ReviewSeat(
            "deepseek",
            "deepseek-chat",
            "deepseek",
            10,
        )
        higher = ReviewSeat(
            "openai",
            "gpt-fixture",
            "openai",
            20,
        )
        seen = []

        def call(seat, messages):
            seen.append((seat.family_id, [message.role for message in messages]))
            if seat.family_id == "deepseek":
                return json.dumps(
                    {
                        "record_boundaries": [],
                        "tags": [],
                        "claims": [],
                        "privacy_flags": [],
                        "non_claims": ["proposal only"],
                    }
                )
            return json.dumps(
                {
                    "corrections": [],
                    "missed_risks": [],
                    "accepted_items": [],
                    "rejected_items": [],
                    "non_claims": ["not independent proof"],
                }
            )

        result = run_ordered_forge_review(
            session,
            deepseek_seat=deepseek,
            higher_seat=higher,
            call_review=call,
        )

        self.assertEqual(
            seen,
            [("deepseek", ["user"]), ("openai", ["user"])],
        )
        self.assertEqual(
            result.call_order,
            ("deepseek:deepseek-chat", "openai:gpt-fixture"),
        )
        self.assertTrue(result.session.validation.passed)
        candidate = json.loads(result.candidate)
        self.assertFalse(candidate["source"]["raw_included"])
        self.assertEqual(
            candidate["artifact_kind"],
            "SCRUBBED_DERIVATIVE",
        )
