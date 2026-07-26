import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["NEXUS_ASSISTANT_HOME"] = tempfile.mkdtemp(prefix="nexus-core-test-")

from nexus_core import (
    CommandResult,
    ModelCatalog,
    ModelRecord,
    ProjectIndex,
    ProjectSpec,
    choose_route_candidates,
    classify_intent,
    detect_flow_state_signals,
    initialize_model_selection,
    is_local_endpoint,
    private_context_allowed,
    read_json,
    read_operating_canon,
    redact_sensitive_text,
)


class NexusCoreTests(unittest.TestCase):
    def test_intent_router_prefers_specific_lane(self):
        lane, _instruction = classify_intent("Enter Anti and pressure-test this claim")
        self.assertEqual(lane, "ANTI")

    def test_intent_router_does_not_match_substrings(self):
        for prompt in (
            "make this available",
            "maintain the terminal",
            "add semantic search",
        ):
            lane, _instruction = classify_intent(prompt)
            self.assertEqual(lane, "SANDBOX")

    def test_flow_state_lane_and_signals(self):
        lane, instruction = classify_intent(
            "I'm flow stating a cathedral for RoomFinal ClientFinal dual gate"
        )
        self.assertEqual(lane, "FLOW")
        self.assertIn("RoomFinal", instruction)
        signals = detect_flow_state_signals(
            "this smells off after I flow stated what I wanted"
        )
        self.assertIn("flow_state", signals)
        self.assertIn("smell_alarm", signals)

    def test_operating_canon_loads_roomfinal_and_flow_law(self):
        canon = read_operating_canon()
        self.assertIn("ClientFinal", canon)
        self.assertIn("flow-state", canon.lower())
        self.assertIn("UNABLE_TO_RESOLVE", canon)

    def test_model_catalog_exposes_missing_key_instead_of_hiding_model(self):
        os.environ.pop("TEST_NEXUS_KEY", None)
        catalog = ModelCatalog(
            {
                "providers": {
                    "test": {
                        "type": "openai_compatible",
                        "api_key_env": "TEST_NEXUS_KEY",
                        "models": ["model-a", "model-b"],
                    }
                }
            }
        ).scan()
        direct = [item for item in catalog if item.provider == "test"]
        self.assertEqual([item.model for item in direct], ["model-a", "model-b"])
        self.assertTrue(all(item.state == "NEEDS KEY" for item in direct))

    def test_configured_and_offline_states_are_distinct(self):
        os.environ["TEST_NEXUS_KEY"] = "synthetic-test-key"
        config = {
            "providers": {
                "test": {
                    "type": "openai_compatible",
                    "api_key_env": "TEST_NEXUS_KEY",
                    "models": ["cloud-model"],
                },
                "ollama": {
                    "type": "ollama",
                    "base_url": "http://127.0.0.1:1",
                    "models": [],
                },
            }
        }
        with patch.object(ModelCatalog, "_ollama_models", return_value=[]):
            catalog = ModelCatalog(config).scan()
        configured = next(item for item in catalog if item.provider == "test")
        offline = next(item for item in catalog if item.provider == "ollama")
        self.assertEqual(configured.state, "CONFIGURED")
        self.assertEqual(offline.state, "OFFLINE")
        os.environ.pop("TEST_NEXUS_KEY", None)

    def test_json_reader_rejects_invalid_encoding_and_wrong_shape(self):
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / "cache.json"
            cache.write_bytes(b"\xff\xfe")
            self.assertEqual(
                read_json(cache, {}, expected_type=dict),
                {},
            )
            cache.write_text('["not", "a", "mapping"]', encoding="utf-8")
            self.assertEqual(
                read_json(cache, {}, expected_type=dict),
                {},
            )

    def test_model_catalog_ignores_malformed_cache_shape(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            hermes = home / ".hermes"
            hermes.mkdir()
            (hermes / "provider_models_cache.json").write_text(
                '["not", "a", "provider", "mapping"]',
                encoding="utf-8",
            )
            with (
                patch("nexus_core.HOME", home),
                patch("nexus_core.shutil.which", return_value=None),
            ):
                self.assertEqual(ModelCatalog({"providers": {}}).scan(), [])

    def test_project_context_is_read_only_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index = ProjectIndex((ProjectSpec("fixture", root, "TEST", True),))
            rows = index.scan()
            self.assertEqual(rows[0]["name"], "fixture")
            self.assertIn("fixture", index.context_for("anything"))

    def test_project_scan_marks_failed_git_telemetry_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            index = ProjectIndex(
                (ProjectSpec("fixture", Path(temp), "TEST", True),)
            )
            failed = CommandResult("", 128, "not a git repository")
            with patch("nexus_core.run_command", return_value=failed):
                row = index.scan()[0]

            self.assertEqual(row["dirty"], 0)
            self.assertEqual(row["commits"], 0)
            self.assertEqual(row["scan_status"], "partial")
            self.assertEqual(row["telemetry_status"]["dirty"], "unknown")
            self.assertEqual(row["telemetry_status"]["commits"], "unknown")
            summary = index.summary()
            self.assertIn("commits=unknown", summary)
            self.assertIn("dirty=unknown", summary)

    def test_project_scan_distinguishes_successful_clean_state(self):
        outputs = {
            "branch": "main",
            "log": "2026-07-25T00:00:00Z\tabc123\tfixture",
            "status": "",
            "rev-list": "7",
        }

        def command_result(args, **_kwargs):
            return CommandResult(outputs[args[1]], 0)

        with tempfile.TemporaryDirectory() as temp:
            index = ProjectIndex(
                (ProjectSpec("fixture", Path(temp), "TEST", True),)
            )
            with patch("nexus_core.run_command", side_effect=command_result):
                row = index.scan()[0]

            self.assertEqual(row["dirty"], 0)
            self.assertEqual(row["commits"], 7)
            self.assertEqual(row["scan_status"], "ok")
            self.assertEqual(row["telemetry_status"]["dirty"], "ok")
            self.assertIn("commits=7 dirty=0", index.summary())

    def test_project_scan_survives_experiment_iteration_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "experiments").mkdir()
            index = ProjectIndex((ProjectSpec("fixture", root, "TEST", True),))
            clean = CommandResult("", 0)
            with (
                patch("nexus_core.run_command", return_value=clean),
                patch.object(Path, "iterdir", side_effect=PermissionError("denied")),
            ):
                row = index.scan()[0]

            self.assertEqual(row["experiments"], 0)
            self.assertEqual(row["experiment_names"], [])
            self.assertEqual(row["telemetry_status"]["experiments"], "unknown")
            self.assertEqual(row["scan_status"], "partial")
            self.assertIn("experiments", row["scan_errors"])

    def test_private_project_metadata_is_excluded_by_default(self):
        with tempfile.TemporaryDirectory() as public_temp, tempfile.TemporaryDirectory() as private_temp:
            index = ProjectIndex(
                (
                    ProjectSpec("public-fixture", Path(public_temp), "TEST", True),
                    ProjectSpec(
                        "private-fixture",
                        Path(private_temp),
                        "PRIVATE",
                        False,
                        False,
                    ),
                )
            )
            index.scan()
            public_context = index.context_for("anything")
            private_context = index.context_for("anything", include_private=True)
            self.assertIn("public-fixture", public_context)
            self.assertNotIn("private-fixture", public_context)
            self.assertIn("private-fixture", private_context)

    def test_route_modes_and_private_context_guard(self):
        local = ModelRecord(
            "ollama:a",
            "ollama",
            "a",
            "ollama",
            "READY",
            "test",
        )
        cloud = ModelRecord(
            "deepseek:b",
            "deepseek",
            "b",
            "openai_compatible",
            "READY",
            "test",
        )
        self.assertEqual(choose_route_candidates([local, cloud], "solo"), [local])
        self.assertEqual(
            choose_route_candidates([local, cloud], "failover"),
            [local, cloud],
        )
        self.assertEqual(
            choose_route_candidates(
                [local, cloud],
                "council",
                council_cap=1,
            ),
            [local],
        )
        providers = {
            "ollama": {"base_url": "http://127.0.0.1:11434"},
            "deepseek": {"base_url": "https://api.deepseek.com"},
        }
        self.assertTrue(private_context_allowed([local], providers))
        self.assertFalse(private_context_allowed([local, cloud], providers))
        self.assertTrue(is_local_endpoint("http://[::1]:1234/v1"))
        self.assertFalse(is_local_endpoint("https://example.com/v1"))

    def test_explicit_empty_model_pool_stays_empty(self):
        record = ModelRecord(
            "ollama:a",
            "ollama",
            "a",
            "ollama",
            "READY",
            "test",
        )
        self.assertEqual(
            initialize_model_selection(
                [record],
                set(),
                initialized=True,
            ),
            set(),
        )
        self.assertEqual(
            initialize_model_selection(
                [record],
                set(),
                initialized=False,
            ),
            {"ollama:a"},
        )

    def test_secret_like_excerpt_values_are_redacted(self):
        redacted = redact_sensitive_text(
            'config.json:4:"api_key": "sk-synthetic1234567890"'
        )
        self.assertIn("[REDACTED]", redacted)
        self.assertNotIn("synthetic1234567890", redacted)


if __name__ == "__main__":
    unittest.main()
