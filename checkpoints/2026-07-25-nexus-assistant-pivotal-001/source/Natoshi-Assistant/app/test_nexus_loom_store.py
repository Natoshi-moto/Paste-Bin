import json
import multiprocessing
import os
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path

from nexus_loom_store import (
    LoomArchiveCryptoError,
    LoomArchiveError,
    LoomSealedArchive,
)


def _append_worker(path: str, key: bytes, index: int) -> None:
    LoomSealedArchive(Path(path), key).append(
        f"worker-{index}".encode("utf-8"),
        session_id=f"worker-session-{index}",
        event_index=1,
        created_at=f"2026-07-25T00:00:{index:02d}+00:00",
    )


class LoomSealedArchiveTests(unittest.TestCase):
    def test_exact_bytes_are_encrypted_hash_linked_and_recoverable(self):
        first_raw = b'{"content":"first\\r\\nline","role":"user"}'
        second_raw = b'{"content":"second","role":"assistant"}'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "loom" / "sessions.jsonl"
            archive = LoomSealedArchive(path, b"k" * 32)
            first = archive.append(
                first_raw,
                session_id="session-1",
                event_index=1,
                created_at="2026-07-25T00:00:00+00:00",
            )
            second = archive.append(
                second_raw,
                session_id="session-1",
                event_index=2,
                created_at="2026-07-25T00:00:01+00:00",
            )

            disk = path.read_bytes()
            records = archive.records()
            self.assertNotIn(first_raw, disk)
            self.assertNotIn(second_raw, disk)
            self.assertEqual(records, (first, second))
            self.assertEqual(second.previous_record_id, first.record_id)
            self.assertEqual(archive.open_record(records[0]), first_raw)
            self.assertEqual(archive.open_record(records[1]), second_raw)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_wrong_key_and_ciphertext_tamper_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sessions.jsonl"
            writer = LoomSealedArchive(path, b"a" * 32)
            record = writer.append(
                b"private bytes",
                session_id="session-1",
                event_index=1,
                created_at="2026-07-25T00:00:00+00:00",
            )
            with self.assertRaises(LoomArchiveCryptoError):
                LoomSealedArchive(path, b"b" * 32).open_record(record)
            tampered = replace(record, ciphertext_sha256="f" * 64)
            with self.assertRaises(LoomArchiveCryptoError):
                writer.open_record(tampered)

    def test_noncanonical_or_truncated_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sessions.jsonl"
            archive = LoomSealedArchive(path, os.urandom(32))
            record = archive.append(
                b"one",
                session_id="session-1",
                event_index=1,
                created_at="2026-07-25T00:00:00+00:00",
            )
            path.write_text(json.dumps(asdict(record), indent=2), encoding="utf-8")
            with self.assertRaises(LoomArchiveError):
                archive.records()

    def test_key_and_record_limits_are_enforced(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(LoomArchiveError):
                LoomSealedArchive(Path(temp) / "x", b"short")
            archive = LoomSealedArchive(Path(temp) / "x", b"k" * 32)
            with self.assertRaises(LoomArchiveError):
                archive.append(
                    b"",
                    session_id="session-1",
                    event_index=1,
                    created_at="now",
                )

    def test_session_event_indexes_must_be_contiguous(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = LoomSealedArchive(
                Path(temp) / "sessions.jsonl",
                b"k" * 32,
            )
            archive.append(
                b"one",
                session_id="session-1",
                event_index=1,
                created_at="now-1",
            )
            with self.assertRaisesRegex(
                LoomArchiveError,
                "next contiguous",
            ):
                archive.append(
                    b"three",
                    session_id="session-1",
                    event_index=3,
                    created_at="now-3",
                )

    def test_cross_process_appends_do_not_lose_or_fork_records(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sessions.jsonl"
            key = b"z" * 32
            context = multiprocessing.get_context("fork")
            workers = [
                context.Process(
                    target=_append_worker,
                    args=(str(path), key, index),
                )
                for index in range(1, 7)
            ]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(timeout=5)
                self.assertEqual(worker.exitcode, 0)

            archive = LoomSealedArchive(path, key)
            records = archive.records()
            self.assertEqual(len(records), 6)
            self.assertEqual(
                [record.sequence for record in records],
                list(range(1, 7)),
            )
            self.assertEqual(
                {
                    archive.open_record(record).decode("utf-8")
                    for record in records
                },
                {f"worker-{index}" for index in range(1, 7)},
            )
