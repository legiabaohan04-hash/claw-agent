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
OUT_DIR = Path("data_exports/traffic_views")
PAYLOAD_PATH = Path("data_exports/tableau-live-payload.json")
WORKBOOK_ID = "ac9d1c78-2eee-43c7-b57e-840c9102c0dc"
INTERESTING = ["zone", "zoneid", "source", "sku", "detail", "absolute", "traffic by"]


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


def request(method, url, payload=None, token=None, accept="application/json"):
    body = None
    headers = {"Accept": accept}
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


def sign_in():
    server = clean(os.getenv("TABLEAU_SERVER_URL") or os.getenv("SERVER")).rstrip("/")
    site = clean(os.getenv("TABLEAU_SITE_CONTENT_URL") or os.getenv("SITE_NAME"))
    pat_name = clean(os.getenv("TABLEAU_PAT_NAME") or os.getenv("PAT_NAME"))
    pat_secret = clean(os.getenv("TABLEAU_PAT_SECRET") or os.getenv("PAT_VALUE"))
    version = clean(os.getenv("TABLEAU_API_VERSION") or os.getenv("REST_API_VERSION") or "3.19")
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
    return server, version, credentials["token"], credentials["site"]["id"]


def csv_name(name):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())[:80]
    return cleaned or "view"


def main():
    load_env(ENV_PATH)
    server, version, token, site_id = sign_in()
    workbook_id = clean(os.getenv("TABLEAU_WORKBOOK_INSURANCE_TRAFFIC_ID") or WORKBOOK_ID)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    status, data = request(
        "GET",
        f"{server}/api/{version}/sites/{site_id}/workbooks/{workbook_id}/views",
        token=token,
    )
    if status >= 400 or status == 0:
        raise SystemExit(f"List workbook views failed HTTP {status}: {data[:1000]}")

    parsed = json.loads(data)
    views = parsed.get("views", {}).get("view", [])
    if isinstance(views, dict):
        views = [views]
    manifest = []
    selected_detail = None

    for view in views:
        view_id = view.get("id")
        name = view.get("name", "")
        content_url = view.get("contentUrl", "")
        normalized = f"{name} {content_url}".lower()
        should_export = any(keyword in normalized for keyword in INTERESTING)
        manifest.append({"name": name, "id": view_id, "contentUrl": content_url, "exported": False})
        if not should_export or not view_id:
            continue
        query = urllib.parse.urlencode({"maxAge": "1"})
        status, csv_text = request(
            "GET",
            f"{server}/api/{version}/sites/{site_id}/views/{view_id}/data?{query}",
            token=token,
            accept="text/csv",
        )
        manifest[-1].update({"http": status, "bytes": len(csv_text.encode("utf-8"))})
        if status >= 400 or status == 0:
            manifest[-1]["error"] = csv_text[:500]
            continue
        path = OUT_DIR / f"{csv_name(name)}__{view_id}.csv"
        path.write_text(csv_text, encoding="utf-8")
        manifest[-1].update({"exported": True, "path": str(path)})
        header = csv_text.splitlines()[0] if csv_text.splitlines() else ""
        if not selected_detail and ("FLOW" in header or "ZONE ID" in header or "FROM_SOURCE" in header):
            selected_detail = {"name": name, "id": view_id, "csv": csv_text, "path": str(path), "header": header}

    manifest_path = OUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps({"exported_at": datetime.now().isoformat(), "views": manifest}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest: {manifest_path}")
    for item in manifest:
        flag = "EXPORT" if item.get("exported") else "skip"
        print(f"- {flag}: {item.get('name')} | {item.get('id')} | {item.get('path', '')}")

    if selected_detail:
        if PAYLOAD_PATH.exists():
            payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
        else:
            payload = {"message": "Traffic funnel", "mode": "traffic", "use_tableau_live": False, "data": {}}
        payload.setdefault("data", {})["insurance_traffic_detail_csv"] = selected_detail["csv"]
        payload.setdefault("tableau_export_status", {})["insurance_traffic_detail_csv"] = {
            "http": 200,
            "view_id": selected_detail["id"],
            "view_name": selected_detail["name"],
            "path": selected_detail["path"],
            "header": selected_detail["header"],
        }
        PAYLOAD_PATH.parent.mkdir(exist_ok=True)
        PAYLOAD_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Selected traffic detail: {selected_detail['name']}")
        print(f"Updated payload: {PAYLOAD_PATH}")
    else:
        print("No detail-like traffic view was selected automatically. Check manifest and share view name if needed.")


if __name__ == "__main__":
    main()
