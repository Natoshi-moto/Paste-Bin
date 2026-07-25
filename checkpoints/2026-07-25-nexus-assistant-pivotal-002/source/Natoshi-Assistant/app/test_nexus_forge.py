import hashlib
import json
import unittest

from nexus_connectors import CommonsPolicy
from nexus_forge import (
    CommitExecutionUnavailable,
    ForgeDisposition,
    ForgeStage,
    ForgeTransitionError,
    ReviewSeat,
    approve_loom_scrub,
    build_deepseek_work_order,
    build_second_review_work_order,
    capture_loom_session,
    choose_local_disposition,
    execute_commit,
    make_commit_proposal,
    record_deepseek_review,
    record_second_review,
    render_forge_candidate,
    scrub_loom_session,
    validate_forge_candidate,
)


DEEPSEEK = ReviewSeat(
    provider="deepseek",
    model="deepseek-chat",
    family="deepseek",
    capability_rank=10,
    local=False,
)
SECOND = ReviewSeat(
    provider="openai",
    model="gpt-review-fixture",
    family="openai",
    capability_rank=20,
    local=False,
)

FIRST_OUTPUT = json.dumps(
    {
        "record_boundaries": [{"start": 1, "end": 2}],
        "tags": ["CONFLICT"],
        "claims": [{"text": "candidate only", "class": "DRAFT"}],
        "privacy_flags": [],
        "non_claims": ["not authority"],
    }
)
SECOND_OUTPUT = json.dumps(
    {
        "corrections": ["keep the claim drafted"],
        "missed_risks": ["third-party context may remain"],
        "accepted_items": ["record boundary"],
        "rejected_items": ["none"],
        "non_claims": ["not independent proof"],
    }
)


def validated_pipeline(
    raw: str = "operator: hello\nassistant: hello",
    *,
    commons_policy: CommonsPolicy | None = None,
):
    session = capture_loom_session(
        raw,
        session_id="test-session",
        created_at="2026-07-25T00:00:00+00:00",
        commons_policy=commons_policy,
        sealed_archive_ref="loom-record:fixture",
    )
    session = scrub_loom_session(session)
    session = approve_loom_scrub(
        session,
        approval_ref="scrub-approval-1",
        expected_scrubbed_sha256=session.scrubbed_sha256,
        allowed_provider_families=("deepseek", "openai"),
    )
    session, _ = build_deepseek_work_order(session, DEEPSEEK)
    session = record_deepseek_review(session, DEEPSEEK, FIRST_OUTPUT)
    session, _ = build_second_review_work_order(session, SECOND)
    session = record_second_review(session, SECOND, SECOND_OUTPUT)
    return validate_forge_candidate(session)


class LoomCaptureAndScrubTests(unittest.TestCase):
    def test_raw_capture_is_exact_local_sealed_and_absent_from_snapshot(self):
        raw = "first\r\nsecond\n"
        session = capture_loom_session(
            raw,
            session_id="Exact Session",
            created_at="2026-07-25T00:00:00+00:00",
            sealed_archive_ref="loom-record:exact-session",
        )
        self.assertEqual(session.raw_text, raw)
        self.assertEqual(
            session.raw_sha256,
            hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(session.raw_label, "VERBATIM_LOCAL_SEALED")
        self.assertEqual(
            session.sealed_archive_ref,
            "loom-record:exact-session",
        )
        self.assertEqual(session.privacy, "LOCAL_ONLY")
        snapshot = json.dumps(session.public_snapshot())
        self.assertNotIn("first\\r\\nsecond", snapshot)
        self.assertNotIn(raw, snapshot)
        self.assertEqual(session.stage, ForgeStage.CAPTURED_LOCAL)

    def test_scrub_redacts_credentials_and_explicit_identity_literals(self):
        raw = (
            "DEEPSEEK_API_KEY=super-secret-value\n"
            "Talked to Named Third Party at noon."
        )
        session = capture_loom_session(raw)
        session = scrub_loom_session(
            session,
            literal_redactions=("Named Third Party",),
        )
        self.assertEqual(session.raw_text, raw)
        self.assertNotIn("super-secret-value", session.scrubbed_text)
        self.assertNotIn("Named Third Party", session.scrubbed_text)
        self.assertGreaterEqual(session.scrub_redactions, 2)
        self.assertTrue(session.scrub_passed)
        self.assertEqual(session.stage, ForgeStage.SCRUB_REVIEW_REQUIRED)

    def test_scrub_approval_is_hash_bound_and_provider_bound(self):
        session = scrub_loom_session(
            capture_loom_session(
                "safe transcript",
                sealed_archive_ref="loom-record:safe",
            )
        )
        with self.assertRaises(ForgeTransitionError):
            approve_loom_scrub(
                session,
                approval_ref="approval",
                expected_scrubbed_sha256="stale",
                allowed_provider_families=("deepseek", "openai"),
            )
        with self.assertRaises(ForgeTransitionError):
            approve_loom_scrub(
                session,
                approval_ref="approval",
                expected_scrubbed_sha256=session.scrubbed_sha256,
                allowed_provider_families=("deepseek",),
            )
        approved = approve_loom_scrub(
            session,
            approval_ref="approval",
            expected_scrubbed_sha256=session.scrubbed_sha256,
            allowed_provider_families=("deepseek", "anthropic"),
        )
        self.assertEqual(approved.stage, ForgeStage.SCRUB_APPROVED)
        self.assertEqual(
            approved.approved_provider_families,
            ("deepseek", "anthropic"),
        )

    def test_memory_only_capture_cannot_be_approved_for_external_models(self):
        session = scrub_loom_session(capture_loom_session("safe transcript"))
        self.assertEqual(session.raw_label, "VERBATIM_LOCAL_MEMORY")
        with self.assertRaises(ForgeTransitionError):
            approve_loom_scrub(
                session,
                approval_ref="approval",
                expected_scrubbed_sha256=session.scrubbed_sha256,
                allowed_provider_families=("deepseek", "openai"),
            )


class OrderedExternalReviewTests(unittest.TestCase):
    def setUp(self):
        session = capture_loom_session(
            "DEEPSEEK_API_KEY=never-route-this\nsafe line",
            session_id="ordered-review",
            sealed_archive_ref="loom-record:ordered-review",
        )
        session = scrub_loom_session(session)
        self.session = approve_loom_scrub(
            session,
            approval_ref="scrub-approval",
            expected_scrubbed_sha256=session.scrubbed_sha256,
            allowed_provider_families=("deepseek", "openai", "anthropic"),
        )

    def test_deepseek_must_be_first_external_model_and_uses_no_system_prompt(self):
        wrong = ReviewSeat("openai", "fixture", "openai", 20)
        local = ReviewSeat("ollama", "deepseek-r1", "deepseek", 10, local=True)
        with self.assertRaises(ForgeTransitionError):
            build_deepseek_work_order(self.session, wrong)
        with self.assertRaises(ForgeTransitionError):
            build_deepseek_work_order(self.session, local)
        pending, order = build_deepseek_work_order(self.session, DEEPSEEK)
        self.assertEqual(pending.stage, ForgeStage.DEEPSEEK_PENDING)
        self.assertEqual([item.role for item in order.messages], ["user"])
        self.assertNotIn("never-route-this", order.messages[0].content)
        self.assertIn("SCRUBBED_DERIVATIVE", order.messages[0].content)
        self.assertEqual(order.status_authority, "NONE")

    def test_return_must_match_exact_pending_seat_and_structured_schema(self):
        pending, order = build_deepseek_work_order(self.session, DEEPSEEK)
        different_deepseek = ReviewSeat(
            "deepseek",
            "deepseek-reasoner",
            "deepseek",
            10,
        )
        with self.assertRaises(ForgeTransitionError):
            record_deepseek_review(
                pending,
                different_deepseek,
                FIRST_OUTPUT,
            )
        with self.assertRaises(ValueError):
            record_deepseek_review(
                pending,
                DEEPSEEK,
                '{"claims":[]}',
            )
        recorded = record_deepseek_review(
            pending,
            DEEPSEEK,
            FIRST_OUTPUT,
        )
        self.assertEqual(recorded.stage, ForgeStage.DEEPSEEK_RECORDED)
        self.assertEqual(recorded.deepseek_review.work_order_id, order.work_order_id)
        self.assertEqual(recorded.deepseek_review.semantic_class, "PROPOSAL")
        self.assertEqual(recorded.deepseek_review.status_authority, "NONE")

    def test_duplicate_review_keys_are_rejected_instead_of_last_wins(self):
        pending, _ = build_deepseek_work_order(self.session, DEEPSEEK)
        duplicate = (
            '{"record_boundaries":[],"tags":[],"claims":[],'
            '"privacy_flags":[],"non_claims":[],"claims":["smuggled"]}'
        )
        with self.assertRaisesRegex(ValueError, "duplicate review key"):
            record_deepseek_review(pending, DEEPSEEK, duplicate)

    def test_second_model_must_be_nonlocal_distinct_family_and_higher_rank(self):
        session, _ = build_deepseek_work_order(self.session, DEEPSEEK)
        session = record_deepseek_review(session, DEEPSEEK, FIRST_OUTPUT)
        same_family = ReviewSeat("other", "fixture", "deepseek", 30)
        local = ReviewSeat("ollama", "qwen", "qwen", 30, local=True)
        lower = ReviewSeat("anthropic", "fixture", "anthropic", 10)
        for invalid in (same_family, local, lower):
            with self.subTest(seat=invalid.seat_id):
                with self.assertRaises(ForgeTransitionError):
                    build_second_review_work_order(session, invalid)
        pending, order = build_second_review_work_order(session, SECOND)
        self.assertEqual(pending.stage, ForgeStage.SECOND_REVIEW_PENDING)
        self.assertEqual(order.prior_review_sha256, session.deepseek_review.output_sha256)
        self.assertIn("UNTRUSTED_DEEPSEEK_PROPOSAL", order.messages[0].content)
        recorded = record_second_review(pending, SECOND, SECOND_OUTPUT)
        self.assertEqual(recorded.stage, ForgeStage.SECOND_REVIEW_RECORDED)
        self.assertNotEqual(
            recorded.deepseek_review.seat.family_id,
            recorded.second_review.seat.family_id,
        )

    def test_model_review_secrets_are_scrubbed_before_persistence(self):
        pending, _ = build_deepseek_work_order(self.session, DEEPSEEK)
        output = json.dumps(
            {
                "record_boundaries": [],
                "tags": [],
                "claims": [],
                "privacy_flags": [
                    "API_KEY=model-invented-secret-value",
                ],
                "non_claims": [],
            }
        )
        recorded = record_deepseek_review(pending, DEEPSEEK, output)
        self.assertNotIn(
            "model-invented-secret-value",
            recorded.deepseek_review.canonical_json,
        )
        self.assertIn("[REDACTED]", recorded.deepseek_review.canonical_json)


class ValidationAndCommitProposalTests(unittest.TestCase):
    def test_validation_keeps_models_proposal_only_and_raw_out(self):
        raw = "API_KEY=private-value\noperator: useful line"
        session = validated_pipeline(raw)
        self.assertEqual(session.stage, ForgeStage.VALIDATED)
        self.assertTrue(session.validation.passed)
        candidate = render_forge_candidate(session)
        payload = json.loads(candidate)
        self.assertEqual(payload["artifact_kind"], "SCRUBBED_DERIVATIVE")
        self.assertFalse(payload["source"]["raw_included"])
        self.assertNotIn("private-value", candidate)
        self.assertEqual(payload["status_authority"], "NONE")
        self.assertTrue(
            all(
                review["semantic_class"] == "PROPOSAL"
                for review in payload["reviews"]
            )
        )

    def test_commit_is_only_an_exact_explicit_inert_proposal(self):
        session = validated_pipeline()
        with self.assertRaises(ForgeTransitionError):
            make_commit_proposal(
                session,
                target_path="corpus/session.json",
                approval_ref="commit-approval",
                expected_candidate_sha256="stale",
            )
        proposed, proposal = make_commit_proposal(
            session,
            target_path="corpus/session.json",
            approval_ref="commit-approval",
            expected_candidate_sha256=session.validation.candidate_sha256,
        )
        self.assertEqual(proposed.stage, ForgeStage.COMMIT_PROPOSED)
        self.assertFalse(proposal.contains_raw)
        self.assertFalse(proposal.execution_available)
        self.assertTrue(proposal.requires_separate_execution_approval)
        self.assertEqual(proposal.requested_operations, ("git.add", "git.commit"))
        with self.assertRaises(CommitExecutionUnavailable):
            execute_commit(proposal)

    def test_commit_target_is_bounded_and_public_commons_is_default_off(self):
        session = validated_pipeline()
        with self.assertRaises(ValueError):
            make_commit_proposal(
                session,
                target_path="../../outside.md",
                approval_ref="approval",
                expected_candidate_sha256=session.validation.candidate_sha256,
            )
        with self.assertRaises(ValueError):
            make_commit_proposal(
                session,
                target_path="corpus/unsafe name.json",
                approval_ref="approval",
                expected_candidate_sha256=session.validation.candidate_sha256,
            )
        with self.assertRaises(ForgeTransitionError):
            make_commit_proposal(
                session,
                target_path="corpus/session.json",
                approval_ref="approval",
                expected_candidate_sha256=session.validation.candidate_sha256,
                public_target=True,
                privacy_review_ref="privacy",
                publish_approval_ref="publish",
            )

    def test_public_proposal_requires_opt_in_license_privacy_and_publish_refs(self):
        policy = CommonsPolicy(opted_in=True, license_id="CC0-1.0")
        session = validated_pipeline(commons_policy=policy)
        with self.assertRaises(ForgeTransitionError):
            make_commit_proposal(
                session,
                target_path="commons/session.json",
                approval_ref="approval",
                expected_candidate_sha256=session.validation.candidate_sha256,
                public_target=True,
                privacy_review_ref="privacy",
            )
        _, proposal = make_commit_proposal(
            session,
            target_path="commons/session.json",
            approval_ref="approval",
            expected_candidate_sha256=session.validation.candidate_sha256,
            public_target=True,
            privacy_review_ref="privacy-review-1",
            publish_approval_ref="publish-approval-1",
        )
        self.assertTrue(proposal.public_target)
        self.assertEqual(proposal.privacy_review_ref, "privacy-review-1")
        self.assertEqual(proposal.publish_approval_ref, "publish-approval-1")

    def test_keep_local_and_discard_are_explicit_non_commit_dispositions(self):
        local = choose_local_disposition(
            validated_pipeline(),
            disposition=ForgeDisposition.KEEP_LOCAL,
            approval_ref="keep-local-approval",
        )
        discarded = choose_local_disposition(
            validated_pipeline(),
            disposition=ForgeDisposition.DISCARD,
            approval_ref="discard-approval",
        )
        self.assertEqual(local.stage, ForgeStage.KEEP_LOCAL)
        self.assertEqual(discarded.stage, ForgeStage.DISCARDED)

    def test_candidate_hash_is_deterministic_for_same_bounded_inputs(self):
        first = validated_pipeline()
        second = validated_pipeline()
        self.assertEqual(
            first.validation.candidate_sha256,
            second.validation.candidate_sha256,
        )
        self.assertEqual(
            render_forge_candidate(first),
            render_forge_candidate(second),
        )


if __name__ == "__main__":
    unittest.main()
