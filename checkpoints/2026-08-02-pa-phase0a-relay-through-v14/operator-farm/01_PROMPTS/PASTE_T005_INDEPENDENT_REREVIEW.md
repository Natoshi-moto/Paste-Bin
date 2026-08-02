# PASTE THIS ENTIRE FILE — T005 / Round 021 independent re-review

You have full access to this PC filesystem. Do not ask me to upload files. Read from disk. Execute end-to-end. Two-terminal rule: you are the only monkey.

You are the **independent** Phase 0A specification re-reviewer.
You did **not** author Round 020. You are **not** the application builder.

══════════════════════════════════════
INPUT
══════════════════════════════════════

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v11.zip
SHA-256: 77d2ae654e770ba7008074edcb0c55fe0bc15021dac010fd2dced0b63ceea044
```

Also at:
```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T004/Pioneer-Alignment-Single-Relay-v11.zip
```

```bash
sha256sum /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v11.zip
mkdir -p /tmp/pa-r021 && cd /tmp/pa-r021
unzip -q /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v11.zip -d relay
cd relay
export PYTHONDONTWRITEBYTECODE=1
```

══════════════════════════════════════
AUTHORITY / READ ORDER
══════════════════════════════════════

1. `00_CONTROL/CURRENT_STATE.json`
2. `00_CONTROL/START_HERE.md`
3. `00_CONTROL/PROMPT_TO_EXECUTE.md`
4. `03_EXCHANGE/ROUND_020_CONTROLLING_PHASE0A_REPAIR/START_HERE.md`
5. `03_EXCHANGE/ROUND_020_CONTROLLING_PHASE0A_REPAIR/REPAIR_SUMMARY.md`
6. `03_EXCHANGE/ROUND_020_CONTROLLING_PHASE0A_REPAIR/REQUEST_FOR_INDEPENDENT_REREVIEW.md`
7. `03_EXCHANGE/ROUND_020_CONTROLLING_PHASE0A_REPAIR/FINDING_CLOSURE.json`
8. `03_EXCHANGE/ROUND_020_CONTROLLING_PHASE0A_REPAIR/MUTATION_RECEIPTS.json`
9. `03_EXCHANGE/ROUND_019_INDEPENDENT_PHASE0A_SPEC_REREVIEW/REVIEW.md` (what R020 was supposed to fix)
10. `01_ORIGINAL_ARTIFACTS/Pioneer-Alignment-Phase-0A-Builder-Handoff-v1.md`

══════════════════════════════════════
REQUIRED EXECUTION
══════════════════════════════════════

From `03_EXCHANGE/ROUND_020_CONTROLLING_PHASE0A_REPAIR/`:

1. `python3 -S meta_validate_round20.py` (full mode) — must document exit code
2. `python3 -S independent_oracle.py`
3. `python3 -S transition_evaluator.py`
4. `python3 -S export_generator.py` and `export_verifier.py`
5. `python3 -S run_round20_mutations.py` with outputs under `/tmp`
6. Re-run mutations under `PYTHONHASHSEED=1` and `2` — receipts must match
7. Run any Round 020 closure probe runner if present (`run_round20_closure_probes.py`)
8. **Invent at least 8 material mutations outside the registry.** Prefer attacks on:
   - deferred cases silently counted as PASS
   - authority strings via unicode / case / synonym evasion
   - raw HTML via encoding, markdown, or alternate fields
   - evidence path symlink/escape if not covered
   - security constants drift via secondary files
   - pycache / bytecode / extraneous files in checksums
   - transition table example deletion / condition constant true
   - coherent removal of deferred floor while claiming candidate eligible
9. Disposable copies only under `/tmp`. Destroy after.

══════════════════════════════════════
HARD QUESTIONS YOU MUST ANSWER
══════════════════════════════════════

1. Are R19-F01..F07 actually closed, or only closed against the known registry?
2. Is DEFERRED honest? Can deferred cases still make `CANDIDATE_TESTS_PASS` / final release?
3. Can you still green the package after injecting public GitHub push / Cloudflare deploy language?
4. Can raw HTML still persist via rename/rewrite games?
5. HOLD still terminal? N80 still bound to reviewed digests?
6. Did Round 020 break export identity or seed stability?

══════════════════════════════════════
WRITE ONLY UNDER
══════════════════════════════════════

```text
03_EXCHANGE/ROUND_021_INDEPENDENT_PHASE0A_SPEC_REREVIEW/**
```

plus control/manifest paths allowed by CURRENT_STATE.json.

Include:
- REVIEW.md
- FINDING_CLOSURE.json
- EXECUTION_RECEIPT.json
- RETURN_SUMMARY.md
- SHA256SUMS.txt
- any probe scripts/receipts you create

Do **not** modify Round 020 package bytes (except via disposable copies for probes).

══════════════════════════════════════
ADJUDICATION — exactly one
══════════════════════════════════════

- `PHASE0A_SPEC_RELEASED_TO_BOUNDED_LOCAL_BUILDER`
- `HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR`
- `INSUFFICIENT_EVIDENCE`

Release only if independent probes fail closed and deferred cannot launder candidate PASS.
Remember: release means **spec → local builder**, NOT deploy, NOT public wallets, NOT economy launch.

══════════════════════════════════════
RETURN
══════════════════════════════════════

Build full relay:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -S 04_TOOLS/build_return_relay.py Pioneer-Alignment-Single-Relay-v12.zip
```

Copy to:
```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T005/Pioneer-Alignment-Single-Relay-v12.zip
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v12.zip
```

Final message:
```text
ADJUDICATION: <token>
ZIP: <path>
SHA256: <detached>
PROBES: <invented N> false_green=<n> rejected=<n>
R19_F01..F07: CLOSED|OPEN each
NOTES: ...
```

No app build, no deploy, no credentials, no network abuse, no public economy.
Start now.
