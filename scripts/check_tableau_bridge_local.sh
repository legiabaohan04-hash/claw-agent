#!/usr/bin/env bash
set -euo pipefail

bridge_url="${TABLEAU_PROXY_URL:-http://localhost:3928}"
bridge_url="${bridge_url%/}"

if [[ -z "${TABLEAU_PROXY_TOKEN:-}" ]]; then
  echo "Set TABLEAU_PROXY_TOKEN to the token printed by start_tableau_bridge.sh"
  exit 1
fi

echo "Bridge: ${bridge_url}"
curl -sS -o /tmp/be-hadi-bridge-health.txt -w 'health HTTP: %{http_code}\n' \
  --connect-timeout 10 \
  --max-time 30 \
  "${bridge_url}/health"

curl -sS \
  --connect-timeout 10 \
  --max-time 120 \
  -X POST "${bridge_url}/tableau/live" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${TABLEAU_PROXY_TOKEN}" \
  --data '{"message":"Performance appID 4326 hôm nay"}' \
  | python3 -m json.tool
