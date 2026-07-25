# Paste-Bin

**Visibility:** PUBLIC

**License:** MIT

**Status authority:** `NONE`

This repository is Natoshi-moto's public, MIT-licensed checkpoint paste bin.
Pivotal work states can be copied here so that useful source, documentation,
tests, and provenance survive outside a single machine or working branch.

A checkpoint is:

- a byte snapshot of the explicitly listed public-safe files;
- an evidence artifact with source-repository and working-state metadata;
- independently hashable;
- allowed to be incomplete, experimental, dirty, or later superseded.

A checkpoint is **not**:

- project canon;
- a release or security certification;
- permission to merge it into another repository;
- proof that every claim in its documentation is true;
- a place for API keys, private messages, local vaults, credentials, or raw
  personal session data.

## Checkpoints

| Checkpoint | Captured | Subject | Evidence |
|---|---|---|---|
| [`2026-07-25-nexus-assistant-pivotal-002`](checkpoints/2026-07-25-nexus-assistant-pivotal-002/) | 2026-07-25 dual-seat | NEXUS Assistant committed spine + bus log + re-verified tests | 123 app + 4 native-host; source HEAD after public sandbox commit |
| [`2026-07-25-nexus-assistant-pivotal-001`](checkpoints/2026-07-25-nexus-assistant-pivotal-001/) | 2026-07-25 17:33 BST | NEXUS Assistant cockpit, Room/Drop/LOOM/Forge/connectivity work | 123 Python app tests + 4 native-host tests; Chromium and Firefox builds |

## Checkpoint contract

Each checkpoint should contain:

1. a `CHECKPOINT.md` stating the exact source and nonclaims;
2. the public-safe source/artifact tree;
3. `MANIFEST.sha256` covering the copied source bytes;
4. `PUBLICATION_EXCLUSIONS.md` explaining what was deliberately left local;
5. test results described precisely enough to rerun.

The MIT licence covers material committed here unless a checkpoint explicitly
identifies third-party material under another licence. A public copy does not
waive privacy, trademark, patent, or third-party rights that the committer does
not own.
