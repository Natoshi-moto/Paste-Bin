# Checkpoint `2026-08-02-pa-phase0a-relay-through-v14`

**Captured:** `2026-08-02T06:53:42+01:00`
**Checkpoint status:** `PUBLIC_BACKUP / NONCANONICAL / NOT_A_RELEASE`
**Status authority:** `NONE`
**Significance:** Pioneer Alignment Phase 0A single-zip relay chain through v14 (Round 023 HOLD). Operator-farm tickets T001–T007 sealed returns + prompts. Not application code; not production deploy; not live NEX/LEX.

| Field | Value |
|---|---|
| Source machine path | `/home/anon/Projects/PA-Release-Prep/operator-farm` + Downloads sealed relays |
| Latest sealed relay | `Pioneer-Alignment-Single-Relay-v14.zip` |
| Latest SHA-256 | `81be0c161051f76eb0f8b49a07db14f1faa106633c68a4ec027ddc282bcc7c54` |
| Latest adjudication | `HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR` (Round 023 independent) |
| Next expected | Round 024 controlling repair → v15 |
| Files in checkpoint | 64 |

## What this is

- Byte snapshots of **sealed** relay zips v9–v14 (complete evolving single-zip corpus).
- Operator-farm control docs, paste prompts, queue tickets, and sealed return zips.
- Evidence that the adversarial gate process is offline-recoverable outside one laptop.

## What this is not

- Project canon or a production release.
- Permission to deploy, issue public wallets, or lift SBX-SOH-001.
- Application implementation of Pioneer-Alignment-App.
- A claim that the Phase 0A gate is builder-ready (it is on HOLD after R023).

## Relay chain (outer zip SHA-256)

```
v9  d1fa17f84dda2842bd7d3b391ae377bdb570d514c33dcf85f6d8a14381e4d753  (if present; verify local)
v10 5c3549431cf38d10a429fe83300fbc73afb8502121a7166df5b2a0b4dbf30e9e
v11 77d2ae654e770ba7008074edcb0c55fe0bc15021dac010fd2dced0b63ceea044
v12 b088ea589ba10af897dea6b7ccc963f620d8bcf5d48bfce3658f6451056adf4a
v13 2bec715b209dc16fef01fab76ac13c3329e61da4f89d6ca320bc4e9c1a68e60b
v14 81be0c161051f76eb0f8b49a07db14f1faa106633c68a4ec027ddc282bcc7c54
```

(Exact digests for each zip also in `relays/*.sha256` and MANIFEST.sha256.)

Verify:

```bash
cd checkpoints/2026-08-02-pa-phase0a-relay-through-v14
sha256sum -c MANIFEST.sha256
```
