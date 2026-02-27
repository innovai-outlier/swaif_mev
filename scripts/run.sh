#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="docker"

usage() {
  cat <<USAGE
Uso: ./scripts/run.sh [--mode docker|onprem] <comando>

Comandos:
  bootstrap
  up
  down
  logs
  health
  migrate
  seed
  seed-admin
  seed-comprehensive
  status

Exemplos:
  ./scripts/run.sh --mode docker up
  ./scripts/run.sh --mode onprem bootstrap
  ./scripts/run.sh --mode onprem migrate
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

COMMAND="${1:-up}"

case "$MODE" in
  docker)
    case "$COMMAND" in
      bootstrap) "$ROOT_DIR/scripts/bootstrap.sh" ;;
      up) "$ROOT_DIR/scripts/up.sh" ;;
      down) "$ROOT_DIR/scripts/down.sh" ;;
      logs) "$ROOT_DIR/scripts/logs.sh" ;;
      health) "$ROOT_DIR/scripts/health.sh" ;;
      migrate) "$ROOT_DIR/scripts/migrate.sh" ;;
      seed) "$ROOT_DIR/scripts/seed.sh" ;;
      seed-admin)
        docker compose -f "$ROOT_DIR/infra/compose/docker-compose.yml" --env-file "$ROOT_DIR/infra/compose/.env" exec -T api python -m app.seed_admin
        ;;
      seed-comprehensive)
        docker compose -f "$ROOT_DIR/infra/compose/docker-compose.yml" --env-file "$ROOT_DIR/infra/compose/.env" exec -T api python -m app.seed_comprehensive
        ;;
      status)
        docker compose -f "$ROOT_DIR/infra/compose/docker-compose.yml" --env-file "$ROOT_DIR/infra/compose/.env" ps
        ;;
      *)
        echo "Comando inválido para modo docker: $COMMAND"
        usage
        exit 1
        ;;
    esac
    ;;
  onprem)
    case "$COMMAND" in
      bootstrap) "$ROOT_DIR/scripts/onprem/bootstrap.sh" ;;
      up) "$ROOT_DIR/scripts/onprem/up.sh" ;;
      down) "$ROOT_DIR/scripts/onprem/down.sh" ;;
      logs) "$ROOT_DIR/scripts/onprem/logs.sh" ;;
      health) "$ROOT_DIR/scripts/health.sh" ;;
      migrate) "$ROOT_DIR/scripts/onprem/migrate.sh" ;;
      seed) "$ROOT_DIR/scripts/onprem/seed.sh" ;;
      seed-admin) "$ROOT_DIR/scripts/onprem/seed_admin.sh" ;;
      seed-comprehensive) "$ROOT_DIR/scripts/onprem/seed_comprehensive.sh" ;;
      status) "$ROOT_DIR/scripts/onprem/status.sh" ;;
      *)
        echo "Comando inválido para modo onprem: $COMMAND"
        usage
        exit 1
        ;;
    esac
    ;;
  *)
    echo "Modo inválido: $MODE"
    usage
    exit 1
    ;;
esac
