# Notification repair, Natoshi-Assistant review, and Lab-history report

**status_authority:** `NONE`  
**Date:** 2026-07-25 (Europe/London)  
**Seat:** Codex  
**Lab touched:** read-only; no Lab files changed  
**Sandbox state:** local uncommitted changes on
`sandbox/experiment/natoshi-assistant-matrix-terminal`

## Operator request

Make a recurring desktop reminder appear above other applications without
interrupting typing, remove the extra permission/accept-style prompt and
top-of-screen alert, inspect Grok's Natoshi-Assistant, inspect the Lab's full
history, and report the result.

## Outcome

The typing interruption had two concrete code-level causes:

1. The standalone security reminder explicitly presented itself and requested
   keyboard focus.
2. Natoshi-Assistant explicitly called `focus_force()` when an in-app reminder
   fired, then also emitted a critical `notify-send` banner.

Both paths are now designed to show an always-above, non-focusable overlay.
Natoshi-Assistant no longer raises its entire chat window for a reminder, and
the duplicate GNOME banner is disabled by default. The older five-minute
Focus/Breathe autostart loop was disabled and its running process was stopped.

The overlays remain dismissible with the mouse and close automatically.
Keyboard shortcuts do not dismiss them because that would require taking
keyboard focus away from the application in which the operator is typing.

Linux security boundaries remain intact: an ordinary reminder is not made able
to cover the lock screen or protected system/security dialogs.

## Desktop reminder evidence and changes

### Sources found

- `~/.config/autostart/screen-reminders.desktop`
  - launched `~/.local/bin/screen_reminders.sh`;
  - that script slept 300 seconds and called `notify-send` for alternating
    Focus and Breathe banners.
- `~/.config/systemd/user/security-issues-alarm.timer`
  - journal evidence shows a five-minute cadence at 11:40;
  - its file was changed at 12:04 to a 150-second cadence.
- `~/bin/security-issues-alarm-ui.py`
  - used `present()`, `present_with_time()`, and `grab_focus()`;
  - those calls invite GNOME focus-stealing prevention and can lead to an
    additional “app is ready” or permission-style surface.
- Natoshi-Assistant `app/matrix_terminal.py`
  - used `focus_force()` and a critical `notify-send` for every in-app
    reminder.

### Changes made

- `~/bin/security-issues-alarm-ui.py`
  - changed to a decoration-free notification-type window;
  - remains always above and is sticky across workspaces;
  - rejects keyboard focus and never calls `present()` or `grab_focus()`;
  - dismisses by mouse or timeout.
- `~/.config/autostart/screen-reminders.desktop`
  - set disabled and hidden;
  - the matching live legacy process was stopped and verified absent.
- Natoshi-Assistant
  - removed `focus_force()` from the reminder path;
  - moved reminder delivery onto the existing Tk main-thread queue;
  - added a borderless, topmost Matrix reminder overlay;
  - stopped deiconifying/raising the full chat window;
  - made the duplicate system notification opt-in through
    `system_reminder_notifications` (default `false`);
  - documented the behavior and security boundary.
- Live installation
  - applied the same source change to `~/Projects/MatrixTerminal`;
  - restarted it as `natoshi-assistant.service`;
  - verified one updated Python process remained active.

### Verification

- `python3 -m py_compile ~/bin/security-issues-alarm-ui.py` — PASS
- `bash -n ~/bin/security-issues-alarm.sh` — PASS
- source scan confirms no `present()`, `present_with_time()`, or
  `grab_focus()` remains in the standalone reminder.
- `python3 -m py_compile app/matrix_terminal.py` — PASS
- `bash -n app/launch.sh` — PASS
- non-GUI reminder-engine test — PASS; event fired once and the duplicate
  system notification path stayed off.
- live-process check for the legacy `screen_reminders.sh` loop — absent.
- `natoshi-assistant.service` — active and running the updated live source as
  one process.
- Full graphical compositor test — NOT AUTOMATED because `xvfb-run` is not
  installed and a synthetic display cannot prove GNOME/Wayland stacking
  behavior. The next real reminder is the final visual confirmation.

## Natoshi-Assistant assessment

### What it is

The first cut is a 1,000-line single-file Python/Tk desktop overlay with:

- draggable/resizable always-on-top Matrix UI;
- Ollama and OpenAI-compatible provider adapters;
- a DuckDuckGo HTML search path;
- streamed chat output;
- in-process reminders;
- local configuration, window state, and chat-history files.

It is correctly isolated in Experimental-Sandbox with `status_authority: NONE`.
The project explicitly disclaims Lab authority, product hardening, verified
model identity, and silent Lab writes.

### What is good

- It is small enough to inspect.
- Model output has no shell-execution path.
- API keys are referenced by environment-variable name rather than embedded.
- Search results are identified as untrusted input.
- The reminder and provider paths fail locally rather than claiming Lab state.
- The project has an experiment claim, falsifier, limitations, handoff, and
  ranked improvement list.

### Important remaining weaknesses

1. Reminders are not persisted and disappear when the app exits.
2. Configuration and chat history live beside source rather than under an XDG
   state/config directory.
3. `/remind 25:99 ...` can raise a `ValueError`; clock bounds need validation.
4. Relative reminder parsing accepts partial malformed strings because it uses
   `findall` without requiring a full match.
5. DuckDuckGo HTML scraping is brittle and search-result prompt injection is
   only documented, not technically contained.
6. Cloud model lists are static guesses and may become stale.
7. There is no automated GUI/focus/stacking test.
8. The optional `notify-send` code still uses critical urgency when explicitly
   enabled; that is intentional opt-in behavior now, not the default.

## Lab full-history review

### Scope

I inspected root entry instructions, current control-plane files, skills
routing, RAM coordination files, the current canonical-status declaration, and
all 603 commit headers reachable from all local refs. “Full history” here means
the complete commit chronology and its declared subjects, not reading the full
diff and every historical file body for all 603 commits.

Repository examined: `Natoshi-moto/Lab`.

- Reachable commits across all refs: **603**
- Dates represented: **2026-07-12 through 2026-07-25**
- Merge commits: **120**
- Authors as recorded:
  - Natoshi-moto: 523
  - Nexus Bootstrap: 78
  - dependabot[bot]: 1
  - Lab PLAY: 1
- Tags: five early freeze/baseline/handoff tags, including
  `baseline-001` at the R001 provenance-hardened baseline.

### Timeline

1. **R001–R010: foundation and hostile audit hardening**
   - private/public research-lab bootstrap;
   - immutable route/audit provenance;
   - secret scanning and size-exclusion visibility;
   - audit-pack and snapshot/tree binding;
   - remediation, retest, adjudication, and typed assurance gates.

2. **R011–R016: bounded real-work and synthetic custody**
   - a hard vertical slice with competing identity-cost models;
   - bounded work exchange;
   - conserved synthetic claims;
   - crash-consistent settlement/durable transcript work;
   - controller custody schemas, kernels, attack tests, CI evidence, and
     bounded promotion records.

3. **R017–R018: replication and post-quantum research**
   - deterministic replication and fork evidence;
   - pinned Ed25519 replica attestations;
   - process-separated partition/healing demonstrations;
   - hybrid post-quantum admission experiments and isolated dependency work;
   - OPEN-GATE declared as a public protocol bet.

4. **Beneficial Genesis and economics scrutiny**
   - synthetic protocol/evidence design;
   - multiple red-team, breaker, repair, clean-room retest, mechanism, technical,
     tribunal, epistemic, and culture-review tracks;
   - a canonical research checkpoint explicitly retained an anti-real-world-
     value boundary.

5. **NOTED / Project OS / break sessions**
   - host bridge, diagnostic suite, agent prompt import, and layout work;
   - sovereignty and membrane/adversary proposals;
   - BREAK sessions recorded T-01 same-origin storage reach and CARD-11
     plaintext-at-rest failures;
   - an emergency stop and three-seat truth audit followed;
   - recovery, hygiene, backups, session-close, and research-assessment
     clearance were installed.

6. **Governance and experimental separation**
   - round-close and epistemic-performance publications;
   - user disclosures, RAM, personas, Whoopsie log, distrust/proof registers;
   - public board and experimental work moved toward Experimental-Sandbox;
   - merge authorization was repaired and hardened;
   - the owner plain-language gate was added.

7. **Latest all-ref work**
   - closed-world economy invariant review;
   - a proposed T-01 iframe fix;
   - a subsequent executed T-01b finding that the pop-out route reopened the
     storage boundary.

### Current-state caution

The official remote `origin/main` inspected at
`46498a96c709a96e86297c09abe0e65efb1100f8` still says:

- `RESEARCH_ASSESSMENT_CLEARED`;
- operator must select the next track;
- product launch/ship language remains gated;
- T-01/G-01 and CARD-11 remain red;
- no real-world token/economic value;
- multi-seat agreement is not independence.

The `/home/anon/Lab` working tree itself is not on `main`; it is on
`fable/t01-storage-boundary-001` at
`3599ea3be938cb731a36495081805664ce3c4264`. That branch contains five commits
beyond `origin/main`, ending in the executed T-01b pop-out failure. Those branch
results are evidence/proposal state, not an official main closeout.

### Overall judgment

The Lab history shows unusually strong attention to provenance, adversarial
testing, typed evidence, reversible proposal boundaries, and explicit
distrust. It also shows repeated control-plane churn, correlated multi-seat
authorship, rapid branch/authorization resynchronization, and a tendency for
new product surfaces to outrun the current scoreboard. The newest T-01b result
is a good example: a narrow iframe repair did not close the broader storage
boundary because another route remained.

Natoshi-Assistant belongs where it currently lives: Experimental-Sandbox. It is
a useful local prototype, but its reminder reliability, parser validation,
state paths, search containment, and GUI testing are not ready for Lab
promotion or product/security claims.

## Files actually inspected

- Desktop:
  - `~/.config/autostart/screen-reminders.desktop`
  - `~/.local/bin/screen_reminders.sh`
  - `~/.config/systemd/user/security-issues-alarm.{timer,service}`
  - `~/bin/security-issues-alarm.sh`
  - `~/bin/security-issues-alarm-ui.py`
  - relevant user-journal entries and reminder history
- Live Natoshi installation:
  - `~/Projects/MatrixTerminal/matrix_terminal.py`
  - `~/Projects/MatrixTerminal/launch.sh`
  - `~/.local/share/applications/matrix-terminal.desktop`
- Natoshi-Assistant:
  - all nine tracked project files present at review time, including the full
    `app/matrix_terminal.py`
- Lab:
  - `AGENTS.md`, `README_START_HERE.md`, `STATUS.json`, `NEXT_ACTION.md`
  - essential skills index
  - `RAM/BOARD.md`, `RAM/PROTOCOL.md`, `RAM/recovery/LAST.md`
  - all 603 reachable commit headers and aggregate history statistics
  - `origin/main` status/next-action content
  - current feature-branch commits and changed-path list

## Not done

- No Lab file was edited, committed, pushed, merged, or promoted.
- No Natoshi-Assistant commit or push was made.
- No system permission was set to “always accept”; the design removes the need
  for that permission instead.
- No lock-screen or security-dialog safeguard was bypassed.

## Follow-up: Wayland stacking, global opener, and automatic APIs

After live use showed that GNOME/Wayland ignored the standalone GTK window's
always-above hint:

- the security timer was returned to a five-minute cadence;
- its separate application window was removed from the active path;
- it now emits one critical GNOME-owned `MATRIX REMINDER` banner, which does
  not request keyboard focus or produce an additional app-ready window;
- Natoshi-Assistant was installed as a persistent user service;
- `Super` + `Shift` + `M` was registered as a global open/raise shortcut using
  a direct `SIGUSR1` message to the single app process;
- `auto` provider mode was added and made the default;
- automatic order is DeepSeek, XAI, OpenAI, Ollama, custom;
- fallback is sequential and stops on the first successful response.

No external API key names were present in the user service environment,
common shell profiles, or `~/.config/matrix-terminal.env` at inspection time.
The code path and a synthetic DeepSeek-first routing test passed, but a real
DeepSeek call remains unverified until `DEEPSEEK_API_KEY` is configured
locally.
