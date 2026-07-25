# Security and privacy — NEXUS ASSISTANT

**status_authority:** `NONE`
This is a **local single-operator Linux cockpit**, not a hardened multi-user
product, autonomous shell, security product, or Lab control plane.

## Secrets

- The preferred entry path is **API VAULT** (`/vault`). It stores provider keys
  with `secret-tool` in the user's Linux Secret Service collection, not in
  NEXUS config or state JSON.
- The hidden capture area renders no characters, bullets, or length. DeepSeek
  is the default provider choice when configured. It accepts hidden typing or
  paste, wipes its mutable capture buffer on store/close, and closes after 120
  seconds.
- After the cockpit opens, a background loader retrieves available vault
  entries without printing them. Decoded keys live in a private in-process
  adapter map, not `os.environ` or command arguments. Secret Service protects
  the value at rest; a callable key necessarily exists in NEXUS process memory
  while the process is running.
- Clipboard clearing after hidden paste is enabled by default. It clears the
  current clipboard selection, but cannot retroactively erase a clipboard
  manager's history or another application's copy.
- Environment compatibility remains available through these recognized names:
  `XAI_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`,
  `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, and
  `CUSTOM_API_KEY`.
- Optional plaintext compatibility file:
  `${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant/env`.
- The launcher reads legacy `~/.config/matrix-terminal.env` first, then the
  NEXUS file. Both must be permission-restricted, excluded from git, and
  treated as less desirable than Secret Service storage.
- Startup moves compatibility values into the private adapter map with
  `os.environ.pop()` before NEXUS can launch a terminal, agent, folder opener,
  or browser. The reverified live PID `437515` audit returned
  `provider_secret_env_names=[]`; provider secrets are not inherited by child
  processes.
- The live NEXUS config/state directories are `0700`, their current files are
  `0600`, and the launcher sets `umask 077` so newly created history,
  reminder, and receipt files inherit private permissions.
- Do **not** place keys in repository files or `config.json`.
- NEXUS does not render, log, catalogue, copy into prompts, or report a key's
  value or length. This does not eliminate process-memory, swap, debugger,
  compromised-session, or clipboard-manager risk.

## Network

| Path | Default network behavior |
|---|---|
| Ollama | Localhost at `127.0.0.1:11434`. |
| LM Studio | Localhost at `127.0.0.1:1234`. |
| Custom adapter | Configured endpoint; localhost by default. |
| XAI, DeepSeek, OpenAI, Groq, OpenRouter | HTTPS through OpenAI-compatible adapters when configured. |
| Anthropic | HTTPS through the Messages adapter when configured. |
| Gemini | HTTPS through the Generative Language adapter when configured. |
| `/search` | HTTPS to DuckDuckGo HTML. |

Search results, repository excerpts, Git metadata, cached catalogues, and model
responses are **untrusted data**. Their embedded instructions never acquire
authority.

## Model-state truth

- `READY` means a local service answered and the model is directly callable.
- `CONFIGURED` means an adapter and private runtime credential are present; it
  is not proof that the endpoint, account, entitlement, model name, billing,
  or response path works.
- `CLIENT` means an installed client can expose or launch the model; it is not
  a direct NEXUS API.
- `NEEDS KEY`, `CACHED`, and `OFFLINE` rows remain visible but are not routed.

NEXUS does not claim provider identity verification merely because a model
name appears in a config file or client cache.

## Routing, privacy, and cost

- `solo` sends the prompt to one selected direct candidate.
- `failover` is sequential. It sends to the next candidate only after the
  previous candidate fails, and stops after the first successful response.
  Each attempt remains buffered until an explicit provider completion signal;
  partial text followed by error/disconnect is rejected before failover
  advances. Ollama EOF without a `done` marker and OpenAI-compatible EOF
  without `[DONE]` or a finish reason are adapter errors, not successful
  completion. Two adapter-level regressions enforce this silent-drop boundary.
- `council` is explicit parallel fan-out to the selected direct candidates,
  up to the configured cap. It can expose the same chat and project context to
  multiple organizations and incur latency, quota use, or cost at each.
  Each member's emitted reasoning remains separate from its answer; `THINK
  OFF` elides the reasoning tag rather than merging it into answer text.
- Rows in `CLIENT`, `NEEDS KEY`, `CACHED`, or `OFFLINE` state are skipped
  rather than silently substituted.
- The default pool order is local-first (`ollama`, then `lmstudio`, then cloud
  adapters). Vault options default to adding the keyed provider to the pool and
  enabling failover, so cloud is attempted only if earlier local candidates
  fail. The operator can untick either option or explicitly reorder/select
  targets.
- Each model attempt defaults to a 90-second limit and the route to a
  180-second total limit. The Key Vault window has its own 120-second close
  timeout.
- Stopping a generation sets transport cancellation and prevents later output
  from being accepted. Bytes already sent to a provider cannot be recalled,
  and a blocking remote/network layer may take time to notice cancellation.

## Project context

- Project indexing is read-only metadata plus bounded Markdown retrieval.
- Dynamic project excerpts are available to local routes when project context
  is enabled. They are suppressed for cloud routes unless the operator
  explicitly enables `/cloud-context on`.
- Private project roots are excluded by default. Private excerpts are admitted
  only if every routed endpoint is demonstrably loopback/local; any cloud
  candidate suppresses them even when private context is toggled on.
- A cloud request still includes the conversation and core system material
  required to answer. Cloud-bound prompt/history/profile text is passed through
  secret-pattern redaction, but pattern matching cannot guarantee removal of
  every sensitive value.
- “Read-only” here means NEXUS's retrieval path does not write project files;
  opened terminal clients remain separate operator-controlled programs.
- Lab metadata is context, not authority. It cannot promote, merge, or mutate
  Lab state.

## Local data

The XDG state directory can contain:

- `history.jsonl` — chat text and selected model metadata;
- `reminders.json` — pending reminder text and times;
- `window_state.json` — cockpit geometry;
- `actions.jsonl` — explicit launch, route, and context-action receipts.
- `loom/sessions.jsonl` — optional ChaCha20-Poly1305 encrypted, canonical,
  hash-linked exact-byte chat records. Capture is OFF by default.

Treat that directory and `OPERATOR_PROFILE.md` as sensitive operator data.
Keep them out of git and backups that are not trusted.

History records answer content, a content digest, truncation state, selected
provider/model, actual route target/mode, and whether a thinking channel was
emitted. It does not intentionally persist API-key values.

LOOM is a separate opt-in archive. Its 256-bit key is stored through Linux
Secret Service under the NEXUS service/purpose tuple and exists in NEXUS
process memory while capture is active. Records are file-locked, fsynced,
bounded, and permissioned `0600`; the parent directory is `0700`. This protects
at-rest content from an attacker who has the archive but not the unlocked key.
It does not protect against a compromised logged-in session, debugger, swap,
memory inspection, keyring compromise, screen capture of the privacy-review
window, or an authorised recipient copying plaintext.

External LOOM processing is a separate, explicit privacy-review action. It
requires a sealed-record reference, deterministic secret scan, approval bound
to the exact scrubbed hash and provider families, external DeepSeek first, and
a nonlocal distinct-family second seat. The displayed “higher” relation is a
declared routing rank, not a benchmark or proof of capability. Only a scrubbed
derivative is sent; heuristic scanning cannot identify every personal fact, so
the local preview is load-bearing. The resulting model material is DRAFT,
`status_authority=NONE`, and cannot execute a commit or publish.

## Thinking channel

NEXUS separates native provider `thinking`, `reasoning`, and
`reasoning_content` fields from answer tokens. A streaming parser also
separates common reasoning tags across chunk boundaries. `THINK ON/OFF` changes
local visibility; it does not disable provider-side reasoning or prove that
displayed text is a faithful/complete chain of thought. Treat all emitted
thinking as untrusted model output. Council preserves separate thinking and
answer blocks under the same rule.

## Desktop

- Always-on-top can obscure ordinary windows — operator responsibility.
- Reminders use a non-focus-stealing, always-on-top app overlay by default.
- The duplicate `notify-send` path is opt-in with
  `system_reminder_notifications`; it is off by default.
- The overlay does not attempt to cover the lock screen or protected system
  security prompts.
- Live X11/GNOME evidence verified the main Normal window as `ABOVE` and
  `STICKY`, and the isolated reminder as notification type with `ABOVE`,
  `SKIP_TASKBAR`, and `SKIP_PAGER`. The active application window stayed
  `0x200003` throughout the reminder check.
- Those results apply to ordinary application windows on this desktop only.
  GNOME's lock screen and protected shell/security surfaces remain outside
  NEXUS authority.

## Commands and host actions

- Model output is never executed as a shell command.
- Command Deck buttons launch a small set of known installed agent commands or
  project terminals only after an explicit operator click.
- Opening a terminal transfers control to that separate program; NEXUS does
  not sandbox what the operator subsequently does there.
- Provider keys are removed from the NEXUS process environment before any
  child launcher becomes available, so those external programs do not inherit
  them.
- No background API client is treated as permission to modify repositories,
  publish, merge, spend funds, or bypass host security.

## Cancelled machinery (do not revive here)

The operator cancelled “security alarm setup” temporary scripts and related
jobs. This project is a **replacement UX direction** (focus-safe reminders and
the Linux cockpit), not a continuation of that setup.

## Lab boundary

- No Lab credentials.
- No silent Lab writes, commits, pushes, merges, or promotion.
- No submodule into Lab.
- Promotion to Lab requires a separate Promotion Gate package and operator
  `ASK LAB`.
