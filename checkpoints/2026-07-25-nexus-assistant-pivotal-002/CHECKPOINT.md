# NEXUS Assistant pivotal checkpoint 002

**Captured:** `2026-07-25T18:05:54+01:00`  
**Checkpoint status:** `PUBLIC_BACKUP / NONCANONICAL / NOT_A_RELEASE`  
**Status authority:** `NONE`  
**Licence:** MIT, subject to the repository licence and any identified
third-party rights

## Why this moment is significant

Dual-seat control is live (Grok drives Claude via CLI). The NEXUS Assistant
spine is committed on the Experimental-Sandbox branch and re-verified green.
This checkpoint freezes provenance after that commit so the public chain has a
rollback point independent of any single machine or dirty working tree.

## Source state

| Field | Value |
|---|---|
| Source repository | `https://github.com/Natoshi-moto/Experimental-Sandbox` |
| Source subdirectory | `projects/Natoshi-Assistant` |
| Source branch | `sandbox/experiment/natoshi-assistant-matrix-terminal` |
| Source HEAD snapshotted | `0686bf42d1469c6702edcfbb5cf51560ae059b33` |
| Working-tree state | Clean at capture (post-commit) |
| Copied project files | 50 public-safe, non-generated files |
| Prior checkpoint | [`2026-07-25-nexus-assistant-pivotal-001`](../2026-07-25-nexus-assistant-pivotal-001/) (pre-commit dirty snapshot) |

## Material checkpointed

- full NEXUS cockpit + Room/Drop/LOOM/Forge/connectors/twin modules
- browser-extension scaffold (source only; dist excluded)
- dual-seat `BUS_LOG.md` and dual-seat RESULTS note
- design/spec/security/results corpus

## Verification observed before publication

```text
Python app suite:           123 tests passed, 52 subtests
Browser native-host suite:  4 tests passed
Secret-pattern scan:        no credential-like hits on publish surface
```

## Live divergence (honest)

At capture time the running desktop process still used
`~/Projects/MatrixTerminal` and did **not** load LOOM/Forge/connectors.
Redeploy from this tree remains a separate operator-gated step.

## Verify the copied bytes

```bash
sha256sum -c MANIFEST.sha256
```

## Non-claims

- Not Lab canon, not a release, not security certification.
- No live connectors, native-host install, or cloud Forge run claimed.
- No secrets, XDG state, or private transcripts included.
