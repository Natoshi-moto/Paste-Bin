# Operator farm — how this works

You run the monkeys in **separate terminals**.  
This Grok session is the **non-retarded operator**: writes packs, prompts, adjudication criteria, and next tickets.

## Two-terminal rule

```text
Terminal 1: this Grok (operator) — always
Terminal 2: exactly one monkey — Claude or Codex or other Grok
```

You may **have** multiple accounts. You only **run one monkey at a time**. No parallel tickets.

## Accounts (pool, not parallel)

| Slot | Tool | Typical use when selected as the single monkey |
|------|------|--------------------------------------------------|
| C* | Any Claude account | Re-review / repair / implement when ticket says |
| X* | Any Codex account | Implementation / tests / debug when ticket says |
| G2 | Other Grok account | Second opinion or alternate operator pass |

**This session** stays orchestrator unless you say otherwise.

## Loop

1. I drop **one** active ticket + paste prompt.
2. You open **one** monkey terminal.
3. You give it only the pack + paste prompt.
4. Monkey returns into `03_RETURNS/<ticket-id>/`.
5. You paste the return path back here.
6. I adjudicate, then open **the next single ticket** (not a swarm).

## Hard rules for every monkey

- No deploy, DNS, Cloudflare, credentials, spending, on-chain, public wallet launch.
- Full **internal** NEX/LEX economy is the strategic target; not Phase 0A smuggling.
- No rewriting original artifacts unless the ticket says so.
- Return one complete artifact set, not a novel.
- If blocked: say `BLOCKED` + exact missing input. Do not invent host/app evidence.

## Charter (operator intent, 2026-08-01)

- **Target:** full **internal** economy (NEX + LEX + internal wallets/accounts).
- **Not:** on-chain, fiat rails, external markets.
- **Public site hold** still exists until you explicitly lift it with a dated decision.
- **Phase 0A** remains the narrow local notes slice until independent re-review passes.
