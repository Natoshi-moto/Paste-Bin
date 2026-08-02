# T006 operator smoke — PASS

Date: 2026-08-02

## Archive

- path: `/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v13.zip`
- also: `operator-farm/03_RETURNS/T006/Pioneer-Alignment-Single-Relay-v13.zip`
- sha256: `2bec715b209dc16fef01fab76ac13c3329e61da4f89d6ca320bc4e9c1a68e60b`
- bytes: 2293915

## Results

| Check | Result |
|---|---|
| verify_input_manifest | PASS — 1240 files |
| meta_validate full | SPEC_CONTRACT_VALID |
| meta_validate semantic | SPEC_CONTRACT_VALID |
| independent_oracle | 54 passed / 35 deferred / candidate_pass_eligible=false |
| transition_evaluator | PASS |
| export_generator/verifier | matches_golden |
| verify_round22_receipts (quick) | 9/9 PASS |
| run_round22_mutations | 66 rejected / 0 false_green / 0 wrong_reason |
| PYTHONHASHSEED 1 vs 2 | byte-identical |
| run_round22_closure_probes | PASS — 43/43 intended reject, 0 false_green, 11/11 findings closed |

## Adjudication

`ROUND022_REPAIR_COMPLETE_AWAITING_INDEPENDENT_REREVIEW` — **provisionally accepted** pending Round 023 independent re-review outside the 66-class registry.

## Next

T007 — independent re-review → v14
