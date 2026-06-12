#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -d "venv" ]]; then
  python3 -m venv venv
fi

source venv/bin/activate
python -m pip install --upgrade pip >/dev/null
pip install -r requirements.txt

echo "Starting Bé Hadi Bảo hiểm on http://localhost:8080"
echo "Health: http://localhost:8080/health"
echo "Preview: open preview.html in your browser after this server is running."
python main.py
