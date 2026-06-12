#!/usr/bin/env bash
set -euo pipefail

if [[ -f /tmp/insurance-pulse-server.pid ]]; then
  pid="$(cat /tmp/insurance-pulse-server.pid)"
  if kill -0 "${pid}" >/dev/null 2>&1; then
    kill "${pid}"
    echo "Stopped Bé Hadi Bảo hiểm server (${pid})."
  else
    echo "Stored server PID is not running."
  fi
  rm -f /tmp/insurance-pulse-server.pid
else
  echo "No stored server PID found."
fi
