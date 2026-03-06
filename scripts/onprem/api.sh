#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

ACTION="${1:-start}"

case "$ACTION" in
  start)
    start_service "api" "$ROOT_DIR/services/api" "${API_START_CMD:-uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT:-8000}}"
    ;;
  stop)
    stop_service "api"
    ;;
  status)
    status_service "api"
    ;;
  *)
    echo "Uso: $0 {start|stop|status}"
    exit 1
    ;;
esac
