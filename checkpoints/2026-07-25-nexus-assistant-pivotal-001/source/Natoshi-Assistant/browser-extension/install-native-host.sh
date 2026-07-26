#!/usr/bin/env bash
set -euo pipefail

browser="${1:-}"
extension_id="${2:-}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
host_path="$script_dir/native_host.py"
host_name="org.nexus_assistant.browser"

case "$browser" in
  firefox)
    manifest_dir="${HOME}/.mozilla/native-messaging-hosts"
    manifest_path="$manifest_dir/$host_name.json"
    mkdir -p "$manifest_dir"
    python3 -c '
import json, os, sys
path, host = sys.argv[1:3]
print(json.dumps({
    "name": "org.nexus_assistant.browser",
    "description": "NEXUS bounded browser evidence organ",
    "path": os.path.abspath(host),
    "type": "stdio",
    "allowed_extensions": ["nexus-assistant@local"],
}, indent=2))
' "$manifest_path" "$host_path" > "$manifest_path"
    ;;
  chromium)
    if [[ ! "$extension_id" =~ ^[a-p]{32}$ ]]; then
      echo "usage: ./install-native-host.sh chromium ACTUAL_32_CHAR_EXTENSION_ID" >&2
      exit 2
    fi
    manifest_dir="${HOME}/.config/chromium/NativeMessagingHosts"
    manifest_path="$manifest_dir/$host_name.json"
    mkdir -p "$manifest_dir"
    python3 -c '
import json, os, sys
path, host, extension_id = sys.argv[1:4]
print(json.dumps({
    "name": "org.nexus_assistant.browser",
    "description": "NEXUS bounded browser evidence organ",
    "path": os.path.abspath(host),
    "type": "stdio",
    "allowed_origins": [f"chrome-extension://{extension_id}/"],
}, indent=2))
' "$manifest_path" "$host_path" "$extension_id" > "$manifest_path"
    ;;
  *)
    echo "usage: ./install-native-host.sh firefox|chromium [extension-id]" >&2
    exit 2
    ;;
esac

chmod 600 "$manifest_path"
chmod +x "$host_path"
echo "Installed $manifest_path"

