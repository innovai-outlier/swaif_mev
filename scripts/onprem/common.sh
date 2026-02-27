#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ONPREM_ENV_FILE="${ONPREM_ENV_FILE:-$ROOT_DIR/config/.env.onprem}"
ONPREM_ENV_EXAMPLE="$ROOT_DIR/config/.env.onprem.example"
ONPREM_RUNTIME_DIR="${ONPREM_RUNTIME_DIR:-$ROOT_DIR/.runtime/onprem}"
ONPREM_PID_DIR="$ONPREM_RUNTIME_DIR/pids"
ONPREM_LOG_DIR="$ONPREM_RUNTIME_DIR/logs"

load_onprem_env() {
  if [[ ! -f "$ONPREM_ENV_FILE" ]]; then
    echo "Arquivo de ambiente não encontrado: $ONPREM_ENV_FILE"
    echo "Dica: cp $ONPREM_ENV_EXAMPLE $ONPREM_ENV_FILE"
    exit 1
  fi

  set -a
  # shellcheck disable=SC1090
  source "$ONPREM_ENV_FILE"
  set +a
}

ensure_runtime_dirs() {
  mkdir -p "$ONPREM_PID_DIR" "$ONPREM_LOG_DIR"
}

service_pid_file() {
  local service_name="$1"
  echo "$ONPREM_PID_DIR/$service_name.pid"
}

service_log_file() {
  local service_name="$1"
  echo "$ONPREM_LOG_DIR/$service_name.log"
}

is_pid_running() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1
}

start_service() {
  local service_name="$1"
  local service_dir="$2"
  local command="$3"

  ensure_runtime_dirs
  load_onprem_env

  local pid_file
  local log_file
  pid_file="$(service_pid_file "$service_name")"
  log_file="$(service_log_file "$service_name")"

  if [[ -f "$pid_file" ]]; then
    local existing_pid
    existing_pid="$(cat "$pid_file")"
    if is_pid_running "$existing_pid"; then
      echo "==> $service_name já está rodando (PID $existing_pid)."
      return 0
    fi
    echo "==> Removendo PID antigo de $service_name ($existing_pid)."
    rm -f "$pid_file"
  fi

  echo "==> Iniciando $service_name..."
  (
    cd "$service_dir"
    nohup bash -lc "$command" >>"$log_file" 2>&1 &
    echo $! >"$pid_file"
  )

  local new_pid
  new_pid="$(cat "$pid_file")"
  echo "==> $service_name iniciado (PID $new_pid). Logs: $log_file"
}

stop_service() {
  local service_name="$1"
  local pid_file
  pid_file="$(service_pid_file "$service_name")"

  if [[ ! -f "$pid_file" ]]; then
    echo "==> $service_name não está em execução (sem PID file)."
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"

  if ! is_pid_running "$pid"; then
    echo "==> $service_name já não está rodando (PID $pid). Limpando PID file."
    rm -f "$pid_file"
    return 0
  fi

  echo "==> Parando $service_name (PID $pid)..."
  kill "$pid"

  for _ in {1..20}; do
    if ! is_pid_running "$pid"; then
      rm -f "$pid_file"
      echo "==> $service_name parado."
      return 0
    fi
    sleep 0.5
  done

  echo "==> Encerramento gracioso falhou, forçando $service_name (PID $pid)."
  kill -9 "$pid"
  rm -f "$pid_file"
  echo "==> $service_name parado (forçado)."
}

status_service() {
  local service_name="$1"
  local pid_file
  pid_file="$(service_pid_file "$service_name")"

  if [[ ! -f "$pid_file" ]]; then
    echo "$service_name: stopped"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"
  if is_pid_running "$pid"; then
    echo "$service_name: running (PID $pid)"
  else
    echo "$service_name: stale pid file (PID $pid)"
  fi
}
