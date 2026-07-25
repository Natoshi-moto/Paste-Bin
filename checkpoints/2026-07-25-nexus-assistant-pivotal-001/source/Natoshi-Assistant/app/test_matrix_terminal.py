import json
import os
import tempfile
import unittest
from pathlib import Path
from queue import Queue
from threading import BoundedSemaphore, Event
from types import SimpleNamespace
from unittest.mock import Mock, patch

import matrix_terminal
from nexus_core import ModelRecord


class ReminderParserTests(unittest.TestCase):
    def test_compound_relative_reminder(self):
        parsed = matrix_terminal.parse_remind("/remind 1h30m check the ship")
        self.assertIsNotNone(parsed)
        delta, text = parsed
        self.assertEqual(int(delta.total_seconds()), 5400)
        self.assertEqual(text, "check the ship")

    def test_invalid_clock_and_zero_duration_are_rejected(self):
        self.assertIsNone(matrix_terminal.parse_remind("/remind 25:00 impossible"))
        self.assertIsNone(matrix_terminal.parse_remind("/remind 0m impossible"))


class ThinkingTagParserTests(unittest.TestCase):
    def test_split_reasoning_tags_are_captured_separately(self):
        parser = matrix_terminal.ThinkingTagParser()
        self.assertEqual(parser.feed("<thi"), [])
        self.assertEqual(parser.feed("nk>private thought"), [("thinking", "private thought")])
        self.assertEqual(parser.feed("</th"), [])
        self.assertEqual(parser.feed("ink>visible answer"), [("token", "visible answer")])
        self.assertEqual(parser.finish(), [])

    def test_common_reasoning_tag_variants_are_supported(self):
        parser = matrix_terminal.ThinkingTagParser()
        events = parser.feed(
            "<reasoning>one</reasoning><thought>two</thought>answer"
        )
        self.assertEqual(
            events,
            [
                ("thinking", "one"),
                ("thinking", "two"),
                ("token", "answer"),
            ],
        )


class PromptFreeTests(unittest.TestCase):
    def test_defaults_are_prompt_free_and_context_is_opt_in(self):
        self.assertEqual(matrix_terminal.DEFAULT_CONFIG["system_prompt"], "")

    def test_malformed_numeric_config_falls_back_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            config_path = Path(temp) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "config_schema_version": "not-a-number",
                        "opacity": "NaN",
                        "max_http_workers": [],
                        "observer_timeout_seconds": "forever",
                        "twin_review_timeout_seconds": None,
                    }
                ),
                encoding="utf-8",
            )
            legacy_path = Path(temp) / "missing-legacy.json"
            with patch.object(matrix_terminal, "CONFIG_PATH", config_path), patch.object(
                matrix_terminal,
                "LEGACY_CONFIG_PATH",
                legacy_path,
            ):
                cfg = matrix_terminal.load_config()
        self.assertEqual(cfg["opacity"], matrix_terminal.DEFAULT_CONFIG["opacity"])
        self.assertEqual(
            cfg["max_http_workers"],
            matrix_terminal.DEFAULT_CONFIG["max_http_workers"],
        )
        self.assertEqual(cfg["observer_timeout_seconds"], 45)
        self.assertEqual(cfg["twin_review_timeout_seconds"], 45)
        self.assertFalse(matrix_terminal.DEFAULT_CONFIG["project_context"])
        self.assertTrue(matrix_terminal.DEFAULT_CONFIG["clean_transcript"])
        self.assertTrue(matrix_terminal.DEFAULT_CONFIG["startup_compact"])

    def test_all_bundled_legacy_prompts_migrate_to_blank(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            legacy = root / "legacy.json"
            current = root / "current.json"
            for prompt in matrix_terminal.LEGACY_BUILTIN_SYSTEM_PROMPTS:
                with self.subTest(prompt=prompt[:28]):
                    current.unlink(missing_ok=True)
                    legacy.write_text(
                        json.dumps({"system_prompt": prompt}),
                        encoding="utf-8",
                    )
                    with patch.object(
                        matrix_terminal,
                        "LEGACY_CONFIG_PATH",
                        legacy,
                    ), patch.object(
                        matrix_terminal,
                        "CONFIG_PATH",
                        current,
                    ):
                        cfg = matrix_terminal.load_config()
                    self.assertEqual(cfg["system_prompt"], "")
                    persisted = json.loads(current.read_text(encoding="utf-8"))
                    self.assertEqual(persisted["system_prompt"], "")
                    self.assertEqual(
                        persisted["config_schema_version"],
                        matrix_terminal.DEFAULT_CONFIG["config_schema_version"],
                    )
                    self.assertEqual(current.stat().st_mode & 0o777, 0o600)

    def test_custom_prompt_survives_config_loading(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            current = root / "current.json"
            current.write_text(
                json.dumps({"system_prompt": "My explicit operator prompt."}),
                encoding="utf-8",
            )
            with patch.object(
                matrix_terminal,
                "LEGACY_CONFIG_PATH",
                root / "missing-legacy.json",
            ), patch.object(
                matrix_terminal,
                "CONFIG_PATH",
                current,
            ):
                cfg = matrix_terminal.load_config()
        self.assertEqual(cfg["system_prompt"], "My explicit operator prompt.")

    def test_blank_prompt_and_context_off_send_no_system_role(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"system_prompt": "", "max_history_messages": 40}
        assistant.messages = [{"role": "user", "content": "raw question"}]
        messages = assistant._build_request_messages(
            "raw question",
            active_mission="BUILD",
            include_context=False,
            include_private=False,
            cloud_route=False,
        )
        self.assertEqual(
            messages,
            [{"role": "user", "content": "raw question"}],
        )

    def test_only_explicit_prompt_creates_system_role_when_context_is_off(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {
            "system_prompt": "My explicit operator prompt.",
            "max_history_messages": 40,
        }
        assistant.messages = [{"role": "user", "content": "raw question"}]
        messages = assistant._build_request_messages(
            "raw question",
            active_mission="BUILD",
            include_context=False,
            include_private=False,
            cloud_route=False,
        )
        self.assertEqual(
            messages[0],
            {"role": "system", "content": "My explicit operator prompt."},
        )
        self.assertEqual(messages[1]["role"], "user")

    def test_explicit_project_context_is_user_attachment_not_system_prompt(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"system_prompt": "", "max_history_messages": 40}
        assistant.messages = [{"role": "user", "content": "raw question"}]
        assistant.project_index = SimpleNamespace(
            context_for=lambda *_args, **_kwargs: "project-index-context"
        )
        with patch.object(
            matrix_terminal,
            "read_operator_profile",
            return_value="operator-profile-context",
        ), patch.object(
            matrix_terminal,
            "read_project_memory",
            return_value="project-memory-context",
        ):
            messages = assistant._build_request_messages(
                "raw question",
                active_mission="BUILD",
                include_context=True,
                include_private=False,
                cloud_route=False,
            )
        self.assertEqual([item["role"] for item in messages], ["user", "user"])
        self.assertIn("EXPLICIT CONTEXT ATTACHMENT", messages[0]["content"])
        self.assertIn("operator-profile-context", messages[0]["content"])
        self.assertIn("project-memory-context", messages[0]["content"])
        self.assertIn("project-index-context", messages[0]["content"])
        self.assertEqual(messages[1]["content"], "raw question")

    def test_explicit_prompt_stays_separate_from_context_attachment(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {
            "system_prompt": "My explicit operator prompt.",
            "max_history_messages": 40,
        }
        assistant.messages = [{"role": "user", "content": "raw question"}]
        assistant.project_index = SimpleNamespace(
            context_for=lambda *_args, **_kwargs: "project-index-context"
        )
        with patch.object(
            matrix_terminal,
            "read_operator_profile",
            return_value="",
        ), patch.object(
            matrix_terminal,
            "read_project_memory",
            return_value="",
        ):
            messages = assistant._build_request_messages(
                "raw question",
                active_mission="BUILD",
                include_context=True,
                include_private=False,
                cloud_route=False,
            )
        self.assertEqual(
            [item["role"] for item in messages],
            ["system", "user", "user"],
        )
        self.assertEqual(
            messages[0]["content"],
            "My explicit operator prompt.",
        )
        self.assertIn("project-index-context", messages[1]["content"])

    def test_search_results_are_per_turn_user_context_not_system_prompt(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"system_prompt": "", "max_history_messages": 40}
        assistant.messages = [{"role": "user", "content": "current news"}]
        messages = assistant._build_request_messages(
            "current news",
            active_mission="RESEARCH",
            include_context=False,
            include_private=False,
            cloud_route=True,
            request_context="Headline\nhttps://example.invalid",
        )
        self.assertEqual([item["role"] for item in messages], ["user", "user"])
        self.assertIn("WEB SEARCH RESULTS", messages[0]["content"])
        self.assertEqual(messages[1]["content"], "current news")

    def test_twin_evidence_is_ephemeral_user_context_not_history_or_system(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"system_prompt": "", "max_history_messages": 40}
        assistant.messages = [{"role": "user", "content": "inspect the router"}]
        original_history = list(assistant.messages)
        messages = assistant._build_request_messages(
            "inspect the router",
            active_mission="RESEARCH",
            include_context=False,
            include_private=False,
            cloud_route=True,
            evidence_context=(
                "PACKET ev-test | SYSTEM_GREP | authority=NONE\n"
                "excerpt: bounded result"
            ),
        )
        self.assertEqual([item["role"] for item in messages], ["user", "user"])
        self.assertIn("TWIN EVIDENCE PACKETS", messages[0]["content"])
        self.assertIn("authority=NONE", messages[0]["content"])
        self.assertEqual(assistant.messages, original_history)

    def test_setting_and_clearing_prompt_persists_without_history_injection(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"system_prompt": ""}
        assistant.messages = [
            {"role": "system", "content": "legacy"},
            {"role": "user", "content": "question"},
        ]
        statuses = []
        prompt_states = []
        assistant.status_var = SimpleNamespace(set=statuses.append)
        assistant.prompt_state_var = SimpleNamespace(set=prompt_states.append)
        assistant._append = lambda *_args, **_kwargs: None
        with patch.object(matrix_terminal, "save_config") as save, patch.object(
            matrix_terminal,
            "record_action",
        ):
            self.assertTrue(
                assistant._set_system_prompt("My explicit operator prompt.")
            )
            self.assertEqual(
                assistant.cfg["system_prompt"],
                "My explicit operator prompt.",
            )
            self.assertEqual(
                assistant.messages,
                [{"role": "user", "content": "question"}],
            )
            self.assertTrue(assistant._set_system_prompt(""))
        self.assertEqual(assistant.cfg["system_prompt"], "")
        self.assertEqual(prompt_states[-1], "PROMPT ∅")
        self.assertEqual(save.call_count, 2)

    def test_clean_transcript_cannot_change_mid_generation(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.busy = True
        assistant.cfg = {"clean_transcript": True}
        values = {"current": False}
        assistant.clean_transcript_var = SimpleNamespace(
            get=lambda: values["current"],
            set=lambda value: values.__setitem__("current", value),
        )
        statuses = []
        assistant.status_var = SimpleNamespace(set=statuses.append)
        assistant._toggle_clean_transcript()
        self.assertTrue(values["current"])
        self.assertIn("active generation", statuses[-1])


class ResponsiveLayoutTests(unittest.TestCase):
    def test_terminal_first_breakpoint(self):
        self.assertEqual(
            matrix_terminal.layout_mode_for_size(900, 560),
            "terminal",
        )
        self.assertEqual(
            matrix_terminal.layout_mode_for_size(1079, 900),
            "terminal",
        )
        self.assertEqual(
            matrix_terminal.layout_mode_for_size(1400, 619),
            "terminal",
        )
        self.assertEqual(
            matrix_terminal.layout_mode_for_size(1080, 620),
            "cockpit",
        )


class LocalCryptoProbeTests(unittest.TestCase):
    def test_room_drop_and_connector_probe_is_local_and_green(self):
        result = matrix_terminal.run_local_crypto_probe()

        self.assertTrue(result["room_replay"])
        self.assertTrue(result["observer_receipt"])
        self.assertTrue(result["drop_roundtrip"])
        self.assertTrue(result["custody_owner"])
        self.assertEqual(
            result["connector_registry"],
            len(matrix_terminal.CONNECTOR_REGISTRY),
        )
        self.assertEqual(result["connector_violations"], [])

    def test_loom_chat_event_preserves_content_inside_canonical_envelope(self):
        content = "first\r\nsecond\nDEEPSEEK_API_KEY=private-but-encrypted"
        encoded = matrix_terminal.render_loom_chat_event(
            session_id="run-test",
            event_index=1,
            captured_at="2026-07-25T00:00:00+00:00",
            role="user",
            content=content,
        )
        decoded = json.loads(encoded.decode("utf-8"))
        self.assertEqual(decoded["content"], content)
        self.assertEqual(decoded["status_authority"], "NONE")
        self.assertEqual(
            encoded,
            matrix_terminal.canonical_json_bytes(decoded),
        )


class LiveSearchRoutingTests(unittest.TestCase):
    def test_current_public_requests_require_live_search(self):
        for request in (
            "Give me a news story for today",
            "Show me the latest headlines",
            "What is happening in Ukraine right now?",
            "What is the current Bitcoin price?",
            "Search the web for current Linux news",
            "Weather in London today",
        ):
            with self.subTest(request=request):
                self.assertTrue(matrix_terminal.requires_live_web_search(request))

    def test_local_or_non_fresh_requests_do_not_silently_search(self):
        for request in (
            "Show me the latest commits in the Lab",
            "What is the current NEXUS config?",
            "Show the latest changes in my local news-app repo",
            "Write a fictional story set today",
            "Explain what the word news means",
            "How does Bitcoin mining work?",
        ):
            with self.subTest(request=request):
                self.assertFalse(matrix_terminal.requires_live_web_search(request))

    def test_send_routes_fresh_request_without_duplicate_display_or_history(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"auto_live_search": True}
        assistant.input = SimpleNamespace(
            get=lambda *_args: "Give me a news story for today",
            delete=Mock(),
        )
        assistant.busy = False
        assistant.clean_transcript_var = SimpleNamespace(get=lambda: True)
        assistant.context_var = SimpleNamespace(get=lambda: False)
        assistant.status_var = SimpleNamespace(set=Mock())
        assistant.messages = []
        assistant._append = Mock()
        assistant._log_history = Mock()
        assistant._do_search = Mock()
        assistant._start_chat = Mock()

        assistant._send()

        self.assertEqual(
            assistant.messages,
            [{"role": "user", "content": "Give me a news story for today"}],
        )
        assistant._log_history.assert_called_once_with(
            "user",
            "Give me a news story for today",
        )
        assistant._do_search.assert_called_once_with(
            "Give me a news story for today",
            display_and_record=False,
        )
        assistant._start_chat.assert_not_called()

    def test_automatic_search_attaches_timestamped_sources_without_relogging(self):
        class ImmediateThread:
            def __init__(self, target, **_kwargs):
                self.target = target

            def start(self):
                self.target()

        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.clean_transcript_var = SimpleNamespace(get=lambda: True)
        assistant.status_var = SimpleNamespace(set=Mock())
        assistant.commentary_var = SimpleNamespace(set=Mock())
        assistant.messages = [{"role": "user", "content": "today's news"}]
        assistant._append = Mock()
        assistant._log_history = Mock()
        assistant.stream_q = Queue()
        assistant.busy = False
        assistant._observer_cancel = Event()
        assistant._cancel_generation = Event()
        assistant._generation_id = 0

        with patch.object(
            matrix_terminal,
            "web_search",
            return_value=[
                {
                    "title": "Current headline",
                    "url": "https://example.invalid/current",
                    "snippet": "Fresh source",
                }
            ],
        ), patch.object(matrix_terminal.threading, "Thread", ImmediateThread):
            assistant._do_search(
                "today's news",
                display_and_record=False,
            )

        self.assertEqual(
            assistant.messages,
            [{"role": "user", "content": "today's news"}],
        )
        assistant._append.assert_not_called()
        assistant._log_history.assert_not_called()
        events = list(assistant.stream_q.queue)
        self.assertEqual([kind for kind, _payload in events], ["search_ok", "search_chat"])
        context = events[-1][1]["context"]
        self.assertIn("FETCHED AT:", context)
        self.assertIn("SOURCE COUNT: 1", context)
        self.assertIn("https://example.invalid/current", context)

    def test_explicit_search_records_the_operator_query_exactly_once(self):
        class ImmediateThread:
            def __init__(self, target, **_kwargs):
                self.target = target

            def start(self):
                self.target()

        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.clean_transcript_var = SimpleNamespace(get=lambda: True)
        assistant.status_var = SimpleNamespace(set=Mock())
        assistant.commentary_var = SimpleNamespace(set=Mock())
        assistant.messages = []
        assistant._append = Mock()
        assistant._log_history = Mock()
        assistant.stream_q = Queue()
        assistant.busy = False
        assistant._observer_cancel = Event()
        assistant._cancel_generation = Event()
        assistant._generation_id = 0

        with patch.object(
            matrix_terminal,
            "web_search",
            return_value=[
                {
                    "title": "Headline",
                    "url": "https://example.invalid/news",
                    "snippet": "Fresh",
                }
            ],
        ), patch.object(matrix_terminal.threading, "Thread", ImmediateThread):
            assistant._do_search("explicit query")

        self.assertEqual(
            assistant.messages,
            [{"role": "user", "content": "explicit query"}],
        )
        assistant._log_history.assert_called_once_with("user", "explicit query")
        self.assertEqual(assistant._append.call_count, 1)


class ObserverPlaneTests(unittest.TestCase):
    def test_observer_defaults_to_small_local_model(self):
        self.assertTrue(matrix_terminal.DEFAULT_CONFIG["observer_enabled"])
        self.assertEqual(
            matrix_terminal.DEFAULT_CONFIG["observer_provider"],
            "ollama",
        )
        self.assertEqual(
            matrix_terminal.DEFAULT_CONFIG["observer_model"],
            "qwen3:0.6b",
        )
        self.assertLessEqual(
            matrix_terminal.DEFAULT_CONFIG["observer_max_tokens"],
            64,
        )

    def test_observer_request_is_isolated_redacted_and_system_free(self):
        messages = matrix_terminal.build_observer_request_messages(
            "Check this api_key=sk-synthetic1234567890 now",
            "council",
            ["deepseek/deepseek-chat", "ollama/dolphin3:8b"],
        )
        self.assertEqual([message["role"] for message in messages], ["user"])
        content = messages[0]["content"]
        self.assertIn("Route mode: council", content)
        self.assertIn("deepseek/deepseek-chat", content)
        self.assertNotIn("synthetic1234567890", content)
        self.assertNotIn("system prompt", content.lower())
        self.assertNotIn("conversation history", content.lower())

    def test_observer_commentary_is_one_line_and_hides_reasoning_tags(self):
        commentary = matrix_terminal.normalize_observer_commentary(
            "<think>private chain</think>\n"
            "Comparing two route targets while the answer is assembled."
        )
        self.assertEqual(
            commentary,
            "Comparing two route targets while the answer is assembled.",
        )
        self.assertNotIn("\n", commentary)
        self.assertNotIn("private chain", commentary)

    def test_streamed_observer_never_exposes_split_reasoning_content(self):
        parser = matrix_terminal.ObserverCommentaryParser()
        self.assertEqual(parser.feed("<thi"), "")
        self.assertEqual(parser.feed("nk>private chain"), "")
        self.assertEqual(parser.feed("</th"), "")
        self.assertEqual(
            parser.feed("ink>Watching the active route."),
            "Watching the active route.",
        )
        self.assertNotIn("private chain", parser.text)

    def test_streamed_observer_hides_reasoning_tags_with_attributes(self):
        parser = matrix_terminal.ObserverCommentaryParser()
        self.assertEqual(parser.feed("<think data-x="), "")
        self.assertEqual(parser.feed('"1">private chain'), "")
        self.assertEqual(parser.feed("</think>Visible line."), "Visible line.")
        self.assertNotIn("private chain", parser.text)

    def test_observer_endpoint_must_be_local_loopback(self):
        for url in (
            "http://127.0.0.1:11434",
            "http://127.7.8.9:11434",
            "http://localhost:11434",
            "https://[::1]:11434",
        ):
            with self.subTest(url=url):
                self.assertTrue(matrix_terminal.is_loopback_http_url(url))
        for url in (
            "http://192.168.1.7:11434",
            "https://ollama.example.com",
            "file:///tmp/ollama.sock",
            "not-a-url",
        ):
            with self.subTest(url=url):
                self.assertFalse(matrix_terminal.is_loopback_http_url(url))

    def test_post_completion_or_stale_observer_events_are_rejected(self):
        self.assertTrue(matrix_terminal.observer_event_is_current(7, 7, True))
        self.assertFalse(matrix_terminal.observer_event_is_current(7, 7, False))
        self.assertFalse(matrix_terminal.observer_event_is_current(6, 7, True))

    def test_witness_post_review_accepts_only_visible_clear_or_dissent(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {
            "twin_review_enabled": True,
            "observer_provider": "ollama",
            "observer_model": "qwen3:0.6b",
            "twin_review_max_tokens": 96,
            "twin_review_timeout_seconds": 10,
            "providers": {
                "ollama": {
                    "type": "ollama",
                    "base_url": "http://127.0.0.1:11434",
                }
            },
        }
        assistant._witness_review_http_slot = BoundedSemaphore(1)

        def fake_chat(
            _base_url,
            _model,
            messages,
            output,
            _cancel,
            _max_tokens,
            _timeout,
            **_kwargs,
        ):
            self.assertEqual([item["role"] for item in messages], ["user"])
            output.put(("token", "<think>private"))
            output.put(("token", " thought</think>CLEAR: bounded sources match"))
            output.put(("done", None))

        with patch.object(matrix_terminal, "chat_ollama", side_effect=fake_chat):
            review, error = assistant._run_witness_review(
                "question",
                "answer",
                "evidence",
                Event(),
            )
        self.assertEqual(review, "CLEAR: bounded sources match")
        self.assertEqual(error, "")
        self.assertNotIn("private", review)


class ProviderDispatchTests(unittest.TestCase):
    class SyntheticStream:
        def __init__(self, lines):
            self.lines = lines

        def __enter__(self):
            return self

        def __exit__(self, _exc_type, _exc, _traceback):
            return False

        def __iter__(self):
            return iter(self.lines)

    def test_anthropic_and_gemini_use_their_native_adapters(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {
            "providers": {
                "anthropic": {
                    "type": "anthropic",
                    "base_url": "https://anthropic.invalid/v1",
                    "api_key_env": "",
                },
                "gemini": {
                    "type": "gemini",
                    "base_url": "https://gemini.invalid/v1beta",
                    "api_key_env": "",
                },
            }
        }
        messages = [{"role": "user", "content": "synthetic"}]
        output = Queue()
        anthropic = ModelRecord(
            "anthropic:a",
            "anthropic",
            "a",
            "anthropic",
            "CONFIGURED",
            "test",
        )
        gemini = ModelRecord(
            "gemini:g",
            "gemini",
            "g",
            "gemini",
            "CONFIGURED",
            "test",
        )
        with patch.object(matrix_terminal, "chat_anthropic") as anthropic_call:
            assistant._dispatch_model(anthropic, messages, output)
            anthropic_call.assert_called_once()
        with patch.object(matrix_terminal, "chat_gemini") as gemini_call:
            assistant._dispatch_model(gemini, messages, output)
            gemini_call.assert_called_once()

    def test_anthropic_omits_empty_system_field(self):
        output = Queue()
        with patch.object(
            matrix_terminal,
            "http_json",
            return_value={
                "content": [{"type": "text", "text": "answer"}],
            },
        ) as request:
            matrix_terminal.chat_anthropic(
                "https://anthropic.invalid/v1",
                "synthetic-key",
                "synthetic-model",
                [{"role": "user", "content": "question"}],
                output,
            )
        body = request.call_args.kwargs["body"]
        self.assertNotIn("system", body)
        self.assertEqual(
            list(output.queue),
            [("token", "answer"), ("done", None)],
        )

    def test_gemini_omits_empty_system_instruction(self):
        output = Queue()
        with patch.object(
            matrix_terminal,
            "http_json",
            return_value={
                "candidates": [
                    {"content": {"parts": [{"text": "answer"}]}}
                ],
            },
        ) as request:
            matrix_terminal.chat_gemini(
                "https://gemini.invalid/v1beta",
                "synthetic-key",
                "synthetic-model",
                [{"role": "user", "content": "question"}],
                output,
            )
        body = request.call_args.kwargs["body"]
        self.assertNotIn("systemInstruction", body)
        self.assertEqual(
            list(output.queue),
            [("token", "answer"), ("done", None)],
        )

    def test_ollama_forwards_system_free_messages_unchanged(self):
        output = Queue()
        stream = self.SyntheticStream([b'{"message":{},"done":true}\n'])
        with patch.object(
            matrix_terminal.urllib.request,
            "urlopen",
            return_value=stream,
        ) as request:
            matrix_terminal.chat_ollama(
                "http://ollama.invalid",
                "synthetic-model",
                [{"role": "user", "content": "question"}],
                output,
            )
        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual(
            payload["messages"],
            [{"role": "user", "content": "question"}],
        )

    def test_openai_forwards_system_free_messages_unchanged(self):
        output = Queue()
        stream = self.SyntheticStream([b"data: [DONE]\n"])
        with patch.object(
            matrix_terminal.urllib.request,
            "urlopen",
            return_value=stream,
        ) as request:
            matrix_terminal.chat_openai_compatible(
                "https://openai.invalid/v1",
                "synthetic-key",
                "synthetic-model",
                [{"role": "user", "content": "question"}],
                output,
            )
        payload = json.loads(request.call_args.args[0].data)
        self.assertEqual(
            payload["messages"],
            [{"role": "user", "content": "question"}],
        )

    def test_call_model_keeps_native_reasoning_out_of_answer(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"route_attempt_timeout_seconds": 2}
        assistant._http_slots = BoundedSemaphore(1)
        record = ModelRecord(
            "ollama:a",
            "ollama",
            "a",
            "ollama",
            "READY",
            "test",
        )
        seen_answer = []
        seen_thinking = []

        def synthetic_dispatch(_record, _messages, output, _cancel, _timeout):
            output.put(("thinking", "reason"))
            output.put(("token", "answer"))
            output.put(("done", None))

        with patch.object(assistant, "_dispatch_model", synthetic_dispatch):
            answer, error, thinking = assistant._call_model(
                record,
                [{"role": "user", "content": "test"}],
                Event(),
                on_token=seen_answer.append,
                on_thinking=seen_thinking.append,
            )
        self.assertEqual((answer, error, thinking), ("answer", "", "reason"))
        self.assertEqual(seen_answer, ["answer"])
        self.assertEqual(seen_thinking, ["reason"])

    def test_incomplete_partial_response_is_not_accepted(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"route_attempt_timeout_seconds": 2}
        assistant._http_slots = BoundedSemaphore(1)
        record = ModelRecord(
            "ollama:a",
            "ollama",
            "a",
            "ollama",
            "READY",
            "test",
        )

        def synthetic_dispatch(_record, _messages, output, _cancel, _timeout):
            output.put(("token", "partial"))
            output.put(("error", "connection failed"))

        with patch.object(assistant, "_dispatch_model", synthetic_dispatch):
            answer, error, _thinking = assistant._call_model(
                record,
                [{"role": "user", "content": "test"}],
                Event(),
            )
        self.assertEqual(answer, "")
        self.assertIn("connection failed", error)
        self.assertIn("before provider completion", error)

    def test_ollama_markerless_eof_is_an_error(self):
        output = Queue()
        stream = self.SyntheticStream(
            [b'{"message":{"content":"partial"},"done":false}\n']
        )
        with patch.object(
            matrix_terminal.urllib.request,
            "urlopen",
            return_value=stream,
        ):
            matrix_terminal.chat_ollama(
                "http://ollama.invalid",
                "synthetic",
                [{"role": "user", "content": "test"}],
                output,
            )
        events = list(output.queue)
        self.assertEqual(events[0], ("token", "partial"))
        self.assertEqual(
            events[-1],
            ("error", "Ollama stream ended before done marker"),
        )
        self.assertNotIn(("done", None), events)

    def test_openai_markerless_eof_is_an_error(self):
        output = Queue()
        stream = self.SyntheticStream(
            [
                b'data: {"choices":[{"delta":{"content":"partial"},'
                b'"finish_reason":null}]}\n'
            ]
        )
        with patch.object(
            matrix_terminal.urllib.request,
            "urlopen",
            return_value=stream,
        ):
            matrix_terminal.chat_openai_compatible(
                "https://openai.invalid/v1",
                "synthetic-key",
                "synthetic",
                [{"role": "user", "content": "test"}],
                output,
            )
        events = list(output.queue)
        self.assertEqual(events[0], ("token", "partial"))
        self.assertEqual(
            events[-1],
            (
                "error",
                "OpenAI-compatible stream ended before completion marker",
            ),
        )
        self.assertNotIn(("done", None), events)


class SecretIsolationTests(unittest.TestCase):
    def tearDown(self):
        matrix_terminal.RUNTIME_PROVIDER_KEYS.clear()

    def test_compatibility_environment_key_is_removed_from_child_environment(self):
        cfg = {
            "providers": {
                "test": {"api_key_env": "TEST_NEXUS_RUNTIME_SECRET"}
            }
        }
        with patch.dict(
            os.environ,
            {"TEST_NEXUS_RUNTIME_SECRET": "synthetic-secret"},
            clear=False,
        ):
            loaded = matrix_terminal.capture_environment_provider_secrets(cfg)
            self.assertEqual(loaded, 1)
            self.assertNotIn("TEST_NEXUS_RUNTIME_SECRET", os.environ)
            self.assertEqual(
                matrix_terminal.RUNTIME_PROVIDER_KEYS[
                    "TEST_NEXUS_RUNTIME_SECRET"
                ],
                "synthetic-secret",
            )

    def test_keyring_secret_never_enters_process_environment_or_command_args(self):
        cfg = {
            "providers": {
                "test": {"api_key_env": "TEST_NEXUS_KEYRING_SECRET"}
            }
        }
        result = SimpleNamespace(returncode=0, stdout=b"synthetic-secret\n")
        with patch.object(matrix_terminal.shutil, "which", return_value="/secret-tool"):
            with patch.object(
                matrix_terminal.subprocess,
                "run",
                return_value=result,
            ) as run:
                loaded = matrix_terminal.load_keyring_provider_secrets(cfg)
        self.assertEqual(loaded, 1)
        self.assertNotIn("TEST_NEXUS_KEYRING_SECRET", os.environ)
        args = run.call_args.args[0]
        self.assertNotIn("synthetic-secret", args)

    def test_history_redacts_secret_like_content(self):
        assistant = object.__new__(matrix_terminal.NexusAssistant)
        assistant.cfg = {"providers": {}}
        assistant.provider_var = SimpleNamespace(get=lambda: "auto")
        assistant.model_var = SimpleNamespace(get=lambda: "automatic")
        assistant.routing_var = SimpleNamespace(get=lambda: "solo")
        with tempfile.TemporaryDirectory() as temp:
            history = Path(temp) / "history.jsonl"
            with patch.object(matrix_terminal, "HISTORY_PATH", history):
                assistant._log_history(
                    "user",
                    "api_key=sk-synthetic1234567890",
                )
            record = json.loads(history.read_text(encoding="utf-8"))
        self.assertTrue(record["content_redacted"])
        self.assertNotIn("synthetic1234567890", record["content"])


if __name__ == "__main__":
    unittest.main()
