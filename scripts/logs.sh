#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_DIR="$ROOT_DIR/infra/compose"

docker compose -f "$COMPOSE_DIR/docker-compose.yml" --env-file "$COMPOSE_DIR/.env" logs -f --tail=200
