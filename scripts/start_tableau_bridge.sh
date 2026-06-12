#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -d "venv" ]]; then
  python3 -m venv venv
fi

source venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null

if [[ -z "${TABLEAU_PROXY_TOKEN:-}" ]]; then
  export TABLEAU_PROXY_TOKEN="$(python - <<'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
)"
fi

echo "Starting Bé Hadi Tableau bridge on http://localhost:3928"
echo "Bridge health: http://localhost:3928/health"
echo "TABLEAU_PROXY_TOKEN=${TABLEAU_PROXY_TOKEN}"
echo
echo "Keep this terminal open while demoing live Tableau."
echo "Expose http://localhost:3928 with an approved tunnel, then set AgentBase env:"
echo "  TABLEAU_PROXY_URL=<public tunnel URL>"
echo "  TABLEAU_PROXY_TOKEN=<token printed above>"
echo

uvicorn tableau_bridge:app --host 0.0.0.0 --port 3928
