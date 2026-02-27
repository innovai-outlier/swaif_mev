#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/web.sh" stop
"$SCRIPT_DIR/worker.sh" stop
"$SCRIPT_DIR/api.sh" stop

echo "==> Stack on-prem desligada."
