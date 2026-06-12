#!/usr/bin/env bash
set -euo pipefail

base_url="${AGENT_ENDPOINT:-https://endpoint-14358055-e169-46fc-9328-8e14537c46cd.agentbase-runtime.aiplatform.vngcloud.vn}"
base_url="${base_url%/}"

echo "Endpoint: ${base_url}"

health_code="$(
  curl -sS -o /tmp/be-hadi-health-body.txt \
    -w '%{http_code}' \
    --connect-timeout 15 \
    --max-time 60 \
    "${base_url}/health"
)"
echo "health HTTP: ${health_code}"
if [[ "${health_code}" != "200" ]]; then
  echo "health body:"
  cat /tmp/be-hadi-health-body.txt
  echo
  exit 1
fi

echo
echo "Checking Tableau live status..."
curl -sS \
  --connect-timeout 15 \
  --max-time 180 \
  -X POST "${base_url}/invocations" \
  -H 'Content-Type: application/json' \
  --data '{"action":"tableau_status","message":"tableau_status"}' \
  | python3 -m json.tool
