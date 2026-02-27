#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/api.sh" status
"$SCRIPT_DIR/worker.sh" status
"$SCRIPT_DIR/web.sh" status
