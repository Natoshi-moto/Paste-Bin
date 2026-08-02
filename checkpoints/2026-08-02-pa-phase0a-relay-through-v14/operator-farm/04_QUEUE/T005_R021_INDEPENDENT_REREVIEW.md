# T005 — Round 021 independent Phase 0A spec re-review

**Priority:** P0  
**Slot:** Fable (or next monkey after Sol Ultra)  
**Status:** OPEN  
**Depends on:** T004 operator smoke-check PASS (not final release)

## Input

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v11.zip
SHA-256: 77d2ae654e770ba7008074edcb0c55fe0bc15021dac010fd2dced0b63ceea044
```

## Paste prompt

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/01_PROMPTS/PASTE_T005_INDEPENDENT_REREVIEW.md
```

## Return

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T005/Pioneer-Alignment-Single-Relay-v12.zip
```

## Operator note on T004

Sol Ultra claims F01–F07 closed and 46/0 mutations. Operator re-ran on fresh unpack:
SPEC_CONTRACT_VALID, oracle 54 decided / 35 deferred / candidate_pass_eligible false,
mutations 46 reject seed-stable. Independent re-review must try to break it outside the registry.
