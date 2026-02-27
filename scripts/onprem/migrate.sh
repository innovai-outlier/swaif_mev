#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

load_onprem_env

cd "$ROOT_DIR/services/api"
alembic upgrade head

echo "==> Migrações aplicadas (on-prem)."
