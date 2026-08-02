# T001 — Round 019 independent Phase 0A spec re-review

**Priority:** P0  
**Recommended slot:** C1 (Claude independent)  
**Optional parallel:** G2 second opinion (read-only, no shared chat history with C1)

## Input pack

```text
/home/anon/Downloads/Pioneer-Alignment-Single-Relay-v9.zip
SHA-256: d1fa17f84dda2842bd7d3b391ae377bdb570d514c33dcf85f6d8a14381e4d753
```

Paste prompt:

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/01_PROMPTS/PASTE_T001_CLAUDE.md
```

## Allowed adjudication tokens (exactly one)

- `PHASE0A_SPEC_RELEASED_TO_BOUNDED_LOCAL_BUILDER`
- `HOLD_FOR_FURTHER_PHASE0A_SPEC_REPAIR`
- `INSUFFICIENT_EVIDENCE`

## Return

Put outputs here:

```text
/home/anon/Projects/PA-Release-Prep/operator-farm/03_RETURNS/T001/
```

Preferred return: complete updated relay zip

```text
Pioneer-Alignment-Single-Relay-v10.zip
```

plus detached SHA-256 reported beside it (not only inside the zip).

If the monkey cannot rebuild the full relay, return at minimum:

- `REVIEW.md`
- `FINDING_CLOSURE.json`
- `EXECUTION_RECEIPT.json`
- `RETURN_SUMMARY.md`
- `SHA256SUMS.txt`

## Operator note

Do not start public wallet / full internal economy build on this ticket. This ticket is Phase 0A gate re-review only.
