# Public checkpoint exclusions

This file records deliberate non-actions. “Back up everything” is interpreted as
all public-safe project source and documentation needed to understand and rebuild
this checkpoint—not every byte readable by the local account.

Excluded:

- API keys, access tokens, passwords, cookies, private keys and Linux Secret
  Service entries;
- NEXUS local configuration, keyring values, encrypted LOOM vault data and
  decrypted session records;
- private messages, raw personal transcripts, browser history, clipboard
  history, voice recordings and screen recordings;
- `.git` object databases and unrelated repository content;
- environment files, machine identifiers, process environments and local
  routing caches;
- Python/pytest caches, bytecode and rebuildable browser `dist/` output;
- dependencies, virtual environments and package caches;
- source archives or third-party binaries not required by this project tree.

The source scan before publication searched for common private-key, GitHub,
OpenAI-style, Google-style, AWS-style and bearer-token signatures. Hits were
limited to defensive regular expressions and synthetic test fixtures. Pattern
scanning is not a proof that no sensitive information exists; this manifest
makes the review boundary explicit.

No excluded secret was intentionally read into the checkpoint, committed, or
printed to build the public backup.

## Checkpoint 002 note

Same exclusion policy as 001. Added dual-seat bus logs are public process
metadata only (no conversation full-text dumps of private seats beyond the
published RESULTS summary).
