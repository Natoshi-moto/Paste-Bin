import json
import unittest

from nexus_connectors import (
    ApprovalPolicy,
    CommonsPolicy,
    CONNECTOR_REGISTRY,
    ConnectorLayer,
    IngressState,
    InvalidIngressTransition,
    admit_ingress,
    capture_fixture,
    connector_stub,
    make_ingress_route_eligible,
    prepare_fixture_ingress,
    quarantine_ingress,
    record_ingress_evidence,
    render_ingress_for_route,
    validate_registry,
)


class ConnectorRegistryTests(unittest.TestCase):
    def test_registry_contains_every_declared_future_surface(self):
        self.assertTrue(
            {
                "nostr",
                "roomfinal",
                "irc",
                "discord",
                "slack",
                "winmx",
                "bittorrent",
                "mediawiki",
                "github",
                "rss-atom",
                "email",
                "web-search",
                "webhook",
                "greywire-drop",
                "removable-media",
                "codex-app-server",
                "chatgpt-handoff",
                "browser",
                "voice",
                "media",
                "dial-up",
                "ham-radio",
                "starlink",
                "hardened-os-gateway",
                "tails-companion-gateway",
            }.issubset(CONNECTOR_REGISTRY)
        )
        self.assertEqual(validate_registry(), ())

    def test_protocol_bearer_gateway_and_evidence_layers_do_not_collapse(self):
        self.assertEqual(
            connector_stub("nostr").layer,
            ConnectorLayer.APPLICATION_PROTOCOL,
        )
        self.assertEqual(
            connector_stub("dial-up").layer,
            ConnectorLayer.BEARER,
        )
        self.assertEqual(
            connector_stub("starlink").layer,
            ConnectorLayer.BEARER,
        )
        self.assertEqual(
            connector_stub("hardened-os-gateway").layer,
            ConnectorLayer.GATEWAY,
        )
        self.assertEqual(
            connector_stub("roomfinal").layer,
            ConnectorLayer.AUTHORITY_EVIDENCE,
        )
        self.assertIsNone(connector_stub("ham-radio").quarantine)
        self.assertIsNone(connector_stub("hardened-os-gateway").quarantine)

    def test_all_connectors_are_disabled_credential_free_and_non_effectful(self):
        for connector in CONNECTOR_REGISTRY.values():
            with self.subTest(connector=connector.connector_id):
                self.assertFalse(connector.enabled)
                self.assertFalse(connector.accepts_credentials)
                self.assertFalse(connector.auto_start)
                self.assertFalse(connector.background_polling)
                self.assertEqual(connector.live_endpoints, ())
                self.assertEqual(connector.status_authority, "NONE")
                self.assertFalse(
                    any(
                        rule.effectful and rule.implemented
                        for rule in connector.capability_rules
                    )
                )

    def test_high_risk_capabilities_require_human_or_are_forbidden(self):
        nostr = connector_stub("nostr")
        self.assertEqual(
            nostr.capability("nostr.sign").approval,
            ApprovalPolicy.HUMAN_ONLY,
        )
        self.assertEqual(
            nostr.capability("online.send").approval,
            ApprovalPolicy.HUMAN_ONLY,
        )
        self.assertIn(
            "online.send",
            nostr.capability("nostr.publish").requires,
        )
        self.assertEqual(
            connector_stub("roomfinal").capability("roomfinal.settle").approval,
            ApprovalPolicy.FORBIDDEN,
        )
        self.assertEqual(
            connector_stub("winmx").capability("winmx.download").approval,
            ApprovalPolicy.FORBIDDEN,
        )
        self.assertEqual(
            connector_stub("bittorrent").capability("bittorrent.dht").approval,
            ApprovalPolicy.FORBIDDEN,
        )
        self.assertEqual(
            connector_stub("bittorrent").capability("bittorrent.pex").approval,
            ApprovalPolicy.FORBIDDEN,
        )
        self.assertEqual(
            connector_stub("mediawiki").capability("mediawiki.edit").approval,
            ApprovalPolicy.FORBIDDEN,
        )
        self.assertEqual(
            connector_stub("ham-radio").capability("ham-radio.transmit").approval,
            ApprovalPolicy.FORBIDDEN,
        )
        self.assertEqual(
            connector_stub("hardened-os-gateway").capability("gateway.sudo").approval,
            ApprovalPolicy.FORBIDDEN,
        )

    def test_commons_is_deterministic_explicit_opt_in_and_never_raw(self):
        default = CommonsPolicy()
        self.assertFalse(
            default.allows_public_projection(
                "SCRUBBED_DERIVATIVE",
                privacy_review_ref="privacy-1",
                publish_approval_ref="publish-1",
            )
        )
        opted_in = CommonsPolicy(opted_in=True, license_id="CC0-1.0")
        self.assertTrue(
            opted_in.allows_public_projection(
                "SCRUBBED_DERIVATIVE",
                privacy_review_ref="privacy-1",
                publish_approval_ref="publish-1",
            )
        )
        self.assertFalse(opted_in.include_raw)
        self.assertFalse(
            opted_in.allows_public_projection(
                "RAW_VERBATIM",
                privacy_review_ref="privacy-1",
                publish_approval_ref="publish-1",
            )
        )


class ConnectorIngressTests(unittest.TestCase):
    def test_prepare_fixture_stops_before_human_admission(self):
        record = prepare_fixture_ingress(
            "nostr",
            '{"content":"hello","kind":1}',
            content_type="application/json",
            observed_at="2026-07-25T00:00:00+00:00",
        )
        self.assertEqual(record.state, IngressState.SCRUBBED)
        self.assertTrue(record.privacy_review_required)
        self.assertFalse(record.human_approval_ref)
        self.assertFalse(record.evidence_ref)
        self.assertEqual(record.status_authority, "NONE")
        self.assertEqual(
            [item.current for item in record.transitions],
            [
                IngressState.RECEIVED_UNTRUSTED,
                IngressState.LIMITS_VALIDATED,
                IngressState.QUARANTINED,
                IngressState.SOURCE_SIGNAL_CHECKED,
                IngressState.SAFE_DERIVATIVE,
                IngressState.POLICY_CLASSIFIED,
                IngressState.SCRUBBED,
            ],
        )

    def test_secret_scrub_is_fail_closed_before_routing(self):
        secret = "DEEPSEEK_API_KEY=super-secret-value"
        record = prepare_fixture_ingress(
            "irc",
            f"hello\n{secret}",
            content_type="text/plain",
        )
        self.assertEqual(record.state, IngressState.SCRUBBED)
        self.assertNotIn("super-secret-value", record.scrubbed_derivative)
        self.assertIn("[REDACTED]", record.scrubbed_derivative)
        snapshot = json.dumps(record.public_snapshot())
        self.assertNotIn("super-secret-value", snapshot)
        self.assertNotIn("hello", snapshot)

    def test_full_admission_requires_exact_hash_and_explicit_refs(self):
        record = prepare_fixture_ingress("slack", "hello")
        with self.assertRaises(InvalidIngressTransition):
            admit_ingress(
                record,
                approval_ref="operator-approval-1",
                expected_scrubbed_sha256="stale",
            )
        record = admit_ingress(
            record,
            approval_ref="operator-approval-1",
            expected_scrubbed_sha256=record.scrubbed_sha256,
        )
        record = record_ingress_evidence(
            record,
            evidence_ref="REC.20260725.session.0001",
        )
        record = make_ingress_route_eligible(record)
        rendered = json.loads(render_ingress_for_route(record))
        self.assertEqual(record.state, IngressState.ROUTE_ELIGIBLE)
        self.assertEqual(rendered["status_authority"], "NONE")
        self.assertEqual(
            rendered["content_label"],
            "UNTRUSTED_SCRUBBED_DERIVATIVE",
        )
        self.assertEqual(rendered["content"], "hello")

    def test_state_machine_rejects_skipped_stages(self):
        record = capture_fixture("discord", "hello")
        with self.assertRaises(InvalidIngressTransition):
            quarantine_ingress(record)

    def test_invalid_content_type_rejects_and_drops_volatile_bytes(self):
        record = prepare_fixture_ingress(
            "nostr",
            b"binary",
            content_type="application/x-executable",
        )
        self.assertEqual(record.state, IngressState.REJECTED)
        self.assertEqual(record.raw_payload, b"")
        self.assertFalse(record.safe_derivative)
        self.assertFalse(record.scrubbed_derivative)

    def test_media_fixture_is_never_decoded_or_auto_opened(self):
        payload = b"\x89PNG\r\n\x1a\nnot-a-real-image"
        record = prepare_fixture_ingress(
            "media",
            payload,
            content_type="image/png",
        )
        self.assertEqual(record.state, IngressState.SCRUBBED)
        self.assertIn("OPAQUE MEDIA FIXTURE", record.scrubbed_derivative)
        self.assertIn(record.raw_sha256, record.scrubbed_derivative)
        self.assertNotIn("not-a-real-image", record.scrubbed_derivative)

    def test_bittorrent_fixture_is_opaque_and_has_no_network_discovery(self):
        payload = b"d4:infod4:name12:../unsafe.py6:lengthi8eee"
        record = prepare_fixture_ingress(
            "bittorrent",
            payload,
            content_type="application/octet-stream",
        )
        connector = connector_stub("bittorrent")
        self.assertEqual(record.state, IngressState.SCRUBBED)
        self.assertIn("OPAQUE MEDIA FIXTURE", record.scrubbed_derivative)
        self.assertNotIn("../unsafe.py", record.scrubbed_derivative)
        self.assertEqual(connector.live_endpoints, ())
        self.assertEqual(
            connector.capability("bittorrent.private-rendezvous").approval,
            ApprovalPolicy.FORBIDDEN,
        )
        self.assertEqual(
            connector.capability("bittorrent.seed").approval,
            ApprovalPolicy.FORBIDDEN,
        )

    def test_mediawiki_fixture_cannot_edit_or_execute_embedded_content(self):
        record = prepare_fixture_ingress(
            "mediawiki",
            '{"revision_id":7,"content":"{{#invoke:Unsafe|run}}"}',
            content_type="application/json",
        )
        connector = connector_stub("mediawiki")
        self.assertEqual(record.state, IngressState.SCRUBBED)
        self.assertTrue(record.privacy_review_required)
        self.assertFalse(record.human_approval_ref)
        self.assertEqual(
            connector.capability("mediawiki.edit").approval,
            ApprovalPolicy.FORBIDDEN,
        )
        self.assertEqual(
            connector.capability("mediawiki.execute-content").approval,
            ApprovalPolicy.FORBIDDEN,
        )

    def test_bearers_cannot_be_misused_as_payload_parsers(self):
        with self.assertRaises(ValueError):
            capture_fixture("starlink", "application data")
        with self.assertRaises(ValueError):
            capture_fixture("ham-radio", "application data")

    def test_fixture_identity_and_transition_receipts_are_deterministic(self):
        first = prepare_fixture_ingress(
            "github",
            '{"b":2,"a":1}',
            content_type="application/json",
            source_locator="fixture.json",
            observed_at="2026-07-25T00:00:00+00:00",
        )
        second = prepare_fixture_ingress(
            "github",
            '{"b":2,"a":1}',
            content_type="application/json",
            source_locator="fixture.json",
            observed_at="2026-07-25T00:00:00+00:00",
        )
        self.assertEqual(first.ingress_id, second.ingress_id)
        self.assertEqual(first.scrubbed_derivative, '{"a":1,"b":2}')
        self.assertEqual(
            [item.receipt_sha256 for item in first.transitions],
            [item.receipt_sha256 for item in second.transitions],
        )


if __name__ == "__main__":
    unittest.main()
