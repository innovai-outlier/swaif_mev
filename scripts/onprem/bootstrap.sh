#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/common.sh"

ensure_jwt_secret() {
  local env_file="$1"
  local generated_secret
  generated_secret="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"

  local current_value=""
  if grep -q '^JWT_SECRET_KEY=' "$env_file"; then
    current_value="$(grep '^JWT_SECRET_KEY=' "$env_file" | tail -n1 | cut -d'=' -f2-)"
  fi

  if [[ -z "$current_value" || "$current_value" == "CHANGE_ME" || "$current_value" == "GENERATE_ME" || "$current_value" == "your-secret-key-change-in-production" ]]; then
    if grep -q '^JWT_SECRET_KEY=' "$env_file"; then
      awk -v new_secret="$generated_secret" '
        BEGIN { replaced=0 }
        /^JWT_SECRET_KEY=/ {
          if (!replaced) {
            print "JWT_SECRET_KEY=" new_secret
            replaced=1
          }
          next
        }
        { print }
        END { if (!replaced) print "JWT_SECRET_KEY=" new_secret }
      ' "$env_file" > "$env_file.tmp"
      mv "$env_file.tmp" "$env_file"
    else
      printf '\nJWT_SECRET_KEY=%s\n' "$generated_secret" >> "$env_file"
    fi
    echo "==> JWT_SECRET_KEY gerada e salva em $env_file"
  else
    echo "==> JWT_SECRET_KEY já configurada em $env_file"
  fi
}

if [[ ! -f "$ONPREM_ENV_FILE" ]]; then
  cp "$ONPREM_ENV_EXAMPLE" "$ONPREM_ENV_FILE"
  echo "==> Criado: $ONPREM_ENV_FILE"
else
  echo "==> Já existe: $ONPREM_ENV_FILE"
fi

ensure_jwt_secret "$ONPREM_ENV_FILE"

ensure_runtime_dirs
echo "==> Runtime: $ONPREM_RUNTIME_DIR"
echo "==> Pronto. Próximo passo: ./scripts/run.sh --mode onprem up"
