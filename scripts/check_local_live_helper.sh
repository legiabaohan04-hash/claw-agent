#!/usr/bin/env bash
set -euo pipefail

base_url="${LOCAL_AGENT_ENDPOINT:-http://localhost:8080}"
base_url="${base_url%/}"

echo "Endpoint: ${base_url}"

health_code="$(
  curl -sS -o /tmp/be-hadi-local-health.txt \
    -w '%{http_code}' \
    --connect-timeout 5 \
    --max-time 20 \
    "${base_url}/health" || true
)"
echo "health HTTP: ${health_code}"
if [[ "${health_code}" != "200" ]]; then
  echo "Local helper is not healthy. Body:"
  cat /tmp/be-hadi-local-health.txt 2>/dev/null || true
  echo
  exit 1
fi

echo
echo "Checking local Tableau live status..."
curl -sS \
  --connect-timeout 10 \
  --max-time 180 \
  -X POST "${base_url}/invocations" \
  -H 'Content-Type: application/json' \
  --data '{"action":"tableau_status","message":"tableau_status"}' \
  | python3 -m json.tool
