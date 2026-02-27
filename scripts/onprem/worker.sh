#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

ACTION="${1:-start}"

case "$ACTION" in
  start)
    start_service "worker" "$ROOT_DIR/services/worker" "${WORKER_START_CMD:-python -m app.main}"
    ;;
  stop)
    stop_service "worker"
    ;;
  status)
    status_service "worker"
    ;;
  *)
    echo "Uso: $0 {start|stop|status}"
    exit 1
    ;;
esac
