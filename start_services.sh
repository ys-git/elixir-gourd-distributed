#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$DIR/.venv/bin/python"

echo "[INFO] Starting Triage Agent on :8001..."
$PYTHON -m services.triage 8001 &
PID_TRIAGE=$!

echo "[INFO] Starting Coder Agent on :8002..."
$PYTHON -m services.coder 8002 &
PID_CODER=$!

echo "[INFO] Starting Verifier Agent on :8003..."
$PYTHON -m services.verifier 8003 &
PID_VERIFIER=$!

cleanup() {
    echo ""
    echo "[INFO] Shutting down agent services..."
    kill $PID_TRIAGE $PID_CODER $PID_VERIFIER 2>/dev/null || true
    wait $PID_TRIAGE $PID_CODER $PID_VERIFIER 2>/dev/null || true
    echo "[INFO] All services stopped."
}

trap cleanup EXIT INT TERM

sleep 1
echo "[INFO] Services online. Press Ctrl+C to terminate."
wait

