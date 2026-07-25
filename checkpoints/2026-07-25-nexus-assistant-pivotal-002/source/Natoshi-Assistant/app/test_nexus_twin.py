import json
import multiprocessing
import tempfile
import unittest
from pathlib import Path

from nexus_core import ModelRecord
from nexus_twin import (
    EVIDENCE_SCHEMA,
    EvidenceStore,
    build_witness_review_messages,
    distinct_pilot_candidates,
    evidence_packet_from_grep_lines,
    evidence_packet_from_news,
    requires_system_evidence,
    witness_ready,
)


def _child_add_evidence(path: str, query: str) -> None:
    store = EvidenceStore(Path(path))
    store.add(
        evidence_packet_from_grep_lines(
            query,
            [f"/tmp/repo/{query}.py:1:bounded result"],
        )
    )


class EvidencePlaneTests(unittest.TestCase):
    def test_packets_are_parked_until_explicit_attachment(self):
        with tempfile.TemporaryDirectory() as temp:
            store = EvidenceStore(Path(temp) / "evidence.json")
            packet = store.add(
                evidence_packet_from_news(
                    "today",
                    [
                        {
                            "title": "Current source",
                            "url": "https://example.invalid/story",
                            "snippet": "A bounded snippet.",
                        }
                    ],
                )
            )
            self.assertEqual(packet.attachment, "NONE")
            self.assertEqual(store.render_attached("PILOT"), "")
            store.attach(packet.packet_id, "PILOT")
            rendered = store.render_attached("PILOT")
            self.assertIn("Current source", rendered)
            self.assertIn("authority=NONE", rendered)
            self.assertEqual(store.render_attached("WITNESS"), "")

    def test_atomic_store_is_private_and_round_trips(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "evidence.json"
            store = EvidenceStore(path)
            packet = store.add(
                evidence_packet_from_grep_lines(
                    "router",
                    ["/tmp/repo/router.py:12:def route(): pass"],
                )
            )
            store.attach(packet.packet_id, "BOTH")
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema"], EVIDENCE_SCHEMA)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            recovered = EvidenceStore(path)
            self.assertEqual(recovered.attached_count(), 1)
            self.assertIn("router.py:12", recovered.render_attached("PILOT"))
            self.assertIn("router.py:12", recovered.render_attached("WITNESS"))

    def test_secret_like_excerpts_are_redacted(self):
        packet = evidence_packet_from_grep_lines(
            "keys",
            ["/tmp/a.env:1:DEEPSEEK_API_KEY=super-secret-value"],
        )
        self.assertNotIn("super-secret-value", packet.items[0].excerpt)
        self.assertIn("[REDACTED]", packet.items[0].excerpt)

    def test_cross_process_additions_are_not_lost(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "evidence.json"
            context = multiprocessing.get_context("fork")
            workers = [
                context.Process(
                    target=_child_add_evidence,
                    args=(str(path), f"packet_{index}"),
                )
                for index in range(6)
            ]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(timeout=10)
                self.assertEqual(worker.exitcode, 0)
            recovered = EvidenceStore(path)
            self.assertEqual(len(recovered.list()), 6)


class TwinRoutingTests(unittest.TestCase):
    def setUp(self):
        self.witness = ModelRecord(
            key="ollama:qwen3:0.6b",
            provider="ollama",
            model="qwen3:0.6b",
            transport="ollama",
            state="READY",
            source="test",
        )
        self.pilot = ModelRecord(
            key="deepseek:deepseek-chat",
            provider="deepseek",
            model="deepseek-chat",
            transport="openai_compatible",
            state="CONFIGURED",
            source="test",
        )

    def test_required_witness_is_ready_and_not_a_pilot_candidate(self):
        records = [self.witness, self.pilot]
        self.assertTrue(witness_ready(records, "ollama", "qwen3:0.6b"))
        self.assertEqual(
            distinct_pilot_candidates(records, "ollama", "qwen3:0.6b"),
            [self.pilot],
        )

    def test_system_evidence_trigger_is_local_and_conservative(self):
        self.assertTrue(requires_system_evidence("grep my project history"))
        self.assertTrue(requires_system_evidence("inspect this repo implementation"))
        self.assertFalse(requires_system_evidence("give me world news today"))
        self.assertFalse(requires_system_evidence("write a poem"))

    def test_witness_review_is_bounded_and_prompt_free(self):
        messages = build_witness_review_messages(
            "review this",
            "answer",
            "evidence",
        )
        self.assertEqual([item["role"] for item in messages], ["user"])
        self.assertIn("CLEAR:", messages[0]["content"])
        self.assertIn("DISSENT:", messages[0]["content"])
        self.assertNotIn('"role": "system"', messages[0]["content"])


if __name__ == "__main__":
    unittest.main()
