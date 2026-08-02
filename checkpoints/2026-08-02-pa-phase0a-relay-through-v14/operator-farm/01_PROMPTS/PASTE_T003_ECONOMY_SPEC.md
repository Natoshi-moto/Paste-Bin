# PASTE THIS ENTIRE FILE — T003 internal economy spec-only

You are writing a **build charter** for Pioneer Alignment’s full **internal** economy.

## Operator intent

- Full internal NEX + LEX + participant internal wallets/accounts
- **Not** on-chain / blockchain
- **Not** fiat buy/redeem / external markets
- Hard membranes: no NEX↔LEX conversion; no external pricing
- Do **not** claim the public site hold is lifted

## Read (minimum)

1. `/home/anon/Projects/PA-Release-Prep/operator-farm/00_CONTROL/CHARTER.md`
2. From relay v9 extracted corpus:
   - Round 5 NEX economy closure
   - Round 7 LEX package if present
3. Public position source (read-only):
   - `/home/anon/Projects/PA-Release-Prep/pioneer-alignment-public/content/positions/2026-07-30--nex-and-lex.md`
   - notes on pioneer-alignment-and-nexus if useful

## Produce only these files

Under:

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T003/
```

### 1. INTERNAL_ECONOMY_BUILD_CHARTER.md

- In/out of scope
- Definitions: wallet = internal account client (not crypto wallet)
- Authority boundaries
- What “done” means for v0 internal economy

### 2. NEX_LEX_WALLET_BOUNDARY.md

- Exact prohibited actions
- Exact allowed participant actions
- Epoch / issuance / transfer high-level invariants
- Failure modes if someone tries to bolt on external value

### 3. PHASE_PLAN.md

Ordered programme (example shape — improve it):

1. Phase 0A local notes gate close
2. Internal ledger core (no UI public)
3. Internal wallet/account client local-only
4. NEX task/issuance simulation epoch
5. LEX governance simulation epoch
6. Combined adversarial gates
7. Public hold-lift decision packet (operator only)

### 4. OPEN_QUESTIONS.md

Only questions that block build. No philosophy essays.

## Prohibitions

No application implementation, no deploy, no credential use, no on-chain design, no “while we’re at it” Phase 0A rewrites.
