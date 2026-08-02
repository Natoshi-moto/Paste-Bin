# PASTE THIS ENTIRE FILE — T009 / Round 025 independent re-review

You have full access to this PC filesystem. Do not ask me to upload files. Read from disk. Execute end-to-end. Two-terminal rule: you are the only monkey.

You are the INDEPENDENT Phase 0A specification re-reviewer.
You did NOT author Round 024. You are NOT the application builder.
No deploy, push, credentials, providers, DNS/Cloudflare, public wallets, on-chain, or app build.

══════════════════════════════════════
INPUT
══════════════════════════════════════

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v15.zip
SHA-256: 195c4691dbe2cb64c963e0a8066e68c5685697acbdb3d3e218f7f7e83c70c601
```

Also:
```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T008/Pioneer-Alignment-Single-Relay-v15.zip
```

```bash
sha256sum /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v15.zip
# must equal 195c4691dbe2cb64c963e0a8066e68c5685697acbdb3d3e218f7f7e83c70c601
rm -rf /tmp/pa-r025-work && mkdir -p /tmp/pa-r025-work && cd /tmp/pa-r025-work
unzip -q /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v15.zip -d relay
cd relay && export PYTHONDONTWRITEBYTECODE=1
```

══════════════════════════════════════
READ
══════════════════════════════════════

1. 00_CONTROL/CURRENT_STATE.json, START_HERE.md, PROMPT_TO_EXECUTE.md, AUTHORITY.md
2. 03_EXCHANGE/ROUND_024_CONTROLLING_PHASE0A_REPAIR/{START_HERE,REPAIR_SUMMARY,REQUEST_FOR_INDEPENDENT_REREVIEW,RETURN_SUMMARY,FINDING_CLOSURE,MUTATION_RECEIPTS,CLOSURE_PROBE_RECEIPT}.md/json
3. 03_EXCHANGE/ROUND_023_INDEPENDENT_PHASE0A_SPEC_REREVIEW/REVIEW.md + r23_probes.py (what R024 was to close)
4. 01_ORIGINAL_ARTIFACTS/Pioneer-Alignment-Phase-0A-Builder-Handoff-v1.md

══════════════════════════════════════
OPERATOR SMOKE (re-run; do not trust alone)
══════════════════════════════════════

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 -S 04_TOOLS/verify_input_manifest.py
cd 03_EXCHANGE/ROUND_024_CONTROLLING_PHASE0A_REPAIR
python3 -S meta_validate_round24.py
python3 -S meta_validate_round24.py --semantic-only
python3 -S independent_oracle.py
python3 -S transition_evaluator.py
python3 -S export_generator.py
python3 -S export_verifier.py
python3 -S verify_round24_receipts.py
# full if time allows:
# python3 -S verify_round24_receipts.py --full
python3 -S run_round24_mutations.py --output-json /tmp/r025-mut.json --output-md /tmp/r025-mut.md
PYTHONHASHSEED=1 python3 -S run_round24_mutations.py --output-json /tmp/r025-m1.json --output-md /tmp/r025-m1.md
PYTHONHASHSEED=2 python3 -S run_round24_mutations.py --output-json /tmp/r025-m2.json --output-md /tmp/r025-m2.md
# m1 must equal m2
python3 -S run_round24_closure_probes.py
```

Claimed: 88 mut / 0 FG / seed-identical; R23-F01..F06 + R21-F01 + R19-F02 closed; receipt replay 17/17.

══════════════════════════════════════
MANDATORY INDEPENDENT PROBES (≥10 outside registry)
══════════════════════════════════════

Attack especially residual authority gaps after R024 matcher hardening:
1. New confusable sets not in TR39 map / mixed-script tricks
2. Fragmentation across more than two leaves / HTML attributes / YAML if any
3. Validator self-mod / unlock of locked python via alternate path
4. Relay-wide scan gaps: tools, manifests, nested rounds, binary smuggling
5. DEFERRED laundering / N80 / HOLD prose
6. Acceptance contract additionalProperties games
7. Export identity / slug floor still
8. Evidence / ZIP / receipt freshness
9. New reflexive oracle ops
10. Coherent floor removal

Disposable /tmp copies only. Coherent rebind. No credit for unpinned digest crashes.

FALSE_GREEN = tools still exit 0 after rebind.

══════════════════════════════════════
WRITE ONLY
══════════════════════════════════════

03_EXCHANGE/ROUND_025_INDEPENDENT_PHASE0A_SPEC_REREVIEW/**
+ CURRENT_STATE allowed control/manifest paths.

Required: REVIEW.md, FINDING_CLOSURE.json, EXECUTION_RECEIPT.json, RETURN_SUMMARY.md, SHA256SUMS.txt, probes.

Do not modify ROUND_024 bytes.

══════════════════════════════════════
ADJUDICATION — one of
══════════════════════════════════════

- PHASE0A_SPEC_RELEASED_TO_BOUNDED_LOCAL_BUILDER
- HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR
- INSUFFICIENT_EVIDENCE

Release only if ≥10 invented probes 0 material FG and deferred/HOLD/N80/authority hold.
Release = local builder later, NOT deploy/wallets/economy.

══════════════════════════════════════
RETURN
══════════════════════════════════════

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 -S 04_TOOLS/build_return_relay.py Pioneer-Alignment-Single-Relay-v16.zip
mkdir -p /home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T009
# copy to T009 and Downloads
```

FINAL:
ADJUDICATION: ...
ZIP: ...
SHA256: <full 64>
PROBES: invented= false_green= rejected=
R23_F01..F06 / R21_F01 / R19_F02: CLOSED|OPEN
OFFICIAL: mut/seed/closure
NOTES: ...

Start now.
