#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

if [[ ! -f "$ONPREM_ENV_FILE" ]]; then
  cp "$ONPREM_ENV_EXAMPLE" "$ONPREM_ENV_FILE"
  echo "==> Criado: $ONPREM_ENV_FILE"
else
  echo "==> Já existe: $ONPREM_ENV_FILE"
fi

ensure_runtime_dirs
echo "==> Runtime: $ONPREM_RUNTIME_DIR"
echo "==> Pronto. Próximo passo: ./scripts/run.sh --mode onprem up"
