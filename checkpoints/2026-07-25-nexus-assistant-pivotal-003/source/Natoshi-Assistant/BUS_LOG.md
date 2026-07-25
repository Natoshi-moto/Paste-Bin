# Dual-seat bus log

**status_authority:** `NONE`  
**Controller:** Grok via `claude -p`  
**Plan seat:** Claude  
**Human:** operator gate

Significant moments are mirrored to public Paste-Bin.

## ROUND 1 — 2026-07-25

**Goal:** Establish control + wiring map.  
**Mode:** plan/read only.

### Outcome

- ACK dual-seat protocol.
- LIVE (`~/Projects/MatrixTerminal`) behind sandbox checkout (~1400 lines; missing LOOM/Forge/connectors).
- Recommended slice: provenance lock (tests → local commit → public paste → gated relaunch → LOOM falsifier).
- Explicit non-actions without human approval: kill live PID, push Lab, register native host, activate connectors, publish secrets.

### Gates

| Gate | Result |
|---|---|
| App tests | 123 passed |
| Native-host tests | 4 passed |
| Public push policy | Operator ordered Paste-Bin + public significant moments |

## ROUND 2 — pending after public publish

Deploy reconciliation + LOOM seal falsifier (operator gate on process restart).

## PUBLIC MOMENT — pivotal-002 published — 2026-07-25

- Experimental-Sandbox commit `0686bf4` pushed to
  `sandbox/experiment/natoshi-assistant-matrix-terminal`
- Paste-Bin checkpoint `2026-07-25-nexus-assistant-pivotal-002` pushed
- Soft-connect: sandbox app modules rsynced into `~/Projects/MatrixTerminal`
  (backup `MatrixTerminal.pre-connect-20260725-180630`)
- Live PID still running old in-memory code until operator restart
- Publish helper: `Paste-Bin/scripts/publish-checkpoint.sh`
