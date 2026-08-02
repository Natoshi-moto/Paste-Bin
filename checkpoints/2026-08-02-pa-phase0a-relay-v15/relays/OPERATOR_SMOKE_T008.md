# T008 operator smoke — PASS

Date: 2026-08-02

## Archive

- Downloads + T008: `Pioneer-Alignment-Single-Relay-v15.zip`
- sha256: `195c4691dbe2cb64c963e0a8066e68c5685697acbdb3d3e218f7f7e83c70c601`
- byte-identical across both paths

## Results

| Check | Result |
|---|---|
| verify_input_manifest | PASS — 1679 files |
| meta_validate full | SPEC_CONTRACT_VALID |
| meta_validate semantic | SPEC_CONTRACT_VALID |
| independent_oracle | 54 passed / 35 deferred / candidate_pass_eligible=false |
| transition / export | PASS / golden match |
| verify_round24_receipts (quick) | 9/9 PASS |
| run_round24_mutations | 88 rejected / 0 false_green / 0 wrong_reason |
| PYTHONHASHSEED 1 vs 2 | byte-identical |
| run_round24_closure_probes | PASS — 43/43, 11/11 findings closed |

## Adjudication

`ROUND024_REPAIR_COMPLETE_AWAITING_INDEPENDENT_REREVIEW` — **provisionally accepted** pending Round 025 independent re-review outside the 88-class registry.

## Next

T009 — independent re-review → v16
