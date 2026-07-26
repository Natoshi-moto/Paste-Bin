import io
import json
import struct
import tempfile
import unittest
from pathlib import Path

from native_host import (
    ProtocolError,
    REQUEST_SCHEMA,
    handle_message,
    read_message,
    write_message,
)

import sys

APP_DIR = Path(__file__).resolve().parents[1] / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from nexus_twin import EvidenceStore


class NativeHostTests(unittest.TestCase):
    def test_selection_is_parked_and_never_auto_attached(self):
        with tempfile.TemporaryDirectory() as temp:
            store = EvidenceStore(Path(temp) / "evidence.json")
            result = handle_message(
                {
                    "schema": REQUEST_SCHEMA,
                    "operation": "capture.selection",
                    "title": "Example",
                    "url": "https://example.invalid/article",
                    "text": "Selected evidence.",
                },
                store=store,
            )
            self.assertTrue(result["ok"])
            self.assertEqual(result["status"], "PARKED")
            self.assertEqual(store.attached_count(), 0)
            self.assertEqual(store.list()[0].kind, "BROWSER")

    def test_unknown_operations_and_secret_text_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            store = EvidenceStore(Path(temp) / "evidence.json")
            with self.assertRaises(ProtocolError):
                handle_message(
                    {
                        "schema": REQUEST_SCHEMA,
                        "operation": "shell.execute",
                    },
                    store=store,
                )
            with self.assertRaises(ProtocolError):
                handle_message(
                    {
                        "schema": REQUEST_SCHEMA,
                        "operation": "voice.transcript",
                        "text": "api_key=sk-synthetic1234567890",
                    },
                    store=store,
                )

    def test_native_framing_round_trips(self):
        payload = {"schema": REQUEST_SCHEMA, "operation": "ping"}
        raw = json.dumps(payload).encode("utf-8")
        source = io.BytesIO(struct.pack("=I", len(raw)) + raw)
        self.assertEqual(read_message(source), payload)

        target = io.BytesIO()
        write_message(target, {"ok": True})
        target.seek(0)
        length = struct.unpack("=I", target.read(4))[0]
        self.assertEqual(json.loads(target.read(length)), {"ok": True})

    def test_plain_http_capture_is_loopback_only(self):
        with tempfile.TemporaryDirectory() as temp:
            store = EvidenceStore(Path(temp) / "evidence.json")
            with self.assertRaisesRegex(ProtocolError, "loopback"):
                handle_message(
                    {
                        "schema": REQUEST_SCHEMA,
                        "operation": "capture.page",
                        "title": "Unsafe transport",
                        "url": "http://example.invalid/",
                        "text": "Visible page excerpt",
                    },
                    store=store,
                )
            accepted = handle_message(
                {
                    "schema": REQUEST_SCHEMA,
                    "operation": "capture.page",
                    "title": "Local service",
                    "url": "http://127.0.0.1:3000/",
                    "text": "Visible local excerpt",
                },
                store=store,
            )
            self.assertTrue(accepted["ok"])


if __name__ == "__main__":
    unittest.main()
