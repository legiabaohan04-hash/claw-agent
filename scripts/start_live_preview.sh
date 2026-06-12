#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/import_tableau_mcp_env.sh

touch .env
for key in TABLEAU_PROXY_URL TABLEAU_PROXY_URLS TABLEAU_PROXY_TOKEN ALLOW_DEMO_DATA_WHEN_TABLEAU_FAILS; do
  if grep -q "^${key}=" .env 2>/dev/null; then
    grep -v "^${key}=" .env > .env.tmp && mv .env.tmp .env
  fi
done
if grep -q "^TABLEAU_AUTO_REFRESH=" .env 2>/dev/null; then
  grep -v "^TABLEAU_AUTO_REFRESH=" .env > .env.tmp && mv .env.tmp .env
fi
echo "TABLEAU_AUTO_REFRESH=true" >> .env
chmod 600 .env

if [[ ! -d "venv" ]]; then
  python3 -m venv venv
fi

source venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

export TABLEAU_AUTO_REFRESH=true
unset TABLEAU_PROXY_URL
unset TABLEAU_PROXY_URLS
unset TABLEAU_PROXY_TOKEN

if lsof -nP -iTCP:8080 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port 8080 is already running. Stop it first with ./scripts/stop_local.sh"
  exit 1
fi

echo "Starting Bé Hadi live preview on http://localhost:8080"
echo "This mode calls Tableau directly from this Mac, so keep VPN enabled."
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

curl -s http://localhost:8080/health >/dev/null
open "http://localhost:8080/?v=$(date +%s)"

echo "Live preview is running."
echo "To stop:"
echo "  ./scripts/stop_local.sh"
