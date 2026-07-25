#!/usr/bin/env bash
# publish-checkpoint.sh — snapshot public-safe NEXUS Assistant bytes into Paste-Bin
# and push the public branch.
#
# Usage:
#   scripts/publish-checkpoint.sh <checkpoint-id> <one-line-significance>
# Example:
#   scripts/publish-checkpoint.sh 2026-07-25-nexus-assistant-pivotal-003 "LOOM live falsifier green"
set -euo pipefail

ID="${1:?checkpoint id required, e.g. 2026-07-25-nexus-assistant-pivotal-003}"
SIGNIFICANCE="${2:?significance blurb required}"
SRC_ROOT="${NEXUS_SRC:-$HOME/Projects/Experimental-Sandbox/projects/Natoshi-Assistant}"
PB_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CP="$PB_ROOT/checkpoints/$ID"
SRC_REPO="$(cd "$SRC_ROOT/../.." && pwd)"
SRC_HEAD="$(git -C "$SRC_REPO" rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
TS="$(date -Iseconds)"

if [[ ! -d "$SRC_ROOT" ]]; then
  echo "missing source: $SRC_ROOT" >&2
  exit 1
fi

rm -rf "$CP"
mkdir -p "$CP/source"
rsync -a \
  --exclude '__pycache__/' \
  --exclude '.pytest_cache/' \
  --exclude '*.pyc' \
  --exclude 'dist/' \
  --exclude '.env' \
  --exclude '.env.*' \
  --exclude 'config.json' \
  --exclude 'history.jsonl' \
  --exclude 'window_state.json' \
  "$SRC_ROOT/" "$CP/source/Natoshi-Assistant/"

( cd "$CP" && find source -type f -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256 )
FILE_COUNT="$(find "$CP/source" -type f | wc -l)"

cat > "$CP/CHECKPOINT.md" <<EOF
# Checkpoint \`$ID\`

**Captured:** \`$TS\`
**Checkpoint status:** \`PUBLIC_BACKUP / NONCANONICAL / NOT_A_RELEASE\`
**Status authority:** \`NONE\`
**Significance:** $SIGNIFICANCE

| Field | Value |
|---|---|
| Source repository | \`https://github.com/Natoshi-moto/Experimental-Sandbox\` |
| Source subdirectory | \`projects/Natoshi-Assistant\` |
| Source HEAD | \`$SRC_HEAD\` |
| Files | $FILE_COUNT |

Verify:

\`\`\`bash
sha256sum -c MANIFEST.sha256
\`\`\`
EOF

if [[ -f "$PB_ROOT/checkpoints/2026-07-25-nexus-assistant-pivotal-001/PUBLICATION_EXCLUSIONS.md" ]]; then
  cp "$PB_ROOT/checkpoints/2026-07-25-nexus-assistant-pivotal-001/PUBLICATION_EXCLUSIONS.md" \
    "$CP/PUBLICATION_EXCLUSIONS.md"
else
  printf 'See repository README for exclusion policy.\n' > "$CP/PUBLICATION_EXCLUSIONS.md"
fi

# Chain append
CHAIN="$PB_ROOT/checkpoints/CHAIN.md"
if [[ ! -f "$CHAIN" ]]; then
  cat > "$CHAIN" <<'EOF'
# Public checkpoint chain

**status_authority:** `NONE`
EOF
fi
if ! grep -q "$ID" "$CHAIN"; then
  printf '| %s | %s |\n' "$ID" "$SIGNIFICANCE" >> "$CHAIN"
fi

# README table row if missing
if ! grep -q "$ID" "$PB_ROOT/README.md"; then
  ROW="| [\`$ID\`](checkpoints/$ID/) | $(date +%Y-%m-%d) | $SIGNIFICANCE | see CHECKPOINT.md |"
  # insert after header separator of checkpoints table if present
  if grep -q 'pivotal-001' "$PB_ROOT/README.md"; then
    sed -i "/pivotal-001/i $ROW" "$PB_ROOT/README.md" || true
  else
    printf '\n%s\n' "$ROW" >> "$PB_ROOT/README.md"
  fi
fi

cd "$PB_ROOT"
git add checkpoints README.md
if git diff --cached --quiet; then
  echo "nothing new to commit"
  exit 0
fi
git commit -m "Add public checkpoint $ID: $SIGNIFICANCE"
git push -u origin HEAD
echo "PUBLISHED $ID @ $(git rev-parse --short HEAD)"
echo "URL: https://github.com/Natoshi-moto/Paste-Bin/tree/$(git rev-parse --abbrev-ref HEAD)/checkpoints/$ID"
