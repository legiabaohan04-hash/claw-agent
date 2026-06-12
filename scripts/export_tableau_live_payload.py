#!/usr/bin/env python3
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


ENV_PATH = Path(os.path.expanduser("~/.codex/tableau-mcp.env"))
OUT_DIR = Path("data_exports")
OUT_PAYLOAD = OUT_DIR / "tableau-live-payload.json"
VIEWS = {
    "insurance_performance_csv": "d3bc93f4-3036-449c-84f8-0a4875cbfc5b",
    "insurance_traffic_csv": "d580ce59-6cc4-4e74-93e0-79b75b2f9154",
    "promotion_summary_csv": "5f8e8ee3-2a76-417b-91ab-e2f4e680e286",
}


def load_env(path):
    if not path.exists():
        raise SystemExit(f"Missing Tableau env file: {path}")
    pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            continue
        key, value = match.groups()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        os.environ.setdefault(key, value)


def clean(value):
    return (value or "").strip().strip('"').strip("'")


def request(method, url, payload=None, token=None):
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["X-Tableau-Auth"] = token
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context()) as resp:
            return resp.status, resp.read().decode("utf-8-sig", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, f"Network error: {exc.reason}"


def main():
    load_env(ENV_PATH)
    server = clean(os.getenv("TABLEAU_SERVER_URL") or os.getenv("SERVER")).rstrip("/")
    site = clean(os.getenv("TABLEAU_SITE_CONTENT_URL") or os.getenv("SITE_NAME"))
    pat_name = clean(os.getenv("TABLEAU_PAT_NAME") or os.getenv("PAT_NAME"))
    pat_secret = clean(os.getenv("TABLEAU_PAT_SECRET") or os.getenv("PAT_VALUE"))
    version = clean(os.getenv("TABLEAU_API_VERSION") or os.getenv("REST_API_VERSION") or "3.19")
    if not all([server, pat_name, pat_secret, version]):
        raise SystemExit("Missing SERVER/PAT_NAME/PAT_VALUE/REST_API_VERSION in ~/.codex/tableau-mcp.env")

    payload = {
        "credentials": {
            "personalAccessTokenName": pat_name,
            "personalAccessTokenSecret": pat_secret,
            "site": {"contentUrl": site},
        }
    }
    status, data = request("POST", f"{server}/api/{version}/auth/signin", payload)
    if status >= 400 or status == 0:
        raise SystemExit(f"Tableau signin failed HTTP {status}: {data[:1000]}")
    credentials = json.loads(data)["credentials"]
    token = credentials["token"]
    site_id = credentials["site"]["id"]

    OUT_DIR.mkdir(exist_ok=True)
    live_data = {}
    view_status = {}
    for key, default_view_id in VIEWS.items():
        env_key = {
            "insurance_performance_csv": "TABLEAU_VIEW_INSURANCE_PERFORMANCE_ID",
            "insurance_traffic_csv": "TABLEAU_VIEW_INSURANCE_TRAFFIC_ID",
            "promotion_summary_csv": "TABLEAU_VIEW_PROMOTION_SUMMARY_ID",
        }[key]
        view_id = clean(os.getenv(env_key) or default_view_id)
        query = urllib.parse.urlencode({"maxAge": "1"})
        url = f"{server}/api/{version}/sites/{site_id}/views/{view_id}/data?{query}"
        status, csv_text = request("GET", url, token=token)
        view_status[key] = {"http": status, "view_id": view_id, "bytes": len(csv_text.encode("utf-8"))}
        if status >= 400 or status == 0:
            view_status[key]["error"] = csv_text[:1000]
            continue
        live_data[key] = csv_text
        (OUT_DIR / f"{key}.csv").write_text(csv_text, encoding="utf-8")

    output = {
        "message": "Phân tích nhanh tình hình insurance, traffic funnel và promotion. Có gì đang cần chú ý không?",
        "mode": "daily",
        "use_tableau_live": False,
        "data": live_data,
        "exported_at": datetime.now().isoformat(),
        "tableau_export_status": view_status,
    }
    OUT_PAYLOAD.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported payload: {OUT_PAYLOAD}")
    print(json.dumps(view_status, ensure_ascii=False, indent=2))
    if not live_data:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
