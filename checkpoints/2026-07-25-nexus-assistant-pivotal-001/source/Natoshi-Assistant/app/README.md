# NEXUS ASSISTANT // LINUX BRIDGE

Always-on-top multi-model project cockpit for this Linux workstation.

The rebuilt source is deployed in the active user service. Source/live hashes,
main-window state, ordinary-window stacking, reminder focus isolation, both
global shortcuts, and a local Ollama route have been verified.

## Run

```bash
./launch.sh
# or
python3 matrix_terminal.py
```

## Cockpit map

- **Flight Deck:** mission presets, Model Bay, Command Deck, Project Deck,
  reminders, recent history, and operator memory.
- **Bridge:** routing strip, conversation, always-visible composer, send, stop,
  clear, and search controls.
- **Ship Systems:** model/project telemetry, direct provider/model target,
  project-context controls, private-context guard, and always-on-top control.

The separate Model, Command, and Project deck windows remain topmost with the
main cockpit.

## Controls

| Action | How |
|---|---|
| Drag | Cockpit title bar |
| Resize | Window edges or bottom-right grip |
| Send | `Enter`, `Ctrl+Enter`, or `TRANSMIT` |
| Newline | `Shift+Enter` |
| Stop generation output | `STOP` or `/stop` |
| Show/hide model-emitted thinking | `THINK ON/OFF` or `/thinking on|off` |
| Command Deck | `Ctrl+K` |
| Model Bay | `Ctrl+M` |
| Project Deck | `Ctrl+P` |
| Rescan models/projects | `Ctrl+R` |
| Clear conversation | `Ctrl+L` or `/clear` |
| Minimize | `Esc` |
| Always on top | Ship Systems toggle or `/top` |
| Open/raise from desktop | `Super+Shift+M` or numpad Enter (`KP_Enter`) |
| Open no-echo key entry | `API VAULT` or `/vault` |
| Open Room / Drop / LOOM bay | `/room`, `/drop`, `/loom`, or `/forge` |
| Verify local Room + Drop spine | `/room probe` |
| Encrypted exact-byte history | `/loom on`, `/loom off`, `/loom status` |
| Review current sealed session | `/forge review` |
| Dismiss reminder | Click `[ dismiss ]` or wait 12 seconds |

Reminders appear above normal application windows without taking keyboard
focus, so typing continues in the window you were already using. The duplicate
GNOME notification banner is off by default. Reminders are stored under the
XDG state directory and reloaded after restart.

The live isolation check held active window `0x200003` before and after the
reminder. Its dedicated window reported notification type plus `ABOVE`,
`SKIP_TASKBAR`, and `SKIP_PAGER`.

## Model Bay

The catalogue merges configured direct adapters, live Ollama inventory,
installed agent commands, and local client caches. Its state labels are
deliberately strict:

| State | Routing behavior |
|---|---|
| `READY` | Directly routable; local service answered. |
| `CONFIGURED` | Directly routable, but adapter/key presence is not a successful endpoint probe. |
| `CLIENT` | Visible and launchable through an installed client; not used as a direct chat API. |
| `NEEDS KEY` | Visible but skipped until a credential exists in the private runtime key map. |
| `CACHED` | Catalogue evidence only; skipped. |
| `OFFLINE` | Local service did not answer; skipped. |

Use the selection controls to choose models, then choose a route:

- `solo`: call the first selected direct candidate.
- `failover`: try selected direct candidates in provider order and stop at the
  first successful response.
- `council`: call up to the configured cap of selected direct candidates and
  display each successful response separately.

Council is explicit fan-out, not a free local operation: it can send the same
prompt and project context to several APIs and may incur cost on each.

Failover buffers an attempt until the provider emits a successful completion
signal. Partial text followed by disconnect/error is discarded and cannot win
the route. At the adapter boundary, Ollama requires its `done` marker and
OpenAI-compatible streaming requires `[DONE]` or a finish reason; markerless
EOF is an error in both cases. Council keeps each member's reasoning in a
separate thinking collection and its answer in the answer collection; with
`THINK OFF`, council thinking remains elided rather than being folded into
answer text.

The default provider order is local-first: Ollama, LM Studio, then configured
cloud adapters. The live checkpoint showed 80 catalogue rows, 13 live Ollama
models, and 13 selected direct local models. `dolphin3:8b` returned a live
answer, and history stored the actual Ollama/model route provenance.

## Thinking channel

NEXUS separates model-emitted reasoning from answer text when a provider
returns native `thinking`, `reasoning`, or `reasoning_content` fields. It also
parses common `<think>`, `<thinking>`, `<reasoning>`, `<thought>`, and
`<reasoning_scratchpad>` tags even when a tag is split across stream chunks.

`THINK ON/OFF` and `/thinking on|off` control whether this emitted channel is
visible. They do not force a model to reason, disable provider-side reasoning,
or reveal reasoning a provider does not return. Answer text remains a separate
stream channel in solo, failover, and council modes.

## API Key Vault

Open **API VAULT** or run `/vault`. The provider defaults to DeepSeek when it
is available in config. The capture surface:

- renders no characters, mask bullets, or key length;
- accepts hidden typing, `Ctrl+V`, or `Shift+Insert`;
- wipes its temporary byte buffer when stored or closed;
- stores through `secret-tool` in Linux Secret Service, never config JSON;
- loads Secret Service entries asynchronously after the cockpit opens;
- closes after 120 seconds;
- defaults to adding that provider's models to the pool and setting
  local-first `failover`, with cloud used only if local candidates fail.

Both route options can be unticked before storing. Clipboard clearing after a
hidden paste is on by default, but it cannot erase an entry already retained
by a clipboard manager. Secret Service protects storage at rest; while
callable, the decoded key exists only in NEXUS's private in-process adapter
map—not `os.environ` or child command arguments.

## Project and Command Decks

Project Deck shows live read-only Git metadata, experiment counts, recent
heads, bounded Markdown retrieval, and buttons to open a project folder or
terminal. Retrieved excerpts are untrusted prompt data, not instructions or
authority.

Command Deck launches known commands only after an operator click. Codex,
Claude, Grok, and Hermes open as their own terminal clients; `CLIENT` catalogue
rows are not silently treated as NEXUS API backends. Model output is never
executed as shell input.

## Commands

```text
/help
/models
/vault
/route solo|failover|council
/provider <name>
/model <name>
/agents
/project <query>
/mission BUILD|BREAK|RESEARCH|CHAOS|LAB READ
/recent
/context on|off
/cloud-context on|off
/private-context on|off
/thinking on|off
/search <query>
/room
/room probe
/connectors
/loom on|off|status
/forge review
/remind 10m message
/remind 1h30m message
/remind 14:30 message
/reminders
/cancel [id]
/stop
/top
/opacity 0.9
/clear
/sys <system prompt>
```

## Project-context privacy

Normal local routes may include bounded metadata/excerpts only from roots
enabled for default context. Dynamic project excerpts are blocked for cloud
routes by default; `/cloud-context on` is the explicit opt-in for bounded
public excerpts. Private roots are excluded by default and private excerpts
remain blocked whenever any selected target is non-local.

Cloud requests still need the conversation and base system material to answer.
NEXUS applies secret-pattern redaction to cloud-bound text, but heuristic
redaction is not a substitute for reviewing what is sent.

## Config and state (local, not committed)

- Config: `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/config.json`
- Preferred provider-key entry: **API VAULT** or `/vault`, backed by Linux
  Secret Service
- Environment compatibility: export keys before launch or place them in
  `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/env`
- Legacy key-file compatibility: `~/.config/matrix-terminal.env`
- Operator profile:
  `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/OPERATOR_PROFILE.md`
- State: `${XDG_STATE_HOME:-$HOME/.local/state}/nexus-assistant/`

Recognized compatibility variable names are `XAI_API_KEY`,
`DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`,
`OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, and
`CUSTOM_API_KEY`. Startup captures their values into the private adapter map
and removes the names from the process environment before the UI can launch
child terminals or agents. The live PID audit returned
`provider_secret_env_names=[]`; children therefore cannot inherit those keys.

Do not place secrets in repository files or `config.json`. Environment files
remain supported for compatibility but are plaintext files; Secret Service is
the preferred at-rest path.

The live NEXUS config/state directories are permission mode `0700`, sensitive
files are `0600`, and `launch.sh` starts with `umask 077`.

Set `"system_reminder_notifications": true` in `config.json` only if you also
want GNOME's standard notification banner in addition to the NEXUS overlay.

## Room, Drop, and LOOM

The Room / LOOM bay keeps three different proof shapes separate:

- Room events are Ed25519-signed, ChaCha20-Poly1305-encrypted, strictly
  ordered, and deterministically replayed. Observer/checkpoint signatures are
  scoped evidence, not truth, settlement, consensus, or universal finality.
- Greywire-style Drops use X25519/HKDF, ChaCha20-Poly1305, signed manifests,
  and a local single-successor custody claim. Custody does not make decrypted
  plaintext non-copyable and does not yet transfer the decryption key.
- LOOM is OFF by default. `/loom on` creates or loads a 256-bit archive key
  from Linux Secret Service and stores exact canonical chat-event bytes in a
  `0600`, file-locked, fsynced, encrypted, hash-linked local archive.

`/forge review` first seals an exact current-session snapshot, then presents
the deterministic scrubbed derivative and its hash for explicit privacy
approval. Only that approved derivative may go to external DeepSeek first and
then to a selected nonlocal, distinct-family seat with a higher declared rank.
Both receive user-role work orders and return untrusted proposal JSON. A
validated result can become an inert, exact commit proposal; this build cannot
execute `git add`, commit, push, merge, or publication from that proposal.

Archive path:
`${XDG_STATE_HOME:-$HOME/.local/state}/nexus-assistant/loom/sessions.jsonl`.
The archive key stays in Linux Secret Service. If the key or chain cannot be
verified, capture fails closed; there is no plaintext fallback.

## Live verification

- All 26 unit tests pass: 14 core and 12
  cockpit/provider/reminder/secret-isolation tests.
- Source/live SHA-256:
  - `matrix_terminal.py`:
    `7b5e6ec9eb71cad56e0a0d9f0ac21f7a77b6cb39d9f5d7f8561d3ad104fda1c7`
  - `nexus_core.py`:
    `f266a8c8ca449f60049ebb5feb64b65b3c292be31ecbe671eab943a32bdd06a1`
  - `launch.sh`:
    `69226db9bc1a0ee90b1a321299de95c0a49aaf49a492ac55ede1da21ddece2d2`
- Service: active PID `437515`, `NRestarts=0`; `35,778,560` bytes
  (approximately 34 MB) current and `43,106,304` bytes (approximately 41 MB)
  peak memory.
- Reverified process credential-name audit:
  `provider_secret_env_names=[]`.
- Main window: `WM_CLASS=nexus.Nexus`, Normal, `ABOVE` + `STICKY`,
  `1180x720`.
- Global launcher exits `0`; both **NEXUS Assistant** bindings are installed.
- Live Ollama `dolphin3:8b` response: PASS.

This verifies behavior above ordinary application windows on this desktop. It
does not grant access above the GNOME lock screen or protected shell/security
surfaces. Direct cloud calls remain untested until the operator supplies keys.
