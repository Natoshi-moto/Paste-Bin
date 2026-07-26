#!/usr/bin/env python3
"""Native-messaging host for the bounded NEXUS browser evidence organ."""

from __future__ import annotations

import json
import re
import struct
import sys
import ipaddress
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import urlparse

APP_DIR = Path(__file__).resolve().parents[1] / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from nexus_core import redact_sensitive_text  # noqa: E402
from nexus_twin import (  # noqa: E402
    EvidenceItem,
    EvidencePacket,
    EvidenceStore,
)


REQUEST_SCHEMA = "nexus.browser.request/v1"
RESPONSE_SCHEMA = "nexus.browser.response/v1"
MAX_INBOUND_BYTES = 1_000_000
MAX_TEXT_CHARS = 50_000
ALLOWED_OPERATIONS = {
    "ping",
    "capture.selection",
    "capture.page",
    "voice.transcript",
    "context.attached",
}


class ProtocolError(ValueError):
    pass


def _clean_text(value: Any, limit: int) -> str:
    text = str(value or "").replace("\x00", "")
    if len(text) > limit:
        text = text[:limit]
    if redact_sensitive_text(text) != text:
        raise ProtocolError("secret-like content is not accepted by browser capture")
    return text


def _capture_url(value: Any) -> str:
    url = _clean_text(value, 4000)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https", "file"}:
        raise ProtocolError("capture URL must use https, loopback http, or file")
    if parsed.username or parsed.password:
        raise ProtocolError("capture URL may not contain credentials")
    if parsed.scheme == "http":
        hostname = parsed.hostname or ""
        try:
            is_loopback = ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            is_loopback = hostname.lower() == "localhost"
        if not is_loopback:
            raise ProtocolError("plain HTTP capture is limited to loopback")
    return url


def _packet_response(packet: EvidencePacket) -> dict[str, Any]:
    return {
        "schema": RESPONSE_SCHEMA,
        "ok": True,
        "status": "PARKED",
        "packet_id": packet.packet_id,
        "kind": packet.kind,
        "items": len(packet.items),
        "attachment": packet.attachment,
        "status_authority": packet.status_authority,
    }


def handle_message(
    payload: Any,
    *,
    store: EvidenceStore | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProtocolError("request must be a JSON object")
    if payload.get("schema") != REQUEST_SCHEMA:
        raise ProtocolError("unsupported request schema")
    operation = str(payload.get("operation") or "")
    if operation not in ALLOWED_OPERATIONS:
        raise ProtocolError("unsupported operation")
    store = store or EvidenceStore()

    if operation == "ping":
        return {
            "schema": RESPONSE_SCHEMA,
            "ok": True,
            "status": "READY",
            "capabilities": sorted(ALLOWED_OPERATIONS),
        }

    if operation == "context.attached":
        return {
            "schema": RESPONSE_SCHEMA,
            "ok": True,
            "status": "EXPLICIT_CONTEXT",
            "context": store.render_attached("PILOT", max_chars=24_000),
            "packets": store.attached_packet_ids("PILOT"),
            "status_authority": "NONE",
        }

    text = _clean_text(payload.get("text"), MAX_TEXT_CHARS)
    if not text.strip():
        raise ProtocolError("capture text is empty")

    if operation == "voice.transcript":
        item = EvidenceItem.create(
            kind="VOICE_TRANSCRIPT",
            title="Operator-reviewed voice draft",
            locator="browser-microphone:draft",
            excerpt=text,
            retrieved=True,
            inspected=False,
        )
        packet = store.add(
            EvidencePacket.create(
                kind="MANUAL",
                query="voice transcript handoff",
                items=[item],
                exclusions=(
                    "raw audio is not retained",
                    "transcript has no command or approval authority",
                ),
            )
        )
        return _packet_response(packet)

    url = _capture_url(payload.get("url"))
    title = _clean_text(payload.get("title"), 500) or "Browser capture"
    kind = (
        "BROWSER_SELECTION"
        if operation == "capture.selection"
        else "BROWSER_PAGE_EXCERPT"
    )
    item = EvidenceItem.create(
        kind=kind,
        title=title,
        locator=url,
        excerpt=text,
        retrieved=True,
        inspected=False,
    )
    packet = store.add(
        EvidencePacket.create(
            kind="BROWSER",
            query=title,
            items=[item],
            exclusions=(
                "page text is untrusted input",
                "capture was user-triggered",
                "cookies, hidden DOM, and session state were not collected",
            ),
        )
    )
    return _packet_response(packet)


def read_message(stream: BinaryIO) -> dict[str, Any] | None:
    header = stream.read(4)
    if not header:
        return None
    if len(header) != 4:
        raise ProtocolError("truncated native-message header")
    length = struct.unpack("=I", header)[0]
    if length <= 0 or length > MAX_INBOUND_BYTES:
        raise ProtocolError("native message size is outside bounds")
    body = stream.read(length)
    if len(body) != length:
        raise ProtocolError("truncated native-message body")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProtocolError("native message is not valid UTF-8 JSON") from error
    if not isinstance(payload, dict):
        raise ProtocolError("native message must be a JSON object")
    return payload


def write_message(stream: BinaryIO, payload: dict[str, Any]) -> None:
    body = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(body) > MAX_INBOUND_BYTES:
        raise ProtocolError("native response exceeds one megabyte")
    stream.write(struct.pack("=I", len(body)))
    stream.write(body)
    stream.flush()


def main() -> int:
    input_stream = sys.stdin.buffer
    output_stream = sys.stdout.buffer
    while True:
        try:
            message = read_message(input_stream)
            if message is None:
                return 0
            response = handle_message(message)
        except ProtocolError as error:
            response = {
                "schema": RESPONSE_SCHEMA,
                "ok": False,
                "error": str(error),
            }
        except Exception:
            response = {
                "schema": RESPONSE_SCHEMA,
                "ok": False,
                "error": "native host recovered from an internal error",
            }
        write_message(output_stream, response)


if __name__ == "__main__":
    raise SystemExit(main())
