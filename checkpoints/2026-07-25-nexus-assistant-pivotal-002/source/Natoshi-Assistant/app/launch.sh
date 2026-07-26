#!/usr/bin/env bash
# Launch the NEXUS Linux project cockpit.
set -euo pipefail
umask 077
app_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$app_dir"
export PYTHONUNBUFFERED=1

# Export optional provider keys. The NEXUS file wins over the legacy path.
nexus_config_root="${XDG_CONFIG_HOME:-$HOME/.config}/nexus-assistant"
for provider_env in \
  "$HOME/.config/matrix-terminal.env" \
  "$nexus_config_root/env"
do
  if [[ -f "$provider_env" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$provider_env"
    set +a
  fi
done

exec python3 "$app_dir/matrix_terminal.py"
