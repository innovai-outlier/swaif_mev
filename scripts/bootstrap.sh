#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_DIR="$ROOT_DIR/infra/compose"
ENV_FILE="$COMPOSE_DIR/.env"
ENV_EXAMPLE="$COMPOSE_DIR/.env.example"

ensure_jwt_secret() {
  local env_file="$1"
  local generated_secret
  generated_secret="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"

  if [[ ! -f "$env_file" ]]; then
    echo "Arquivo de ambiente não encontrado para secret: $env_file"
    exit 1
  fi

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

echo "==> Verificando Docker..."
command -v docker >/dev/null 2>&1 || { echo "Docker não encontrado."; exit 1; }
docker version >/dev/null 2>&1 || { echo "Docker não está respondendo. Inicie o Docker Desktop."; exit 1; }

echo "==> Verificando Docker Compose..."
docker compose version >/dev/null 2>&1 || { echo "docker compose não disponível."; exit 1; }

echo "==> Preparando .env..."
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$ENV_EXAMPLE" "$ENV_FILE"
  echo "Criado: $ENV_FILE"
else
  echo "Já existe: $ENV_FILE"
fi

ensure_jwt_secret "$ENV_FILE"

echo "==> Pronto. Próximo passo: ./scripts/up.sh"
