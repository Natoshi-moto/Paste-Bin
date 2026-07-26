# Results — dual-seat bus + public chain

**status_authority:** `NONE`  
**Date (UTC):** 2026-07-25  
**Seats:** Grok (xAI CLI controller) + Claude (sandbox plan seat via `claude -p`)  
**Operator role:** human gate / kill switch  
**Experiment:** `SBX-EXP-NATOSHI-ASSISTANT-001`

## What happened

1. Operator delegated Grok to drive Claude directly (no human copy-paste UI).
2. ROUND 1 bus packet established dual-seat contract and wiring map.
3. Claude audited live vs sandbox divergence; Grok independently re-verified.
4. Full unit gates re-run green.
5. Work committed on Experimental-Sandbox branch and mirrored into public Paste-Bin
   at significant moments under MIT / noncanonical rules.

## Wiring map (verified)

| Layer | State |
|---|---|
| LIVE process | PID observed at `~/Projects/MatrixTerminal` (not a git repo) |
| LIVE modules | `matrix_terminal`, `nexus_core`, `nexus_drop`, `nexus_room`, `nexus_twin` only |
| SANDBOX ahead | LOOM, Forge, Forge runtime, connectors, browser organ, larger cockpit |
| LOOM state dir | `~/.local/state/nexus-assistant/loom/` missing before redeploy |
| Connectors | INERT registry (no sockets/SDKs) |
| Browser organ | Local scaffold; native host not installed |

**Important correction:** connector inertness does **not** mean the cockpit process has no network. Live LLM providers + Ollama probe + search exist in the cockpit.

## Tests at this moment

```text
app/:               123 passed, 52 subtests
browser-extension/: 4 passed
```

## Public chain

| Artifact | Location |
|---|---|
| Working branch | `Experimental-Sandbox` / `sandbox/experiment/natoshi-assistant-matrix-terminal` |
| Public paste | `Paste-Bin` checkpoints `2026-07-25-nexus-assistant-pivotal-*` |

Paste-Bin checkpoints are public backups, not Lab canon and not releases.

## Next connection steps (still reversible)

1. Local commit + public push of sandbox branch (this moment).
2. Paste-Bin pivotal checkpoint capturing bus evidence + current bytes.
3. **[OPERATOR GATE]** Relaunch cockpit from sandbox checkout so LIVE executes LOOM/Forge/connectors code.
4. Falsify: Room → Drop → LOOM seal creates hash-linked archive under XDG state.
5. Browser organ install remains a separate gated moment (writes browser profiles).

## Non-claims

- Not Lab-canonical.
- No secret material published.
- No live connector activation claimed.
- No credentialed cloud Forge run claimed.
- No automatic Git push/merge of private sessions.
