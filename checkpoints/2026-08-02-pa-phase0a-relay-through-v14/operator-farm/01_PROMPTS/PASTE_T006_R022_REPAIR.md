# PASTE THIS ENTIRE FILE — T006 / Round 022 controlling repair

You have full access to this PC filesystem. Do not ask me to upload files. Read from disk. Execute end-to-end. Two-terminal rule: you are the only monkey.

You are the **controlling** Phase 0A specification/gate engineer for ONE bounded repair round.
You did NOT write Round 021. You are NOT the application builder.

══════════════════════════════════════
INPUT
══════════════════════════════════════

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v12.zip
SHA-256: b088ea589ba10af897dea6b7ccc963f620d8bcf5d48bfce3658f6451056adf4a
```

Also at:
```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T005/Pioneer-Alignment-Single-Relay-v12.zip
```

```bash
sha256sum /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v12.zip
# must match b088ea589ba10af897dea6b7ccc963f620d8bcf5d48bfce3658f6451056adf4a

rm -rf /tmp/pa-r022-work
mkdir -p /tmp/pa-r022-work && cd /tmp/pa-r022-work
unzip -q /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v12.zip -d relay
cd relay
export PYTHONDONTWRITEBYTECODE=1
```

══════════════════════════════════════
READ
══════════════════════════════════════

1. 00_CONTROL/CURRENT_STATE.json
2. 00_CONTROL/START_HERE.md
3. 03_EXCHANGE/ROUND_021_INDEPENDENT_PHASE0A_SPEC_REREVIEW/RETURN_SUMMARY.md
4. 03_EXCHANGE/ROUND_021_INDEPENDENT_PHASE0A_SPEC_REREVIEW/REVIEW.md
5. 03_EXCHANGE/ROUND_021_INDEPENDENT_PHASE0A_SPEC_REREVIEW/FINDING_CLOSURE.json
6. 03_EXCHANGE/ROUND_021_INDEPENDENT_PHASE0A_SPEC_REREVIEW/EXECUTION_RECEIPT.json
7. 03_EXCHANGE/ROUND_021_INDEPENDENT_PHASE0A_SPEC_REREVIEW/r21_probes.py
8. 03_EXCHANGE/ROUND_021_INDEPENDENT_PHASE0A_SPEC_REREVIEW/r21_authority_surface.py
9. Round 020 package (read-only; supersede with NEW Round 022 files — do not edit R020/R021 bytes)

══════════════════════════════════════
PRESERVE (confirmed held under R021 attack)
══════════════════════════════════════

- DEFERRED honest; cannot launder candidate PASS
- HOLD terminal (including renamed HOLD origin)
- N80 cannot release non-reviewed bytes
- Raw HTML payload-based detection (text/html, obfuscated javascript URIs)
- Evidence rejects symlink/path escape
- Export identity + hashseed determinism
- Official 46 registry + R019 probes still reject
- R19-F01, F03, F04, F06, F07 remain CLOSED — do not reopen

══════════════════════════════════════
MUST CLOSE
══════════════════════════════════════

### R21-F01 CRITICAL — authority scan ≠ package membership
- Scan must cover **every file that ships in the Round 0XX package / is checksum-covered**, not only normative-manifest members.
- Undeclared files carrying reject_substrings at any of the 8 locations / 5 extensions Fable used must FAIL validation.
- Import all R021 authority-surface variants as mandatory negative tests.
- Methodology: pin security constants digests the way R020 probes do — do not crash on import and call it “reject”.

### R21-F02 HIGH — slug.max_length weakenable
- max_length (and related bounds) must be locked to handoff/security constants; widening 80→100000 must reject.
- Cross-check is not mere “consistency between two rewritable places” — pin absolute bounds.

### R21-F03 MEDIUM — export identity domains unenforced vs library
- Declared domain strings in export/canonical specs must match lib constants; divergence rejects.
- Closure: change declared domain while leaving code constants (or reverse) → reject.

### R21-F04 MEDIUM — shipped receipts stale
- Regenerated receipts must match live scan counts; or exclude live-varying fields; or regenerate at package seal.
- Cross-hash chain must not claim stale authority_strings_scanned figures.

### R19-F02 / R19-F05 still OPEN via successors
- Close the residual gaps R021 proved.

### General rule (carry forward)
No gate may key on an identifier, list length, or value the mutation can rewrite **without** binding to package-wide bytes / absolute constants.

══════════════════════════════════════
MANDATORY REGISTRY FOR R022
══════════════════════════════════════

Must reject with intended reasons:
1. All Round 020 mutation classes (46)
2. All Round 019 probes (8)
3. All Round 021 invented probe classes (12) from r21_probes.py — especially the 3 false-greens
4. Authority variants from r21_authority_surface.py (8 locations × extensions as documented)
5. Fresh closure probes for F01–F04

Receipts deterministic under PYTHONHASHSEED=1 and 2.
Disposable /tmp copies only for mutations.

══════════════════════════════════════
WRITE ONLY
══════════════════════════════════════

```text
03_EXCHANGE/ROUND_022_CONTROLLING_PHASE0A_REPAIR/**
```

plus allowed_mutations from CURRENT_STATE.json.

Include REPAIR_SUMMARY.md, REQUEST_FOR_INDEPENDENT_REREVIEW.md, FINDING_CLOSURE mapping, validator/oracle/mutation runner, receipts, SHA256SUMS (exclude self, exclude __pycache__).

DO NOT modify ROUND_021, ROUND_020, originals.

══════════════════════════════════════
ADJUDICATION — one of
══════════════════════════════════════

- ROUND022_REPAIR_COMPLETE_AWAITING_INDEPENDENT_REREVIEW
- HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR
- INSUFFICIENT_EVIDENCE

══════════════════════════════════════
RETURN
══════════════════════════════════════

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 -S 04_TOOLS/build_return_relay.py Pioneer-Alignment-Single-Relay-v13.zip
mkdir -p /home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T006
# copy built zip to:
# /home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T006/Pioneer-Alignment-Single-Relay-v13.zip
# /home/anon/Downloads/Pioneer-Alignment-Single-Relay-v13.zip
```

State after success:
  AWAITING_INDEPENDENT_PHASE0A_SPEC_REREVIEW
  completed_round: ROUND_022_CONTROLLING_PHASE0A_REPAIR
  requested_return_filename: Pioneer-Alignment-Single-Relay-v14.zip

Final message:
ADJUDICATION: ...
ZIP: ...
SHA256: ...
CLOSED: R21-F01..F04 and residual R19-F02/F05
MUTATIONS: rejected/false_green
NOTES: ...

No app build, no deploy, no credentials, no public economy.
Start now.
