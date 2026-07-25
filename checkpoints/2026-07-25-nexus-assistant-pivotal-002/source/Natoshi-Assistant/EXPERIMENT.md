# SBX-EXP-NATOSHI-ASSISTANT-001 — experiment record

**status_authority:** `NONE`  
**State:** `RUNNING`  
**Title:** Natoshi-Assistant / Matrix Terminal  
**Date opened (UTC):** 2026-07-25  
**Operator:** Natoshi-moto  

## Raw origin

Operator, 2026-07-25 (paraphrase preserved in spirit):

> Stop the alarm business. Make a mini terminal that sits on top of everything that I use whatever model I want that the whole thing is click and draggable and easily resizable and fucking sick and matrix like and i can just chat to it about shit and web search while i'm doing other stuff and that's an easy way it can remind me, cancel all the other shit.

Follow-up:

> cancel ALL the old alarm shit and post this as an experiment on live sandbox safely for other AI to make better as a Natoshi-Assistant

## Claim

A single local Python/Tk process can present an always-on-top, draggable, resizable Matrix-styled chat overlay that (a) talks to a selectable model provider (Ollama and/or OpenAI-compatible cloud endpoints via env keys), (b) performs a keyless web search path, and (c) schedules local reminders that notify the desktop — without Lab credentials, without the cancelled security-alarm setup, and without claiming product or Lab authority.

## Falsifier

Any of:

1. Window cannot stay above other apps when “always on top” is enabled.  
2. Window cannot be moved by title-bar drag or resized to usable sizes.  
3. Chat path fails for a listed Ollama model when Ollama is healthy.  
4. `/search` cannot return any results on a normal network (or fails closed with a clear error).  
5. `/remind` does not fire a visible reminder by the requested time ±2s under normal load.  
6. Repo contains live API secrets or Lab write credentials.  

## Smallest test

```bash
python3 -m py_compile projects/Natoshi-Assistant/app/matrix_terminal.py
# with display + ollama:
./projects/Natoshi-Assistant/app/launch.sh
# UI: send "hi", /search test, /remind 1m ping
```

## Method and environment

- Language: Python 3 + Tkinter (stdlib GUI)  
- Local models: Ollama HTTP API  
- Cloud models: optional env `XAI_API_KEY` / `DEEPSEEK_API_KEY` / `OPENAI_API_KEY`  
- Search: DuckDuckGo HTML scrape (no key; brittle by nature)  
- Reminders: in-process scheduler + `notify-send` when available  
- Host: Linux desktop (Fedora-class), Wayland/X11 via Tk  

## Results

See `RESULTS_2026-07-25.md`.

## Limitations and non-claims

- Not Lab-canonical; `status_authority: NONE`  
- Not FORGE, not Hermes product, not a security product  
- Not a hardened multi-user app  
- Web search HTML parsing will break when DDG markup changes  
- Cloud providers require operator-supplied keys in env, never git  
- “Always on top” behavior varies by compositor  
- Does not claim model identity verification  
- Does not replace calendar/evolution system alarms; those are unrelated desktop services  

## Evidence

- Source: `app/matrix_terminal.py`  
- Launch: `app/launch.sh`  
- First-cut results: `RESULTS_2026-07-25.md`  

## Lesson

Ship a thin always-on-top personal overlay as a **sandbox experiment** with a clear improvement backlog, instead of bolting reminders onto adversarial “alarm setup” machinery.

## Related cancelled work

Security-alarm setup scripts under `/tmp` and associated Codex sandbox setup jobs were terminated and temp artifacts removed (2026-07-25). This experiment does **not** continue that line.
