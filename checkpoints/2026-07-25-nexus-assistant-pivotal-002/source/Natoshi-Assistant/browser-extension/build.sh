#!/usr/bin/env bash
set -euo pipefail

browser="${1:-}"
case "$browser" in
  chromium|firefox) ;;
  *)
    echo "usage: ./build.sh chromium|firefox" >&2
    exit 2
    ;;
esac

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
dist_dir="$script_dir/dist/$browser"
mkdir -p "$dist_dir"

cp "$script_dir/manifest.$browser.json" "$dist_dir/manifest.json"
cp "$script_dir/background.js" "$dist_dir/background.js"
cp "$script_dir/popup.html" "$dist_dir/popup.html"
cp "$script_dir/popup.css" "$dist_dir/popup.css"
cp "$script_dir/popup.js" "$dist_dir/popup.js"

echo "Built $dist_dir"

