#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${1:-/opt/swaif_mev}"
PLATFORM="$(uname -s)"

if [[ "$PLATFORM" == "Linux" ]]; then
  for unit in swaif-api swaif-web swaif-worker; do
    systemctl disable --now "$unit.service" >/dev/null 2>&1 || true
    rm -f "/etc/systemd/system/$unit.service"
  done
  systemctl daemon-reload
elif [[ "$PLATFORM" == "Darwin" ]]; then
  for svc in api web worker; do
    plist="$HOME/Library/LaunchAgents/com.swaif.mev.${svc}.plist"
    launchctl unload "$plist" >/dev/null 2>&1 || true
    rm -f "$plist"
  done
fi

rm -rf "$INSTALL_DIR"
echo "Uninstall complete for $INSTALL_DIR"
