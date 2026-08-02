# PASTE THIS ENTIRE FILE — T007 / Round 023 independent re-review

You have full access to this PC filesystem. Do not ask me to upload files. Read from disk. Execute end-to-end. Two-terminal rule: you are the only monkey.

You are the **independent** Phase 0A specification re-reviewer.
You did **not** author Round 022. You are **not** the application builder.
No deploy, push, credentials, providers, DNS/Cloudflare, public wallets, on-chain, or app build.

══════════════════════════════════════
INPUT
══════════════════════════════════════

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v13.zip
SHA-256: 2bec715b209dc16fef01fab76ac13c3329e61da4f89d6ca320bc4e9c1a68e60b
```

Also at:
```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T006/Pioneer-Alignment-Single-Relay-v13.zip
```

```bash
sha256sum /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v13.zip
# must equal 2bec715b209dc16fef01fab76ac13c3329e61da4f89d6ca320bc4e9c1a68e60b

rm -rf /tmp/pa-r023-work
mkdir -p /tmp/pa-r023-work && cd /tmp/pa-r023-work
unzip -q /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v13.zip -d relay
cd relay
export PYTHONDONTWRITEBYTECODE=1
```

══════════════════════════════════════
READ
══════════════════════════════════════

1. 00_CONTROL/CURRENT_STATE.json
2. 00_CONTROL/START_HERE.md
3. 00_CONTROL/PROMPT_TO_EXECUTE.md
4. 03_EXCHANGE/ROUND_022_CONTROLLING_PHASE0A_REPAIR/START_HERE.md
5. 03_EXCHANGE/ROUND_022_CONTROLLING_PHASE0A_REPAIR/REPAIR_SUMMARY.md
6. 03_EXCHANGE/ROUND_022_CONTROLLING_PHASE0A_REPAIR/REQUEST_FOR_INDEPENDENT_REREVIEW.md
7. 03_EXCHANGE/ROUND_022_CONTROLLING_PHASE0A_REPAIR/RETURN_SUMMARY.md
8. 03_EXCHANGE/ROUND_022_CONTROLLING_PHASE0A_REPAIR/FINDING_CLOSURE.json
9. 03_EXCHANGE/ROUND_022_CONTROLLING_PHASE0A_REPAIR/MUTATION_RECEIPTS.json
10. 03_EXCHANGE/ROUND_021_INDEPENDENT_PHASE0A_SPEC_REREVIEW/REVIEW.md (what R022 was supposed to fix)
11. 01_ORIGINAL_ARTIFACTS/Pioneer-Alignment-Phase-0A-Builder-Handoff-v1.md

══════════════════════════════════════
OPERATOR SMOKE (re-run yourself; do not trust alone)
══════════════════════════════════════

From ROUND_022:

```bash
export PYTHONDONTWRITEBYTECODE=1
cd 03_EXCHANGE/ROUND_022_CONTROLLING_PHASE0A_REPAIR
python3 -S meta_validate_round22.py
python3 -S meta_validate_round22.py --semantic-only
python3 -S independent_oracle.py
python3 -S transition_evaluator.py
python3 -S export_generator.py
python3 -S export_verifier.py
python3 -S verify_round22_receipts.py
python3 -S run_round22_mutations.py --output-json /tmp/r023-mut.json --output-md /tmp/r023-mut.md
PYTHONHASHSEED=1 python3 -S run_round22_mutations.py --output-json /tmp/r023-m1.json --output-md /tmp/r023-m1.md
PYTHONHASHSEED=2 python3 -S run_round22_mutations.py --output-json /tmp/r023-m2.json --output-md /tmp/r023-m2.md
# m1 must equal m2
python3 -S run_round22_closure_probes.py
```

Also: `python3 -S 04_TOOLS/verify_input_manifest.py` from relay root.

══════════════════════════════════════
MANDATORY INDEPENDENT PROBES
══════════════════════════════════════

Invent **at least 10** material mutations **outside** the 66-class Round 022 registry.
Disposable /tmp full-relay copies only. Use coherent rebind/pin discipline so “reject” is a real control, not an unpinned digest crash.

Attack priorities:

1. Authority smuggling still: undeclared files, zero-width, homoglyphs, encoding, split strings, binary/comment smuggling, ZIP member smuggling beyond the fixed fixture set
2. Package vs manifest coverage gaps after R022 “package membership” claim
3. DEFERRED laundering into candidate PASS / N80
4. HOLD rename / vocabulary extension
5. slug bound / hostile corpus games beyond max_length
6. export domain / identity coherent rebind
7. evidence symlink / path / extra file
8. receipt staleness / non-vacuous content
9. new reflexive oracle op names
10. pycache / extraneous shipped files
11. Python indirection not covered by exact-hash locks
12. Coherent removal of required floor while counts rebind

False-green = relevant tools still exit 0 after mutation.

══════════════════════════════════════
HARD QUESTIONS
══════════════════════════════════════

1. Are R21-F01..F04 and residual R19-F02/F05 actually closed outside the registry?
2. Can prohibited-authority text still ship green anywhere in the package?
3. Is DEFERRED still honest?
4. HOLD terminal? N80 reviewed-bytes?
5. Did R022 break export/hashseed?
6. Release to bounded local builder — yes/no and why

══════════════════════════════════════
WRITE ONLY
══════════════════════════════════════

```text
03_EXCHANGE/ROUND_023_INDEPENDENT_PHASE0A_SPEC_REREVIEW/**
```

plus CURRENT_STATE allowed control/manifest paths.

Required: REVIEW.md, FINDING_CLOSURE.json, EXECUTION_RECEIPT.json, RETURN_SUMMARY.md, SHA256SUMS.txt, probe scripts/receipts.

Do not modify ROUND_022 package bytes (probes on disposable copies only).

══════════════════════════════════════
ADJUDICATION — exactly one
══════════════════════════════════════

- PHASE0A_SPEC_RELEASED_TO_BOUNDED_LOCAL_BUILDER
- HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR
- INSUFFICIENT_EVIDENCE

Release only if invented probes are 0 false-green and release criteria hold.
Release = local builder later, NOT deploy / public wallets / economy launch.

══════════════════════════════════════
RETURN
══════════════════════════════════════

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 -S 04_TOOLS/build_return_relay.py Pioneer-Alignment-Single-Relay-v14.zip
mkdir -p /home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T007
# copy v14 to T007 and Downloads
```

Final message:

```text
ADJUDICATION: <token>
ZIP: <path>
SHA256: <full 64 hex>
PROBES: invented=<N> false_green=<n> rejected=<n>
R21_F01..F04 / R19_F02 F05: CLOSED|OPEN each
OFFICIAL: mut 66 status / seed_identical / closure
NOTES: ...
```

Start now.
