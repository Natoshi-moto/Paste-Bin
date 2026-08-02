# PASTE THIS ENTIRE FILE — T008 / Round 024 controlling repair

You have full access to this PC filesystem. Do not ask me to upload files. Read from disk. Execute end-to-end. Two-terminal rule: you are the only monkey.

You are the **controlling** Phase 0A specification/gate engineer for ONE bounded repair round.
You did NOT write Round 023. You are NOT the application builder.
No deploy, push, credentials, providers, DNS/Cloudflare, public wallets, on-chain, or app build.

══════════════════════════════════════
INPUT
══════════════════════════════════════

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v14.zip
SHA-256: 81be0c161051f76eb0f8b49a07db14f1faa106633c68a4ec027ddc282bcc7c54
```

Also:
```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T007/Pioneer-Alignment-Single-Relay-v14.zip
```

```bash
sha256sum /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v14.zip
# must equal 81be0c161051f76eb0f8b49a07db14f1faa106633c68a4ec027ddc282bcc7c54

rm -rf /tmp/pa-r024-work
mkdir -p /tmp/pa-r024-work && cd /tmp/pa-r024-work
unzip -q /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v14.zip -d relay
cd relay
export PYTHONDONTWRITEBYTECODE=1
```

══════════════════════════════════════
READ
══════════════════════════════════════

1. 00_CONTROL/CURRENT_STATE.json
2. 00_CONTROL/START_HERE.md
3. 03_EXCHANGE/ROUND_023_INDEPENDENT_PHASE0A_SPEC_REREVIEW/RETURN_SUMMARY.md
4. 03_EXCHANGE/ROUND_023_INDEPENDENT_PHASE0A_SPEC_REREVIEW/REVIEW.md
5. 03_EXCHANGE/ROUND_023_INDEPENDENT_PHASE0A_SPEC_REREVIEW/FINDING_CLOSURE.json
6. 03_EXCHANGE/ROUND_023_INDEPENDENT_PHASE0A_SPEC_REREVIEW/EXECUTION_RECEIPT.json
7. 03_EXCHANGE/ROUND_023_INDEPENDENT_PHASE0A_SPEC_REREVIEW/r23_probes.py
8. 03_EXCHANGE/ROUND_023_INDEPENDENT_PHASE0A_SPEC_REREVIEW/receipts/
9. Round 022 package (read-only; supersede with NEW ROUND_024 files — do not edit R022/R023 in place)
10. 01_ORIGINAL_ARTIFACTS/Pioneer-Alignment-Phase-0A-Builder-Handoff-v1.md

══════════════════════════════════════
PRESERVE (confirmed under R023 attack)
══════════════════════════════════════

- Official suite: 66/0 mutations, 43/43 closure, seed-identical, receipt replay
- R21-F02, R21-F03, R21-F04, residual R19-F05 CLOSED — do not reopen
- DEFERRED arithmetic honest; cannot launder candidate PASS
- HOLD terminal in the evaluator (machine)
- N80 reviewed-byte identity
- Export identity + hashseed determinism
- Evidence containment / ZIP fixture closure / payload-semantic active content

══════════════════════════════════════
MUST CLOSE
══════════════════════════════════════

### R23-F01 CRITICAL — confusable authority bypass
- Authority matcher must use a confusable skeleton (Unicode TR39 or explicit map), not NFKC alone.
- Reject leaves that mix Latin with other scripts for authority matching, or fold confusables to a Latin skeleton before match.
- Closure: R23-P01, R23-P02 reject after coherent rebind.

### R23-F02 CRITICAL — fragmentation + unfolded composition
- Match a whole-document / multi-leaf normalized projection in addition to per-leaf matching (adjacent JSON strings, markdown table cells, split phrases).
- Reject non-foldable static composition in validator/source Python used for authority (generator-expression joins that evade literal scan), especially inside meta_validate itself.
- Closure: R23-P03, R23-P04, R23-P05 reject.

### R23-F03 HIGH — scan is round-dir not relay-wide
- Extend authority scan to whole relay (at least 00_CONTROL/**, 04_TOOLS/**, and all exchange rounds that ship), OR pin out-of-scope paths by hash + forbid new text there without scan.
- Closure: R23-P06 rejects (authority in 00_CONTROL/START_HERE.md).

### R23-F04 HIGH — acceptance contract side-channel keys
- additionalProperties false (or closed key allowlist) on acceptance contract top-level.
- Add release/deferral-override vocabulary to authority reject set.
- Closure: R23-P10 rejects.

### R23-F05 HIGH — HOLD overridable in prose
- Add review-bypass vocabulary: e.g. "clear a hold", "without a further independent review", "proceed directly to n80", "advisory hold", synonyms.
- Scan all shipped text including control docs.
- Closure: R23-P11 rejects.

### R23-F06 MEDIUM — receipt freshness limitation
- Document explicitly as anti-staleness not anti-adversary; no false claims. Optional: strengthen if cheap.

### Residual R21-F01 / R19-F02
- Closed only when F01–F03 authority paths are closed.

### Methodology
- All R023 probes must be permanent registry members with intended reason codes.
- Coherent rebind including security-constant repin, validator self-lock, receipt recoherence — no false credit for import-crash rejects.
- P14 bytecode-named members: keep builder exclusion; registry may treat as unshippable green if archive excludes them, but document.

══════════════════════════════════════
MANDATORY REGISTRY
══════════════════════════════════════

Must reject for intended reasons:
1. All Round 022 mutation classes (66)
2. All Round 023 invented probes (14) from r23_probes.py — especially P01,P02,P03,P05,P06,P10,P11 (and P04 if FG)
3. Extra confusable + fragmentation + control-path variants you invent as closure tests
4. Prior R021 false-greens still reject

Seed-identical under PYTHONHASHSEED=1 and 2.

══════════════════════════════════════
WRITE ONLY
══════════════════════════════════════

```text
03_EXCHANGE/ROUND_024_CONTROLLING_PHASE0A_REPAIR/**
```

plus allowed_mutations from CURRENT_STATE.json.

Include full executable gate, REPAIR_SUMMARY.md, REQUEST_FOR_INDEPENDENT_REREVIEW.md, FINDING_CLOSURE, receipts, SHA256SUMS (no self, no __pycache__).

DO NOT modify ROUND_023, ROUND_022, originals.

══════════════════════════════════════
ADJUDICATION — one of
══════════════════════════════════════

- ROUND024_REPAIR_COMPLETE_AWAITING_INDEPENDENT_REREVIEW
- HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR
- INSUFFICIENT_EVIDENCE

══════════════════════════════════════
RETURN
══════════════════════════════════════

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 -S 04_TOOLS/build_return_relay.py Pioneer-Alignment-Single-Relay-v15.zip
mkdir -p /home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T008
# copy to T008 and Downloads
```

State after success:
  AWAITING_INDEPENDENT_PHASE0A_SPEC_REREVIEW
  completed_round: ROUND_024_CONTROLLING_PHASE0A_REPAIR
  requested_return_filename: Pioneer-Alignment-Single-Relay-v16.zip

Final message:
ADJUDICATION: ...
ZIP: ...
SHA256: <full 64>
CLOSED: R23-F01..F06 / R21-F01 / R19-F02
MUTATIONS: rejected= false_green= seed_identical=
NOTES: ...

Start now.
