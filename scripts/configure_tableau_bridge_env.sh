#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

read -r -p "TABLEAU_PROXY_URL (public tunnel URL): " proxy_url
if [[ -z "${proxy_url}" ]]; then
  echo "TABLEAU_PROXY_URL is required."
  exit 1
fi

read -r -s -p "TABLEAU_PROXY_TOKEN (hidden): " proxy_token
echo
if [[ -z "${proxy_token}" ]]; then
  echo "TABLEAU_PROXY_TOKEN is required."
  exit 1
fi

proxy_url="${proxy_url%/}"
echo "Checking bridge health at ${proxy_url}/health ..."
health_code="$(
  curl -sS -o /tmp/be-hadi-bridge-configure-health.txt \
    -w '%{http_code}' \
    --connect-timeout 10 \
    --max-time 30 \
    "${proxy_url}/health" || true
)"
if [[ "${health_code}" != "200" ]]; then
  echo "Bridge URL is not healthy yet. HTTP: ${health_code:-curl_failed}"
  echo "Body:"
  cat /tmp/be-hadi-bridge-configure-health.txt 2>/dev/null || true
  cat <<'HELP'

Fix:
  1. Keep ./scripts/start_tableau_bridge.sh running in Terminal 1.
  2. Keep cloudflared/ngrok tunnel running in Terminal 2.
  3. Paste the CURRENT public tunnel URL here, not an old URL.

HELP
  exit 1
fi

echo "Checking bridge Tableau live endpoint ..."
live_code="$(
  curl -sS -o /tmp/be-hadi-bridge-configure-live.json \
    -w '%{http_code}' \
    --connect-timeout 10 \
    --max-time 120 \
    -X POST "${proxy_url}/tableau/live" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${proxy_token}" \
    --data '{"message":"tableau_status"}' || true
)"
if [[ "${live_code}" != "200" ]]; then
  echo "Bridge live endpoint is not reachable/authenticated. HTTP: ${live_code:-curl_failed}"
  echo "Body:"
  cat /tmp/be-hadi-bridge-configure-live.json 2>/dev/null || true
  exit 1
fi

if ! python3 - <<'PY'
import json
data = json.load(open("/tmp/be-hadi-bridge-configure-live.json"))
raise SystemExit(0 if data.get("metadata", {}).get("used") else 1)
PY
then
  echo "Bridge responded, but Tableau live data was not used. Response:"
  python3 -m json.tool /tmp/be-hadi-bridge-configure-live.json 2>/dev/null || cat /tmp/be-hadi-bridge-configure-live.json
  exit 1
fi

touch .env
chmod 600 .env

set_env() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" .env 2>/dev/null; then
    grep -v "^${key}=" .env > .env.tmp && mv .env.tmp .env
  fi
  printf '%s=%s\n' "$key" "$value" >> .env
}

set_env "TABLEAU_PROXY_URL" "${proxy_url}"
set_env "TABLEAU_PROXY_TOKEN" "${proxy_token}"
set_env "TABLEAU_AUTO_REFRESH" "true"

echo "Tableau bridge env saved locally without printing the token."
