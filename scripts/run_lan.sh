#!/usr/bin/env bash
# run_lan.sh — Start the agent-orchestrator on the LAN for multi-device access
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=5173

###############################################################################
# Usage / Help
###############################################################################
usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Start the agent-orchestrator backend and frontend, bound to 0.0.0.0 so that
phones, tablets, and laptops on the same LAN can reach the UI.

Options:
  --backend-port PORT    Backend (uvicorn) port  [default: ${BACKEND_PORT}]
  --frontend-port PORT   Frontend (vite) port    [default: ${FRONTEND_PORT}]
  -h, --help             Show this help message and exit

Example:
  $(basename "$0") --backend-port 9000 --frontend-port 3000
EOF
  exit 0
}

###############################################################################
# Parse arguments
###############################################################################
while [[ $# -gt 0 ]]; do
  case "$1" in
    --backend-port)
      BACKEND_PORT="$2"; shift 2 ;;
    --frontend-port)
      FRONTEND_PORT="$2"; shift 2 ;;
    -h|--help)
      usage ;;
    *)
      echo "Unknown option: $1" >&2
      usage ;;
  esac
done

###############################################################################
# Pre-flight checks
###############################################################################
check_cmd() {
  if ! command -v "$1" &>/dev/null; then
    echo "ERROR: Required command '$1' not found. Please install it or enter the nix dev shell." >&2
    exit 1
  fi
}

check_cmd python3
check_cmd node
check_cmd npm

# Check that uvicorn is importable
if ! python3 -c "import uvicorn" &>/dev/null; then
  echo "ERROR: uvicorn not found. Install it (pip install uvicorn) or enter nix develop." >&2
  exit 1
fi

###############################################################################
# Detect LAN IP
###############################################################################
LAN_IP=""
if command -v hostname &>/dev/null; then
  LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || true)
fi
if [[ -z "${LAN_IP}" ]] && command -v ip &>/dev/null; then
  LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' || true)
fi
if [[ -z "${LAN_IP}" || "${LAN_IP}" == "127.0.0.1" ]]; then
  echo "WARNING: Could not detect a LAN IP. Falling back to 0.0.0.0 (all interfaces)." >&2
  LAN_IP="0.0.0.0"
fi

###############################################################################
# Cleanup on exit
###############################################################################
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo ""
  echo "Shutting down..."
  [[ -n "${BACKEND_PID}" ]]  && kill "${BACKEND_PID}"  2>/dev/null || true
  [[ -n "${FRONTEND_PID}" ]] && kill "${FRONTEND_PID}" 2>/dev/null || true
  wait 2>/dev/null || true
  echo "Done."
}
trap cleanup SIGINT SIGTERM EXIT

###############################################################################
# Start services
###############################################################################
echo ""
echo "======================================================="
echo "  Agent Orchestrator - LAN Mode"
echo "======================================================="
echo ""
echo "  Backend URL:   http://${LAN_IP}:${BACKEND_PORT}"
echo "  Frontend URL:  http://${LAN_IP}:${FRONTEND_PORT}"
echo ""
echo "  Health check:  curl http://${LAN_IP}:${BACKEND_PORT}/api/health"
echo ""
echo "  Open the Frontend URL on any device on this network."
echo "  Press Ctrl+C to stop."
echo "======================================================="
echo ""

# Start backend
echo "[backend] Starting uvicorn on 0.0.0.0:${BACKEND_PORT} ..."
(
  cd "${REPO_ROOT}/backend"
  PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}" DEV_MODE=1 python3 -m uvicorn agent_orchestrator.api:app \
    --host 0.0.0.0 \
    --port "${BACKEND_PORT}" \
    --reload
) &
BACKEND_PID=$!

# Start frontend
echo "[frontend] Starting vite dev server on 0.0.0.0:${FRONTEND_PORT} ..."
(
  cd "${REPO_ROOT}/frontend"
  npx vite --host 0.0.0.0 --port "${FRONTEND_PORT}"
) &
FRONTEND_PID=$!

# Wait for either process to exit
wait -n "${BACKEND_PID}" "${FRONTEND_PID}" 2>/dev/null || true
echo "A service exited unexpectedly. Shutting down..."
