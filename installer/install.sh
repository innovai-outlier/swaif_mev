#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${1:-/opt/swaif_mev}"
PROFILE="${PROFILE:-production}"
CONFIG_DIR="$INSTALL_DIR/config"

mkdir -p "$CONFIG_DIR"
python3 installer/wizard.py --profile "$PROFILE" --output-dir "$CONFIG_DIR"

export API_PORT="$(awk -F= '/^API_PORT=/{print $2}' "$CONFIG_DIR/api.env")"
export WEB_PORT="$(awk -F= '/^WEB_PORT=/{print $2}' "$CONFIG_DIR/web.env")"

bash installer/scripts/register_services.sh "$INSTALL_DIR"
echo "Installation complete."
