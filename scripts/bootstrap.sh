#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_DIR="$ROOT_DIR/infra/compose"
ENV_FILE="$COMPOSE_DIR/.env"
ENV_EXAMPLE="$COMPOSE_DIR/.env.example"

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

echo "==> Pronto. Próximo passo: ./scripts/up.sh"
