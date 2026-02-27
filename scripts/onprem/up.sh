#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/api.sh" start
"$SCRIPT_DIR/worker.sh" start
"$SCRIPT_DIR/web.sh" start

"$SCRIPT_DIR/status.sh"
echo "==> Stack on-prem no ar."
