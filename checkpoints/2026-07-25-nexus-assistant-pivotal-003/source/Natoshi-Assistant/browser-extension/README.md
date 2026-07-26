# NEXUS Browser Organ

Status: working local scaffold; not installed or published.

This Firefox/Chromium extension is a bounded evidence organ for NEXUS
ASSISTANT. It is not a third agent, an authority kernel, a ChatGPT session
scraper, or a place to store API keys.

## What the P0 does

- sends a user-selected excerpt or a user-requested page excerpt to the local
  NEXUS evidence deck;
- accepts a visibly reviewed voice/dictation transcript and parks it as DRAFT;
- retrieves the context packets that the operator explicitly attached to the
  PILOT lane, so they can be reviewed and copied into ChatGPT;
- opens ChatGPT only after the operator clicks `OPEN CHATGPT`; it does not
  inject text, read conversations, or automate the composer;
- talks only to the registered local native-messaging host;
- requests no broad host permission and runs no remote code.

Nothing captured here enters chat automatically. The native host writes a
`nexus.evidence/v1` packet with `status_authority=NONE`. The operator still
chooses `ATTACH NEXT TURN` in the cockpit.

## ChatGPT integration boundary

The extension does not read hidden ChatGPT conversations, borrow login cookies,
or automate private UI internals. The supported handoff is:

1. explicitly capture a page selection into NEXUS;
2. explicitly request already-attached NEXUS context in the popup;
3. review/copy it;
4. paste it into ChatGPT or a supported plugin/MCP surface.

A future ChatGPT plugin should expose typed NEXUS tools over MCP. It should not
depend on DOM scraping.

## Voice boundary

Chromium-family browsers may expose `SpeechRecognition`; the popup uses it only
after the operator presses `START VOICE`. The transcript remains editable and
is not sent until `PARK TRANSCRIPT` is clicked. Firefox currently uses the
editable text fallback in this scaffold. The next production step is a visible
`getUserMedia`/MediaRecorder flow whose audio is sent to a local or Realtime STT
organ through a short-lived session—never an invisible always-listening mic.

## Build

```bash
./build.sh chromium
./build.sh firefox
```

Load the generated directory as an unpacked/temporary extension:

- Chromium: `chrome://extensions` → Developer mode → Load unpacked.
- Firefox: `about:debugging` → This Firefox → Load Temporary Add-on.

Native messaging does not work until its browser-specific manifest is
installed. The Chromium extension ID is assigned by the browser and must be
passed explicitly:

```bash
./install-native-host.sh chromium ACTUAL_EXTENSION_ID
./install-native-host.sh firefox
```

The installer is intentionally not run by the build. Review it first.

## Protocol

Requests are JSON messages framed by the browser native-messaging protocol.
Accepted operations:

- `ping`
- `capture.selection`
- `capture.page`
- `voice.transcript`
- `context.attached`

The host rejects unknown operations, capture URLs outside HTTPS, local files,
and loopback HTTP, secret-like excerpts, oversized fields, and malformed
shapes. It has no shell,
sudo, publishing, provider-key, or arbitrary-file capability.

## Current limitations

- This is not yet packaged or signed for either browser store.
- Context handoff is review/copy, not ChatGPT composer automation.
- Firefox voice capture needs the planned MediaRecorder/STT adapter.
- The cockpit notices external packets when its evidence store refreshes; there
  is not yet a long-lived push channel.
- A Chromium production package should pin a stable extension key/ID before
  generating its native-host allowlist.
