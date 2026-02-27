#!/usr/bin/env bash
set -euo pipefail

PLATFORM="$(uname -s)"
INSTALL_DIR="${1:-/opt/swaif_mev}"
API_PORT="${API_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3000}"

render() {
  local template="$1"
  local target="$2"
  sed \
    -e "s|@INSTALL_DIR@|$INSTALL_DIR|g" \
    -e "s|@API_PORT@|$API_PORT|g" \
    -e "s|@WEB_PORT@|$WEB_PORT|g" \
    "$template" > "$target"
}

if [[ "$PLATFORM" == "Linux" ]]; then
  for unit in api worker web; do
    render "installer/templates/services/systemd/swaif-${unit}.service" "/etc/systemd/system/swaif-${unit}.service"
    systemctl daemon-reload
    systemctl enable --now "swaif-${unit}.service"
  done
  echo "systemd services registered."
elif [[ "$PLATFORM" == "Darwin" ]]; then
  mkdir -p "$HOME/Library/LaunchAgents"
  for svc in api web worker; do
    target="$HOME/Library/LaunchAgents/com.swaif.mev.${svc}.plist"
    render "installer/templates/services/launchd/com.swaif.mev.${svc}.plist" "$target"
    launchctl unload "$target" >/dev/null 2>&1 || true
    launchctl load "$target"
  done
  echo "launchd agents registered."
else
  echo "Unsupported Unix platform: $PLATFORM"
  exit 1
fi
