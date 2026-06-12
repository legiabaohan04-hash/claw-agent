#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

BASE_URL="${AGENT_ENDPOINT:-http://localhost:8080}"

curl -s -X POST "${BASE_URL%/}/invocations" \
  -H "Content-Type: application/json" \
  -H "X-GreenNode-AgentBase-User-Id: demo-user" \
  -H "X-GreenNode-AgentBase-Session-Id: demo-session" \
  --data-binary @scripts/kb_status_payload.json
