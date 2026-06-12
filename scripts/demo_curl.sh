#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${AGENT_ENDPOINT:-http://localhost:8080}"
echo "Calling ${BASE_URL%/}/invocations ..."

curl -sS --connect-timeout 15 --max-time 180 -X POST "${BASE_URL%/}/invocations" \
  -H "Content-Type: application/json" \
  -H "X-GreenNode-AgentBase-User-Id: demo-user" \
  -H "X-GreenNode-AgentBase-Session-Id: demo-session" \
  --data-binary @scripts/demo_payload.json
echo
