#!/usr/bin/env bash
# dev_stack.sh — manage backend+frontend dev stack as background processes
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${REPO_ROOT}/.run"
BACKEND_PID_FILE="${RUN_DIR}/backend.pid"
FRONTEND_PID_FILE="${RUN_DIR}/frontend.pid"
ENV_FILE="${RUN_DIR}/stack.env"
BACKEND_LOG="${RUN_DIR}/backend.log"
FRONTEND_LOG="${RUN_DIR}/frontend.log"

BACKEND_PORT=8000
FRONTEND_PORT=5173
LAN_MODE=0

usage() {
  cat <<USAGE
Usage: $(basename "$0") <start|stop|status|logs> [OPTIONS]

Commands:
  start                Start backend + frontend in the background
  stop                 Stop running backend + frontend started by this script
  status               Show current stack status
  logs                 Tail backend/frontend logs

Options (for start):
  --lan                Bind services to 0.0.0.0 for LAN access
  --backend-port PORT  Backend port (default: ${BACKEND_PORT})
  --frontend-port PORT Frontend port (default: ${FRONTEND_PORT})
  -h, --help           Show this help
USAGE
}

check_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: Missing command '$1'. Enter nix develop and try again." >&2
    exit 1
  fi
}

is_running() {
  local pid="$1"
  [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1
}

read_pid() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    tr -d '[:space:]' <"$pid_file"
  fi
}

detect_lan_ip() {
  local ip=""
  if command -v hostname >/dev/null 2>&1; then
    ip=$(hostname -I 2>/dev/null | awk '{print $1}' || true)
  fi
  if [[ -z "$ip" ]] && command -v ip >/dev/null 2>&1; then
    ip=$(ip route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' || true)
  fi
  if [[ -z "$ip" || "$ip" == "127.0.0.1" ]]; then
    ip="0.0.0.0"
  fi
  printf '%s' "$ip"
}

ensure_not_running() {
  local bp fp
  bp=$(read_pid "$BACKEND_PID_FILE")
  fp=$(read_pid "$FRONTEND_PID_FILE")
  if is_running "$bp" || is_running "$fp"; then
    echo "Stack already running. Use '$0 status' or '$0 stop'." >&2
    exit 1
  fi
}

start_stack() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --lan)
        LAN_MODE=1
        shift
        ;;
      --backend-port)
        BACKEND_PORT="$2"
        shift 2
        ;;
      --frontend-port)
        FRONTEND_PORT="$2"
        shift 2
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "Unknown option: $1" >&2
        usage
        exit 1
        ;;
    esac
  done

  check_cmd python3
  check_cmd npm

  if ! python3 -c "import uvicorn" >/dev/null 2>&1; then
    echo "ERROR: uvicorn not importable. Enter nix develop and try again." >&2
    exit 1
  fi

  mkdir -p "$RUN_DIR"
  ensure_not_running

  local host lan_ip display_ip
  host="127.0.0.1"
  if [[ "$LAN_MODE" -eq 1 ]]; then
    host="0.0.0.0"
  fi
  lan_ip=$(detect_lan_ip)
  display_ip="127.0.0.1"
  if [[ "$host" == "0.0.0.0" ]]; then
    display_ip="$lan_ip"
  fi

  (
    cd "${REPO_ROOT}/backend"
    DEV_MODE=1 python3 -m uvicorn agent_orchestrator.api:app \
      --host "$host" \
      --port "$BACKEND_PORT" \
      --reload
  ) >"$BACKEND_LOG" 2>&1 &
  local backend_pid=$!

  (
    cd "${REPO_ROOT}/frontend"
    npm run dev -- --host "$host" --port "$FRONTEND_PORT"
  ) >"$FRONTEND_LOG" 2>&1 &
  local frontend_pid=$!

  echo "$backend_pid" >"$BACKEND_PID_FILE"
  echo "$frontend_pid" >"$FRONTEND_PID_FILE"
  cat >"$ENV_FILE" <<ENV
HOST=${host}
LAN_IP=${display_ip}
BACKEND_PORT=${BACKEND_PORT}
FRONTEND_PORT=${FRONTEND_PORT}
ENV

  sleep 1

  if ! is_running "$backend_pid" || ! is_running "$frontend_pid"; then
    echo "Failed to start stack. Recent logs:" >&2
    [[ -f "$BACKEND_LOG" ]] && tail -n 30 "$BACKEND_LOG" >&2 || true
    [[ -f "$FRONTEND_LOG" ]] && tail -n 30 "$FRONTEND_LOG" >&2 || true
    exit 1
  fi

  echo "Stack started in background"
  echo "  Backend:  http://${display_ip}:${BACKEND_PORT}"
  echo "  Frontend: http://${display_ip}:${FRONTEND_PORT}"
  echo "  Status:   ./scripts/dev_stack.sh status"
  echo "  Stop:     ./scripts/dev_stack.sh stop"
}

stop_one() {
  local pid="$1"
  if ! is_running "$pid"; then
    return 0
  fi
  kill "$pid" >/dev/null 2>&1 || true
  for _ in {1..10}; do
    if ! is_running "$pid"; then
      return 0
    fi
    sleep 0.3
  done
  kill -9 "$pid" >/dev/null 2>&1 || true
}

stop_stack() {
  local bp fp
  bp=$(read_pid "$BACKEND_PID_FILE")
  fp=$(read_pid "$FRONTEND_PID_FILE")

  if [[ -z "$bp" && -z "$fp" ]]; then
    echo "Stack is not running."
    return 0
  fi

  stop_one "$bp"
  stop_one "$fp"

  rm -f "$BACKEND_PID_FILE" "$FRONTEND_PID_FILE" "$ENV_FILE"
  echo "Stack stopped."
}

status_stack() {
  local bp fp host lan_ip backend_port frontend_port
  bp=$(read_pid "$BACKEND_PID_FILE")
  fp=$(read_pid "$FRONTEND_PID_FILE")

  host="127.0.0.1"
  lan_ip="127.0.0.1"
  backend_port="$BACKEND_PORT"
  frontend_port="$FRONTEND_PORT"

  if [[ -f "$ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    host="${HOST:-$host}"
    lan_ip="${LAN_IP:-$lan_ip}"
    backend_port="${BACKEND_PORT:-$backend_port}"
    frontend_port="${FRONTEND_PORT:-$frontend_port}"
  fi

  echo "Backend PID:  ${bp:-none}"
  echo "Frontend PID: ${fp:-none}"

  if is_running "$bp" && is_running "$fp"; then
    echo "Status: RUNNING"
    echo "Backend URL:  http://${lan_ip}:${backend_port}"
    echo "Frontend URL: http://${lan_ip}:${frontend_port}"
    echo "Logs:         ./scripts/dev_stack.sh logs"
  else
    echo "Status: STOPPED"
    if [[ -n "$bp" ]] && ! is_running "$bp"; then
      echo "  backend process not alive"
    fi
    if [[ -n "$fp" ]] && ! is_running "$fp"; then
      echo "  frontend process not alive"
    fi
  fi

  if [[ "$host" == "0.0.0.0" ]]; then
    echo "Mode: LAN"
  else
    echo "Mode: Localhost"
  fi
}

logs_stack() {
  mkdir -p "$RUN_DIR"
  touch "$BACKEND_LOG" "$FRONTEND_LOG"
  echo "== backend.log =="
  tail -n 20 "$BACKEND_LOG"
  echo ""
  echo "== frontend.log =="
  tail -n 20 "$FRONTEND_LOG"
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

cmd="$1"
shift

case "$cmd" in
  start)
    start_stack "$@"
    ;;
  stop)
    stop_stack
    ;;
  status)
    status_stack
    ;;
  logs)
    logs_stack
    ;;
  -h|--help)
    usage
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    usage
    exit 1
    ;;
esac
