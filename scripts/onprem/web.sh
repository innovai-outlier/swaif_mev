#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

ACTION="${1:-start}"

case "$ACTION" in
  start)
    start_service "web" "$ROOT_DIR/services/web" "npm run build && next start -p ${WEB_PORT:-3000}"
    ;;
  stop)
    stop_service "web"
    ;;
  status)
    status_service "web"
    ;;
  *)
    echo "Uso: $0 {start|stop|status}"
    exit 1
    ;;
esac
