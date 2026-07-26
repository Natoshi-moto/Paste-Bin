# NEXUS Linux cockpit rebuild — audit and verified live deployment

**status_authority:** `NONE`\
**Date:** 2026-07-25 (Europe/London)\
**Seat:** Codex\
**Branch:** `sandbox/experiment/natoshi-assistant-matrix-terminal`\
**Lab touched:** read-only inspection only; no Lab file changed\
**Source checkpoint:** PASS\
**Live deployment / GUI checkpoint:** PASS for the evidence stated below

## Outcome

Natoshi-Assistant's source has been rebuilt from a narrow floating chat overlay
into **NEXUS ASSISTANT // LINUX BRIDGE**, a three-zone cockpit designed around
this workstation:

- an honest merged model catalogue rather than one short provider dropdown;
- explicit solo, failover, and council routing;
- read-only project state and bounded retrieval;
- mission and intent lanes derived from the wider project system;
- direct launch surfaces for Linux terminals and installed agent clients;
- an always-visible composer with stop control;
- a separate thinking channel for native fields and split reasoning tags;
- a no-echo Linux Secret Service API Key Vault;
- a local-first route pool and explicit cloud-context guard;
- persistent, non-focus-stealing reminders;
- XDG config/state paths and local operator/action memory.

The rebuilt cockpit and core are installed in the active user service with
source/live hash parity. The main window, ordinary-window stacking, isolated
reminder focus behavior, global launcher/bindings, service stability, and a
real Ollama route were verified. The limitations section preserves the
remaining shell, cloud, credential, and audit boundaries.

## Audit scope

### Repository history

The reconstruction used complete commit-header chronologies plus selected
current architecture, experiment, handoff, governance, and status documents.
It did not read every historical diff or every file body.

| Repository | Reachable commit headers reviewed |
|---|---:|
| Experimental-Sandbox | 26 |
| Chaos | 3 |
| Anti | 3 |
| Nexus-Foundry | 30 |
| nexus-cognitive-spine | 6 |
| Quantum-Nexus | 66 |
| Advanced-Prompt-Engineering | 78 |
| Sensitive-Safety-Research | 5 |
| Grok | 1 |
| main-ai-desk | 2 |
| nexus-corpus-engine | 2 |
| consensus-foundry | 34 |
| **Twelve non-Lab repositories** | **256** |
| Lab, all local refs | **604** |

The Lab review also covered its root instructions, current status and next
action, evolving constitution, essential skill routing, RAM protocol/board,
urgent disclosures, and the current feature-branch boundary. Lab remained
read-only and its evidence was not treated as product authority.

### Fork and interface patterns

The newest actual GitHub fork found during the audit was
`Natoshi-moto/worldmonitor-hermes-abliterated-agent`, forked from
`koala73/worldmonitor`. Its command palette, mission presets, movable panels,
agent bus, status/freshness telemetry, model/memory documentation, and hybrid
local/cloud boundaries informed the cockpit design. This was pattern reuse,
not wholesale source incorporation or a claim that NEXUS now contains every
World Monitor subsystem.

### Local model and client inventory

The audit inspected live/local catalogue surfaces rather than only hard-coded
names:

- Ollama returned 13 local models at the audit snapshot:
  `obliterated-gemma-65k`, `qwen3-coder-work`, `qwythos-max`,
  `qwable-3.6-27b-abliterated`, `obliterated-gemma:q4`,
  `gemma-fable-stable:q4`, the local Huihui Gemma coder GGUF, `qwythos`,
  `deepseek-r1-14b-24k`, `whiterabbitneo`,
  `deepseek-r1-14b-abliterated`, `deepseek-r1-32b`, and `dolphin3:8b`.
- Hermes caches exposed DeepSeek, Copilot/OpenAI, Anthropic, Gemini, and Ollama
  Cloud catalogue entries.
- Grok's cache exposed Grok model entries.
- `ollama`, `codex`, `claude`, `grok`, and `hermes` commands were installed.
- No direct NEXUS cloud-provider keys were found configured at the audit
  checkpoint, so those direct rows must remain `NEEDS KEY` until local
  configuration changes.

Catalogue presence is not callability. Counts and states are snapshots and
must be rescanned on each live launch.

The verified live scan showed:

- 80 catalogue rows;
- 13 live local models;
- 13 selected direct models;
- 14 project roots;
- 5,825 reachable commits;
- 26 experiment directories.

A real `dolphin3:8b` Ollama request returned an answer, and the persisted
history recorded the actual winning provider/model route rather than only the
dropdown's nominal target.

## Architecture

### `app/matrix_terminal.py`

Owns the Tk cockpit, provider transports, Model/Project/Command Deck windows,
chat orchestration, native/split-tag thinking channels, the no-echo API Key
Vault, web search, reminder UI, persistence, and Linux terminal launching.

### `app/nexus_core.py`

Owns:

- `ModelCatalog` and strict model-state merging;
- route-candidate selection and the private-context guard;
- the 14-root read-only project map, including the World Monitor fork;
- bounded project metadata/Markdown retrieval;
- secret-pattern redaction for retrieved/cloud-bound text;
- intent classification into `LAB READ`, `ANTI`, `CHAOS`, `SANDBOX`, and
  `ADVISE`;
- operator-profile loading and local action receipts.

### Local state

The rebuilt source uses:

- `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/config.json`;
- `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/env`;
- `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/OPERATOR_PROFILE.md`;
- `${XDG_STATE_HOME:-$HOME/.local/state}/nexus-assistant/` for history,
  reminders, window state, and action receipts.

The launch path retains `~/.config/matrix-terminal.env` as a legacy input,
loaded before the NEXUS env file. Recognized compatibility values are captured
into private adapter memory and removed from `os.environ` before child
launchers become available.

The preferred credential path is Linux Secret Service. After the UI starts, an
asynchronous loader uses `secret-tool lookup` without printing results and
places decoded values only in a private in-process adapter map. It does not put
them into environment variables or command arguments.

The verified live config/state directories are mode `0700`, their current
files are mode `0600`, and `launch.sh` sets `umask 077` so future state such
as reminders and action receipts is created privately.

## Cockpit surfaces

### Flight Deck

Provides mission presets, Model Bay, Command Deck, Project Deck, reminders,
recent project history, operator-memory access, and API Vault.

### Bridge

Keeps route mode, conversation, composer, transmit, stop, clear, and search
controls visible in the main window. Native provider thinking and common
`<think>`-style tags use a distinct stream/tag; `THINK ON/OFF` changes local
visibility without mixing that channel into ordinary answer tokens.

### Ship Systems

Shows model/project telemetry, direct provider/model targeting, project-context
state, explicit cloud-context consent, private-context state, thinking
visibility, and always-on-top state.

### Linux Command Deck

Launches Codex, Claude, Grok, or Hermes in the first supported installed
terminal among Ptyxis, Kitty, GNOME Terminal, KGX, and xterm. It also opens
selected project worlds and cockpit surfaces. These are explicit operator
actions; model responses never become shell commands.

### Linux API Key Vault

The vault defaults its provider selector to DeepSeek when available. Hidden
capture shows neither characters, mask bullets, nor key length; it accepts
typing or paste, wipes its mutable capture buffer on store/close, and closes
after 120 seconds. It stores through Linux Secret Service rather than config.

Its checked defaults add the provider's configured models to the pool and set
failover with local providers ordered first. The operator can disable either
option. Clipboard clearing is enabled after hidden paste, but cannot erase
entries already retained by a clipboard-history service. Secret Service
protects at rest; a usable key still exists in the private in-process adapter
map/memory while the adapter is callable.

## Model-state truth

| State | Exact claim |
|---|---|
| `READY` | The local service answered and the named model is directly callable now. |
| `CONFIGURED` | A direct adapter and required credential are present; endpoint/model/account success is not established by this state. |
| `CLIENT` | A relevant installed client can expose or launch the model; NEXUS has not established a direct chat API. |
| `NEEDS KEY` | The direct adapter exists but no credential is present in the private runtime key map. |
| `CACHED` | A local cache/catalogue mentioned the model; callability is unknown. |
| `OFFLINE` | The configured local service did not answer. |

Model Bay keeps unavailable rows visible so the operator can see what exists
and why it is not routable. Only direct `READY` and `CONFIGURED` candidates are
eligible for chat routing.

## Routing behavior

- **Solo:** call the first selected direct candidate.
- **Failover:** try selected direct candidates in configured provider order
  and stop after the first successful response. An attempt remains buffered
  until the provider emits completion; partial text followed by error or
  disconnect is rejected. Ollama EOF without `done`, and OpenAI-compatible EOF
  without `[DONE]` or a finish reason, are explicit adapter errors.
- **Council:** call selected direct candidates concurrently, up to the
  configured cap, and label every successful response. Each member's reasoning
  stays in a separate thinking collection and answer text stays in the answer
  collection; `THINK OFF` elides the former.

`CLIENT`, `NEEDS KEY`, `CACHED`, and `OFFLINE` rows are reported but skipped.
Agent clients are launched in their own terminals rather than impersonated as
direct background APIs.

The default order is Ollama, LM Studio, then configured cloud providers. Each
attempt defaults to 90 seconds and a complete route to 180 seconds. Stop sets
the route/transport cancellation event and rejects late output, but cannot
recall prompt bytes a provider already received.

## Project memory and intent

The Project Deck covers 14 configured roots spanning Lab, Experimental
Sandbox, World Monitor Hermes, Chaos, Anti, Foundry, cognitive-spine, research,
and desk/corpus surfaces. Its verified scan reported 5,825 reachable commits
and 26 experiment directories. It records read-only Git metadata and retrieves
bounded Markdown matches.

Default local prompts may include only roots marked for ordinary context.
Dynamic project excerpts are suppressed for cloud routes unless the operator
explicitly enables cloud context. Private roots remain excluded unless the
operator enables private context, and private excerpts remain suppressed
whenever any selected endpoint is not demonstrably local/loopback.

Cloud routes still receive the conversation and core system material required
to answer. Cloud-bound prompt/history/profile material is passed through
secret-pattern redaction, which reduces risk but is not a proof that every
sensitive phrase can be recognized.

Intent detection adds a bounded instruction lane; it does not silently change
repository authority:

- `LAB READ` explains governed evidence without mutation;
- `ANTI` pressure-tests in public quarantine;
- `CHAOS` works account-wide in reversible lanes;
- `SANDBOX` builds falsifiable experiments;
- `ADVISE` separates observation, inference, pushback, and next action.

## Privacy, cost, and security rules

1. No provider key is stored in tracked source, config JSON, chat history, or
   report output. The preferred vault stores at rest in Linux Secret Service.
   A loaded key exists in a private adapter map/process memory while callable,
   but not in `os.environ` or child command arguments.
2. Web results, repository excerpts, caches, and model output are untrusted
   data.
3. Solo sends to one candidate. Failover may send to several sequentially
   after failures. Council deliberately sends the same request to several
   targets and may create cost at each.
4. Dynamic public project excerpts require explicit cloud-context consent;
   private excerpts are local-only.
5. A stop request and route timeouts bound accepted output, but cannot retract
   data already received by a remote provider.
6. Hidden vault input has no echo, bullets, or rendered length. Clipboard
   clearing cannot retroactively clean a clipboard manager's history.
7. Model-emitted thinking is separated from answer tokens—including council
   output—and can be hidden locally with `THINK OFF`. It remains untrusted
   output and is not guaranteed to be complete or faithful reasoning.
8. Model output is never executed as shell.
9. Command Deck launches known programs only after an operator action; those
   external programs retain their own permissions.
10. NEXUS can remain above ordinary app windows, but cannot cover the lock
    screen or protected GNOME shell/security surfaces.
11. No Lab write, commit, push, merge, promotion, or credential use is implied.

## Source verification

The current source checkpoint is green:

| Check | Result |
|---|---|
| Python syntax/import compilation for cockpit and core | PASS |
| `test_nexus_core.py` | 14 tests PASS |
| `test_matrix_terminal.py` | 12 tests PASS |
| **Unit-test total** | **26 tests PASS** |

The 26 tests cover intent routing and substring safety; catalogue truth and
malformed-cache handling; configured/offline distinction; failed, clean, and
partially unreadable Git telemetry; explicit-empty model-pool preservation;
private-root and local-route guards; secret-like excerpt redaction; reminder
parsing; split/common reasoning tags; native Anthropic/Gemini dispatch; and
separation of native reasoning from answer text. The six hardening regressions
also prove that incomplete partial responses cannot win failover; Ollama and
OpenAI-compatible markerless EOF are rejected; compatibility keys are removed
from the process environment; Secret Service values do not enter environment
variables or command arguments; and history redacts secret-like content.

These source-level tests do not by themselves prove live desktop behavior or
remote-provider availability; the separate evidence below covers the live
claims actually exercised.

## Verified live deployment evidence

### Source/live parity

| File | Source and live SHA-256 |
|---|---|
| `matrix_terminal.py` | `7b5e6ec9eb71cad56e0a0d9f0ac21f7a77b6cb39d9f5d7f8561d3ad104fda1c7` |
| `nexus_core.py` | `f266a8c8ca449f60049ebb5feb64b65b3c292be31ecbe671eab943a32bdd06a1` |
| `launch.sh` | `69226db9bc1a0ee90b1a321299de95c0a49aaf49a492ac55ede1da21ddece2d2` |

### Service and resource state

- `natoshi-assistant.service`: active, PID `437515`;
- `NRestarts=0`;
- `MemoryCurrent=35,778,560` bytes (approximately 34 MB);
- `MemoryPeak=43,106,304` bytes (approximately 41 MB);
- reverified live process credential-name audit:
  `provider_secret_env_names=[]`.

### Main cockpit

- `WM_CLASS`: `nexus.Nexus`;
- window type/state: Normal, `ABOVE`, `STICKY`;
- geometry: `1180x720`.

### Focus-safe reminder

The isolated reminder proof recorded active window `0x200003` both before and
after display. The reminder itself reported notification window type with
`ABOVE`, `SKIP_TASKBAR`, and `SKIP_PAGER`. That establishes non-interruption
and ordinary-window stacking for this desktop session without pretending to
override protected GNOME surfaces.

### Global entry

- the launcher completed with exit status `0`;
- numpad Enter is installed as `KP_Enter`, labeled **NEXUS Assistant**;
- `Super+Shift+M` is installed and labeled **NEXUS Assistant**.

### Live model route

Ollama model `dolphin3:8b` returned a real response. The corresponding history
record persisted the actual provider/model route provenance.

Direct cloud calls were not tested because no user cloud keys were supplied.
Council fan-out remains an explicit operator action with per-provider
privacy/cost implications.

## Claude and GitHub coordination

No active local Claude process was observed at the coordination checkpoint.
The latest material Claude-authored Lab work reviewed was PR #122, whose
executed T-01b result showed that a pop-out/open-tab route could reopen the
same-origin storage boundary. NEXUS therefore treats cross-window shared state
as a security boundary rather than assuming one repaired route closes every
route.

The Claude handoff also disclosed credit exhaustion and a model switch.
Accordingly, later output is not represented as one uninterrupted,
identity-stable Claude seat.

Coordination for this Experimental-Sandbox rebuild was placed on existing PR
#5 (`Natoshi-moto/Experimental-Sandbox`) as one updatable RAM heartbeat,
GitHub comment ID `5078459302`. Reusing one comment avoids fabricating Lab RAM
state and avoids notification spam. This documentation edit does not itself
commit, push, merge, or alter Lab.

## Files in the source rebuild

- `app/matrix_terminal.py` — cockpit and runtime;
- `app/nexus_core.py` — catalogue, routing, projects, intent, receipts;
- `app/test_nexus_core.py` — 14 core tests;
- `app/test_matrix_terminal.py` — twelve
  cockpit/provider/reminder/secret-isolation tests;
- `app/OPERATOR_PROFILE.md` — bundled fallback operator contract;
- active README and security documentation.

## Limitations and non-claims

- Live topmost/focus evidence applies to ordinary application windows on this
  desktop session, not every compositor or future desktop configuration.
- NEXUS cannot cover the GNOME lock screen or protected shell/security
  surfaces.
- Secret Service protects keys at rest, not while loaded in the private
  in-process adapter map/memory.
- Clipboard clearing cannot erase clipboard-manager history that already
  captured a key.
- `CONFIGURED` is not the same as an authenticated successful API call.
- Direct cloud calls were not tested without user-supplied keys.
- Cancellation and timeouts cannot recall prompt bytes already delivered to a
  provider.
- Cached/client model lists can be stale.
- DuckDuckGo HTML parsing remains brittle and search-result prompt injection is
  contained only by trust labeling and prompt boundaries, not a perfect
  sanitizer.
- Project retrieval is bounded text search, not a complete semantic memory of
  every repository file and historical diff.
- The app is a local Experimental-Sandbox prototype, not Lab-canonical,
  independently security-audited, or production hardened.
- The full chronology audit covered every commit header in scope, not every
  repository blob, file body, and historical diff.
- No public commit, push, merge, or Lab promotion is claimed here.
