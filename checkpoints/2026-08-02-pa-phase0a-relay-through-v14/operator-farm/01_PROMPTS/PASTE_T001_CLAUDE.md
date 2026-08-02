# PASTE THIS ENTIRE FILE INTO CLAUDE (account C1) — T001

You are the **independent** Phase 0A specification re-reviewer for Pioneer Alignment.

You are **not** the author of Round 018. You are **not** the application builder.

## Input

Unpack and use this archive as the only corpus:

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v9.zip
```

Verify SHA-256 first:

```text
d1fa17f84dda2842bd7d3b391ae377bdb570d514c33dcf85f6d8a14381e4d753
```

## Authority

Read:

- `00_CONTROL/START_HERE.md`
- `00_CONTROL/PROMPT_TO_EXECUTE.md`
- `00_CONTROL/CURRENT_STATE.json`
- `00_CONTROL/AUTHORITY.md`
- `03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/START_HERE.md`
- `03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/REPAIR_SUMMARY.md`
- `03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/REQUEST_FOR_INDEPENDENT_REREVIEW.md`
- `03_EXCHANGE/ROUND_017_INDEPENDENT_PHASE0A_BUILD_READINESS/REVIEW.md`

## Required work (Round 019)

1. Verify archive integrity + immutable input manifest (`04_TOOLS/verify_input_manifest.py`).
2. Run Round 018 tools:
   - `python3 -S 03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/meta_validate_round18.py`
   - `python3 -S 03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/independent_oracle.py`
   - `python3 -S 03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/transition_evaluator.py`
   - `python3 -S 03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/export_generator.py`
   - `python3 -S 03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/export_verifier.py`
   - `python3 -S 03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/run_round18_mutations.py --output-json /tmp/r19-mut.json --output-md /tmp/r19-mut.md`
3. Re-run mutations under `PYTHONHASHSEED=1` and `PYTHONHASHSEED=2`; receipts must be byte-identical.
4. Confirm all 20 Round 017 adversarial classes still reject (they are inside the Round 018 mutation registry).
5. Attempt **at least 5 additional** material mutations you invent. If any false-green, HOLD.
6. Decide if HOLD is terminal and N80 cannot release non-reviewed bytes.
7. Preserve external blockers. Do **not** claim host/app/git/remote success.

## Write only under

```text
03_EXCHANGE/ROUND_019_INDEPENDENT_PHASE0A_SPEC_REREVIEW/
```

Include at least:

- `REVIEW.md`
- `FINDING_CLOSURE.json`
- `EXECUTION_RECEIPT.json`
- `RETURN_SUMMARY.md`
- `SHA256SUMS.txt`

Also update control/manifest paths only as `CURRENT_STATE.json` allows, then build:

```text
Pioneer-Alignment-Single-Relay-v10.zip
```

using `04_TOOLS/build_return_relay.py` if you produce a full relay return.

## Adjudication — exactly one

- `PHASE0A_SPEC_RELEASED_TO_BOUNDED_LOCAL_BUILDER`
- `HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR`
- `INSUFFICIENT_EVIDENCE`

## Prohibitions

Do not build the app, mutate repos outside disposable `/tmp` copies, push, deploy, credentials, providers, public wallets, on-chain, DNS, Cloudflare, or spend money.

## Return to operator

Put the zip (or review folder) at:

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T001/
```

Print the detached outer zip SHA-256 in your final message.
