#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

ensure_runtime_dirs

tail -n 200 -f \
  "$(service_log_file api)" \
  "$(service_log_file worker)" \
  "$(service_log_file web)"
