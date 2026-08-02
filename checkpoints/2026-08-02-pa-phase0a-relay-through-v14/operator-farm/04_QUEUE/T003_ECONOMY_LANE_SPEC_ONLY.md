# T003 — Full internal economy lane (spec-only charter pack)

**Priority:** P1 after T001 is in flight (can run on C2/X1 in parallel)  
**Status:** READY TO OPEN when you want economy work simultaneous with Phase 0A re-review  
**Recommended slot:** C2 or X1

## Intent (operator)

Full **internal** NEX + LEX + internal wallets.  
**No** on-chain, **no** fiat rails, **no** external markets.

## Do not

- Implement application code yet
- Touch production site hold text unless a separate ticket says so
- Merge economy into Phase 0A notes app

## Input corpus pointers

- Relay v9 contains Round 5 NEX package under extracted corpus
- Public position pages under `pioneer-alignment-public` (read-only reference)
- Operator charter: `operator-farm/00_CONTROL/CHARTER.md`

## Paste prompt

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/01_PROMPTS/PASTE_T003_ECONOMY_SPEC.md
```

## Return

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T003/
```

Expected:

- `INTERNAL_ECONOMY_BUILD_CHARTER.md`
- `NEX_LEX_WALLET_BOUNDARY.md`
- `PHASE_PLAN.md` (ordered gates before any public hold lift)
- `OPEN_QUESTIONS.md`
