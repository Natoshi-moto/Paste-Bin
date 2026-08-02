# PASTE THIS ENTIRE FILE INTO SOL ULTRA — T004 / Round 020

You are the **controlling** Phase 0A specification/gate engineer for **one bounded repair round**.

You are **not** the independent reviewer who wrote Round 019.  
You are **not** the application builder.

## Input corpus (only)

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v10.zip
```

Verify SHA-256 first:

```text
5c3549431cf38d10a429fe83300fbc73afb8502121a7166df5b2a0b4dbf30e9e
```

Unpack to a working tree. Prefer disposable copies under `/tmp` for all mutations.

**Critical hygiene:** Round 019 found that importing Python packages writes `__pycache__` and breaks hash-pinned trees. Always use:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -S ...
```

Never validate the live tree you are editing without excluding `__pycache__`.

## Read completely (in order)

1. `00_CONTROL/CURRENT_STATE.json`
2. `00_CONTROL/START_HERE.md`
3. `00_CONTROL/PROMPT_TO_EXECUTE.md` (if present for R020; else this prompt is controlling)
4. `03_EXCHANGE/ROUND_019_INDEPENDENT_PHASE0A_SPEC_REREVIEW/RETURN_SUMMARY.md`
5. `03_EXCHANGE/ROUND_019_INDEPENDENT_PHASE0A_SPEC_REREVIEW/REVIEW.md`
6. `03_EXCHANGE/ROUND_019_INDEPENDENT_PHASE0A_SPEC_REREVIEW/FINDING_CLOSURE.json`
7. `03_EXCHANGE/ROUND_019_INDEPENDENT_PHASE0A_SPEC_REREVIEW/EXECUTION_RECEIPT.json`
8. `03_EXCHANGE/ROUND_019_INDEPENDENT_PHASE0A_SPEC_REREVIEW/r19_probes.py`
9. `01_ORIGINAL_ARTIFACTS/Pioneer-Alignment-Phase-0A-Builder-Handoff-v1.md`
10. Round 018 package under `03_EXCHANGE/ROUND_018_CONTROLLING_PHASE0A_REPAIR/` (do not modify it)

## Adjudication you are responding to

```text
HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR
```

Round 018's own 31 mutations reject. Round 019 invented 8 more probes; **7 false-green**.

## Do not reopen (carry forward closed)

These are **CLOSED** at spec level — preserve behaviour:

- HOLD is terminal (exhaustive N50/N60/N70 matrix; only two allowed traces)
- N80 cannot release non-reviewed bytes (binding/tree/source/evidence + remotes/bind/provider/untracked)
- Export identity formulas + golden ZIP independent reproduction
- Deterministic mutation receipts across PYTHONHASHSEED values

## Must close (Round 019 findings)

### R19-F01 CRITICAL — oracle blind / echo channel

- `CANDIDATE_OBSERVE` / any op that only compares expectation to itself is **forbidden** for counted PASS.
- Every case counted in the 89 total must be decided by a **non-reflexive** oracle path, **or** explicitly labelled `DEFERRED` and **excluded** from pass totals / candidate PASS eligibility.
- Closure test: garbage inputs and invented reason codes must **not** yield 60/89 or 42/89 passes.
- Blacklist must cover behavioural classes, not only the string `APPLY_NAMED_CASE`.

### R19-F02 CRITICAL — authority scan dead code

- `AUTHORITY_REJECT_SUBSTRINGS` (or successor) must be **used**.
- Extend vocabulary: GitHub, push, deploy, Cloudflare, DNS, public repository, credentials, provider, 0.0.0.0, DeepSeek, etc. consistent with prohibited authority.
- Scan **every string field of every normative file** under the Round 020 package (not only DAG required_checks).
- Closure test: inject “push to public GitHub repository” / “deploy to Cloudflare” into a normative string; validator rejects.

### R19-F03 CRITICAL — raw HTML keyed on case ID

- Enforce on **fixture payload** (`body_markdown` / input text), not case-id substrings.
- Closure test: rename SCRIPT/EVENT/JS case IDs consistently and flip to echo channel → must still REJECT raw HTML fixtures; pure rename must not invert to ACCEPT.

### R19-F04 HIGH — evidence hashes not resolved

- Every `evidence_sha256` must resolve to bytes at a safe relative `evidence_path` (or explicit synthetic fixture root declared in the vectors package).
- Closure test: alter fixture bytes without updating hash → reject; swap hash without bytes → reject.

### R19-F05 HIGH — schema constants diverge from oracle

- Schema slug pattern + reserved list must be the **single source of truth**; oracle/validator must load them from schema (or shared locked constants file), not hardcode diverging copies.
- Closure test: weaken slug pattern / empty reserved list → reject.

### R19-F06 HIGH — `__pycache__` breaks documented commands

- Exclude `__pycache__` / `*.pyc` from SHA256SUMS, normative manifest coverage, and full-mode checksum walks.
- Documented commands must exit 0 on a clean unpack **without** requiring tribal knowledge — still set `PYTHONDONTWRITEBYTECODE=1` in runner scripts as defense in depth.
- Closure test: fresh unpack + documented `python3 -S meta_validate_*.py` full mode → green (after R020).

### R19-F07 MEDIUM — empty forbidden_examples vacuously OK

- Minimum forbidden-example set required by exact IDs, **or** derive forbidden set from transition table exhaustively (preferred: evaluator is source of truth and examples cannot be deleted to disable checks).
- Closure test: empty `forbidden_examples` → reject **or** behaviour still refuses HOLD traces without needing that list.

## Mandatory negative controls for Round 020 suite

Import:

1. All Round 018 registry mutations (31) — still must reject  
2. All Round 017 adversarial classes (20) — still must reject  
3. All Round 019 probe classes that were false-green (from `r19_probes.py` / FINDING_CLOSURE) — must now reject for intended reasons  
4. At least the closure tests above  

Receipts must be deterministic under `PYTHONHASHSEED=1` and `2`.

## Write only under

```text
03_EXCHANGE/ROUND_020_CONTROLLING_PHASE0A_REPAIR/**
```

plus control/tool/manifest paths listed in `CURRENT_STATE.json` allowed_mutations.

**Do not modify** Round 019, Round 018, or `01_ORIGINAL_ARTIFACTS/`.

## Required outputs in ROUND_020 directory

- Complete repaired normative package (may supersede R018 files by **new** R020 files; do not edit R018 in place)
- Validator, oracle, transition evaluator, mutation runner (R020 names)
- Mapping of R19-F01..F07 → exact files/tests
- `REPAIR_SUMMARY.md`
- `REQUEST_FOR_INDEPENDENT_REREVIEW.md`
- Validation + mutation receipts with commands, exit codes, hashes, counts
- `SHA256SUMS.txt` (exclude self; exclude `__pycache__`)

## Adjudication — exactly one

- `ROUND020_REPAIR_COMPLETE_AWAITING_INDEPENDENT_REREVIEW`
- `HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR`
- `INSUFFICIENT_EVIDENCE`

## Prohibitions

No application build; no repo/git init; no branch/commit; no push; no credentials; no provider; no deploy; no DNS/Cloudflare; no public wallets; no on-chain; no lifting public hold; no inventing host/app evidence.

## Return protocol

Update state to:

```text
AWAITING_INDEPENDENT_PHASE0A_SPEC_REREVIEW
```

(or equivalent per RELAY_PROTOCOL after R020)

Build and return **one** complete zip:

```text
Pioneer-Alignment-Single-Relay-v11.zip
```

Place it at:

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T004/Pioneer-Alignment-Single-Relay-v11.zip
```

Print detached outer SHA-256 in the final message.

## Operator note

Bulletproof before deployment. Credits are not a reason to leave name-keyed gates. If you cannot close a finding, HOLD and say exactly why — do not ship theater.
