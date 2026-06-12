#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if lsof -nP -iTCP:8080 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8080 is already running. Opening preview..."
else
  if [[ ! -d "venv" ]]; then
    python3 -m venv venv
  fi
  source venv/bin/activate
  python -m pip install --upgrade pip >/dev/null
  pip install -r requirements.txt
  echo "Starting API server on http://localhost:8080 ..."
  python main.py > /tmp/insurance-pulse-server.log 2>&1 &
  server_pid=$!
  echo "${server_pid}" > /tmp/insurance-pulse-server.pid

  for _ in $(seq 1 30); do
    if curl -s http://localhost:8080/health >/dev/null 2>&1; then
      break
    fi
    if ! kill -0 "${server_pid}" >/dev/null 2>&1; then
      echo "Server crashed while starting. Logs:"
      cat /tmp/insurance-pulse-server.log
      exit 1
    fi
    sleep 1
  done
fi

if ! curl -s http://localhost:8080/health >/dev/null 2>&1; then
  echo "Server did not become healthy. Logs:"
  cat /tmp/insurance-pulse-server.log 2>/dev/null || true
  exit 1
fi

echo "Server is running."
echo "Opening preview at http://localhost:8080/ ..."
open "http://localhost:8080/?v=$(date +%s)"
echo
echo "If you need logs:"
echo "  tail -f /tmp/insurance-pulse-server.log"
echo
echo "To stop server:"
echo "  kill \$(cat /tmp/insurance-pulse-server.pid)"
