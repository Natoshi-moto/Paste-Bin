# NEXUS ASSISTANT — Linux project cockpit

**status_authority:** `NONE`\
**Sandbox ID:** `SBX-EXP-NATOSHI-ASSISTANT-001`\
**State:** `LIVE VERIFIED` — source/live parity, compositor, focus, shortcuts, and local route checked\
**Zone:** `sandbox/experiment/*`\
**Branch:** `sandbox/experiment/natoshi-assistant-matrix-terminal`

## One line

An always-on-top, draggable, resizable **Linux bridge** that brings honest
model discovery, explicit multi-model routing, bounded project memory, agent
launchers, web search, and persistent reminders into one cockpit.

## Why this exists

Operator order (verbatim intent): cancel old alarm machinery; ship a mini
terminal that sits on top of everything, is click-draggable and resizable,
Matrix-like, chat + web search, easy reminders — and post it on the live
sandbox so **other AIs can make it better** as **Natoshi-Assistant**.

The first-cut overlay has now been redesigned as **NEXUS ASSISTANT // LINUX
BRIDGE**: a compact spaceship-style control surface built around the way this
Linux workstation, its local models, installed agent clients, and project
repositories actually work.

This is **not** Lab-canonical. This is **not** FORGE. This remains a reversible
Experimental-Sandbox surface.

## Verified cockpit

- Three-zone cockpit: Flight Deck, chat/composer, and Ship Systems.
- Model Bay keeps discovered models visible and labels whether they are
  actually callable.
- `solo`, `failover`, and explicit `council` routing operate only on direct
  candidates in `READY` or `CONFIGURED` state.
- Project Deck presents read-only Git/project metadata and bounded Markdown
  retrieval across the configured project map.
- Command Deck launches known Linux terminals, installed agent clients, and
  selected project roots by explicit operator action.
- Reminders persist under XDG state and use a non-focus-stealing overlay.
- The no-echo API Key Vault stores provider keys in Linux Secret Service.
- Keys are loaded asynchronously into a private in-process adapter map, removed
  from the process environment, and never inherited by launched children.
- Native provider reasoning fields and split `<think>`-style tags are kept
  separate from answer text—including council output—with `THINK ON/OFF`
  display control.
- Failover buffers each attempt and accepts it only after provider completion;
  a partial response cannot win the route. Ollama and OpenAI-compatible
  streams also reject EOF without their completion marker, closing the silent
  connection-drop path.
- Syntax checks and all 26 source unit tests pass.

The same cockpit/core source is installed in the active user service. The live
window, ordinary-window stacking, isolated reminder focus behavior, both global
shortcuts, and an Ollama route were checked on this host. See the rebuild
report for hashes and exact evidence.

## Run from this checkout

```bash
cd projects/Natoshi-Assistant/app
./launch.sh
# or
python3 matrix_terminal.py
```

Needs: Python 3.11+ (3.14 OK), Tkinter, `cryptography` (see
`app/requirements.txt`), Linux Secret Service for encrypted LOOM history/API
vault storage, and optional Ollama at `127.0.0.1:11434`.

## Model truth

The Model Bay deliberately distinguishes discovery from callability:

| State | Meaning |
|---|---|
| `READY` | A local model service answered and the model is directly callable now. |
| `CONFIGURED` | A direct adapter and credential are present; the remote endpoint has not yet been proven by that state alone. |
| `CLIENT` | An installed client can expose or launch the model; NEXUS does not claim a direct API path. |
| `NEEDS KEY` | A direct adapter exists but no credential is present in the private runtime key map. |
| `CACHED` | The model appeared in a local catalogue only; callability is unknown. |
| `OFFLINE` | The configured local service did not answer. |

“Visible” never means “verified,” and selecting a `CLIENT`, `CACHED`,
`NEEDS KEY`, or `OFFLINE` row does not make it directly routable.

## Linux entry points

- Inside the cockpit: `Ctrl+K` Command Deck, `Ctrl+M` Model Bay, `Ctrl+P`
  Project Deck, `Ctrl+R` rescan, and `Esc` minimize.
- The verified desktop bindings are `Super+Shift+M` and numpad Enter
  (`KP_Enter`), both labeled **NEXUS Assistant**.
- Codex, Claude, Grok, and Hermes are opened in a supported terminal
  (`ptyxis`, `kitty`, `gnome-terminal`, `kgx`, or `xterm`) when installed.

## Live snapshot

- Service: active as PID `437515`, `NRestarts=0`; `35,778,560` bytes
  (approximately 34 MB) current and `43,106,304` bytes (approximately 41 MB)
  peak memory.
- Main window: `WM_CLASS=nexus.Nexus`, Normal, `ABOVE` + `STICKY`,
  `1180x720`.
- Model/project telemetry: 80 catalogued models, 13 live local, 13 selected,
  14 repositories, 5,825 reachable commits, and 26 experiment directories.
- Live route: `dolphin3:8b` answered through Ollama and its actual route
  provenance was persisted.
- Source/live SHA-256:
  - `matrix_terminal.py`:
    `7b5e6ec9eb71cad56e0a0d9f0ac21f7a77b6cb39d9f5d7f8561d3ad104fda1c7`
  - `nexus_core.py`:
    `f266a8c8ca449f60049ebb5feb64b65b3c292be31ecbe671eab943a32bdd06a1`
  - `launch.sh`:
    `69226db9bc1a0ee90b1a321299de95c0a49aaf49a492ac55ede1da21ddece2d2`

## Local state

- Config: `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/config.json`
- Optional provider environment compatibility:
  `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/env`
- Operator profile:
  `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/OPERATOR_PROFILE.md`
- History, reminders, window state, and action receipts:
  `${XDG_STATE_HOME:-$HOME/.local/state}/nexus-assistant/`

The launcher still reads the legacy `~/.config/matrix-terminal.env` first for
compatibility, then the NEXUS env file. At startup NEXUS immediately captures
recognized provider values into its private adapter map and removes their
names from `os.environ`; the live service recheck reported
`provider_secret_env_names=[]`. New child terminals/agents therefore do not
inherit provider keys.

Prefer **API VAULT** or `/vault`: it captures without showing characters,
bullets, or length and stores the key in Linux Secret Service instead of
plaintext config. Secret Service loading runs asynchronously after the cockpit
opens. Live NEXUS config/state directories are mode `0700`, sensitive files
are `0600`, and the launcher sets `umask 077`. See
[SECURITY.md](SECURITY.md) for process-memory, clipboard-history, and timeout
boundaries.

## Docs for AI seats (read in order)

1. [`EXPERIMENT.md`](EXPERIMENT.md) — claim, falsifier, non-claims
2. [`HANDOFF_ANY_AI.md`](HANDOFF_ANY_AI.md) — how to improve this safely
3. [`IMPROVE_ME.md`](IMPROVE_ME.md) — ranked backlog other seats can grab
4. [`SECURITY.md`](SECURITY.md) — secrets, network, desktop boundaries
5. [`app/README.md`](app/README.md) — user-facing controls
6. [`RESULTS_2026-07-25.md`](RESULTS_2026-07-25.md) — first cut evidence
7. [`RESULTS_2026-07-25_CODEX_NOTIFICATION_AND_LAB_HISTORY_REVIEW.md`](RESULTS_2026-07-25_CODEX_NOTIFICATION_AND_LAB_HISTORY_REVIEW.md)
   — focus-safe reminder repair, app assessment, and full Lab commit-history review
8. [`RESULTS_2026-07-25_NEXUS_LINUX_COCKPIT_REBUILD.md`](RESULTS_2026-07-25_NEXUS_LINUX_COCKPIT_REBUILD.md)
   — cross-project audit, NEXUS architecture, source/live hashes, and desktop evidence
9. [`NEXUS_ROOM_LOOM_CONNECTIVITY_SPEC.md`](NEXUS_ROOM_LOOM_CONNECTIVITY_SPEC.md)
   — Room/Drop/LOOM schemas, status map, threat model, connector stubs, UX,
   contributor roadmap, and source lineage

## Layout

```text
projects/Natoshi-Assistant/
  README.md
  EXPERIMENT.md
  HANDOFF_ANY_AI.md
  IMPROVE_ME.md
  SECURITY.md
  RESULTS_*.md
  app/
    matrix_terminal.py       # Linux cockpit, providers, search, reminders
    nexus_core.py            # model truth, routing, project context, receipts
    nexus_room.py            # encrypted ordered room and scoped evidence
    nexus_drop.py            # sealed Greywire-style Drops and custody claims
    nexus_connectors.py      # disabled typed connectors + ingress quarantine
    nexus_forge.py           # proposal-only DeepSeek → higher review state
    nexus_forge_runtime.py   # effect-injected ordered model-call bridge
    nexus_loom_store.py      # encrypted hash-linked exact-byte local archive
    OPERATOR_PROFILE.md      # bundled fallback operator contract
    test_matrix_terminal.py  # reminders, routing, thinking, secret isolation
    test_nexus_*.py          # core, twin, Room, Drop, Forge, archive, connectors
    requirements.txt
    launch.sh
    README.md
```

## Authority

`status_authority: NONE`\
Nothing here merges into Nexus Lab without a separate Promotion Gate package.\
No secrets in git. No Lab credentials. No automatic promotion.
