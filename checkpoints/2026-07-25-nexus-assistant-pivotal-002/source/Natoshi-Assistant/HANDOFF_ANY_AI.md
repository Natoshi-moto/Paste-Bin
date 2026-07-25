# Handoff — any AI improving Natoshi-Assistant

**status_authority:** `NONE`  
**Experiment:** `SBX-EXP-NATOSHI-ASSISTANT-001`

## Activation

Operator may say any of:

- “Improve Natoshi-Assistant”  
- “Make the Matrix terminal better”  
- “Fork the floating chat”  
- “Let’s fuck around in the sandbox” (then point at this project)

## First response (substance)

> 🧪 You’re in FUCK-AROUND LAND on **Natoshi-Assistant**. Improve the overlay. Nothing here can affect Nexus Lab unless we deliberately package a Promotion Gate.

## Mandatory contract

1. Read `README.md`, `EXPERIMENT.md`, `SECURITY.md`, `IMPROVE_ME.md`, then `app/matrix_terminal.py`.  
2. Preserve operator words separately from your interpretation.  
3. Work only under Experimental-Sandbox (`sandbox/experiment/*` or a new `sandbox/*` branch).  
4. **Never** push Lab. **Never** add secrets to git.  
5. Prefer small, reversible PRs with a dated `RESULTS_*.md` or appendix.  
6. Re-run `python3 -m py_compile app/matrix_terminal.py` (and any new tests you add).  
7. Disclose your model/provider as reported metadata, not verified identity.  
8. Finish with: what changed, what became public, what failed, Lab touched? (must be no), ≤3 next choices.

## Safe improvement modes

| Mode | OK examples |
|------|-------------|
| UX | Better drag/resize, hotkeys, opacity, themes, minimize-to-tray |
| Providers | Fix streaming bugs, add Anthropic-compatible, better Ollama options |
| Search | More robust search backend, citations UI, offline cache |
| Reminders | Persist reminders to disk, snooze, natural language times |
| Quality | Split modules, tests, packaging (flatpak later), a11y |
| Break | Adversarial: prompt injection via search results; document findings |

## Unsafe / forbidden without explicit operator + separate process

- Lab `main` writes or credentials  
- Shipping real API keys  
- Enabling YOLO shell execution from chat by default  
- Claiming the assistant is secure, audited, or canonical  
- Quietly resurrecting cancelled security-alarm setup scripts  

## Suggested PR shape

```text
branch: sandbox/experiment/natoshi-assistant-<short-topic>
files:  projects/Natoshi-Assistant/**
commit: clear user-facing change + RESULTS note
PR:     against Experimental-Sandbox main (or keep on experiment branch)
```

## Done bar for a contribution

- [ ] Claim in EXPERIMENT still true or claim updated honestly  
- [ ] No secrets  
- [ ] `py_compile` (or tests) green  
- [ ] Short RESULTS or IMPROVE_ME checkoff  
- [ ] Lab not touched  
