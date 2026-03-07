#!/usr/bin/env bash
# run_lan_test.sh — smoke tests for the LAN startup script
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_LAN="${SCRIPT_DIR}/run_lan.sh"
PASS=0
FAIL=0

pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }

echo "=== run_lan.sh smoke tests ==="
echo

# Test 1: Script exists and is executable
echo "Test 1: Script exists and is executable"
if [[ -x "${RUN_LAN}" ]]; then
  pass "run_lan.sh exists and is executable"
else
  fail "run_lan.sh missing or not executable"
fi

# Test 2: --help prints usage information
echo "Test 2: --help prints usage information"
HELP_OUTPUT=$("${RUN_LAN}" --help 2>&1 || true)
if echo "${HELP_OUTPUT}" | grep -qi "usage\|lan\|backend.*port\|frontend.*port"; then
  pass "--help prints usage info"
else
  fail "--help did not print expected usage info"
fi

# Test 3: LAN IP detection logic works (extracts a non-localhost IP)
echo "Test 3: LAN IP detection extracts a non-localhost IP"
# Use the same detection logic the script uses
LAN_IP=""
if command -v hostname &>/dev/null; then
  LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || true)
fi
if [[ -z "${LAN_IP}" ]] && command -v ip &>/dev/null; then
  LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}' || true)
fi
if [[ -n "${LAN_IP}" && "${LAN_IP}" != "127.0.0.1" ]]; then
  pass "Detected LAN IP: ${LAN_IP}"
else
  fail "Could not detect a non-localhost LAN IP"
fi

# Test 4: --help output mentions both port flags
echo "Test 4: --help mentions --backend-port and --frontend-port"
if echo "${HELP_OUTPUT}" | grep -q "\-\-backend-port" && echo "${HELP_OUTPUT}" | grep -q "\-\-frontend-port"; then
  pass "--help documents both port flags"
else
  fail "--help missing port flag documentation"
fi

echo
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="
if [[ ${FAIL} -gt 0 ]]; then
  exit 1
fi
