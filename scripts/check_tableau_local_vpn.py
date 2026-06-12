#!/usr/bin/env python3
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request


ENV_PATH = os.path.expanduser("~/.codex/tableau-mcp.env")
DEFAULT_VIEWS = {
    "insurance_performance": "d3bc93f4-3036-449c-84f8-0a4875cbfc5b",
    "insurance_traffic": "d580ce59-6cc4-4e74-93e0-79b75b2f9154",
    "promotion_summary": "5f8e8ee3-2a76-417b-91ab-e2f4e680e286",
}


def load_env(path):
    if not os.path.exists(path):
        raise SystemExit(f"Missing Tableau env file: {path}")
    pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
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
        with urllib.request.urlopen(req, timeout=45, context=ssl.create_default_context()) as resp:
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
    view_id = clean(os.getenv("TABLEAU_VIEW_INSURANCE_PERFORMANCE_ID") or DEFAULT_VIEWS["insurance_performance"])

    if not all([server, pat_name, pat_secret, version]):
        raise SystemExit("Missing SERVER/PAT_NAME/PAT_VALUE/REST_API_VERSION in ~/.codex/tableau-mcp.env")

    print(f"Server: {server}")
    print(f"Site: {site or '(default)'}")
    print(f"REST API version: {version}")
    print("PAT secret: loaded, not printed")

    status, data = request("GET", f"{server}/api/{version}/serverInfo")
    print(f"serverInfo HTTP: {status}")
    if status >= 400 or status == 0:
        print(data[:1000])
        return 1

    payload = {
        "credentials": {
            "personalAccessTokenName": pat_name,
            "personalAccessTokenSecret": pat_secret,
            "site": {"contentUrl": site},
        }
    }
    status, data = request("POST", f"{server}/api/{version}/auth/signin", payload)
    print(f"signin HTTP: {status}")
    if status >= 400 or status == 0:
        print(data[:1200])
        return 1

    parsed = json.loads(data)
    credentials = parsed["credentials"]
    token = credentials["token"]
    site_id = credentials["site"]["id"]
    print("PAT signin: OK")
    print(f"REST token length: {len(token)}")
    print(f"site id: {site_id}")

    query = urllib.parse.urlencode({"maxAge": "1"})
    view_url = f"{server}/api/{version}/sites/{site_id}/views/{view_id}/data?{query}"
    status, data = request("GET", view_url, token=token)
    print(f"Insurance Performance CSV HTTP: {status}")
    if status >= 400 or status == 0:
        print(data[:1200])
        return 1
    first_line = data.splitlines()[0] if data.splitlines() else ""
    print(f"CSV header: {first_line[:300]}")
    print(f"CSV bytes: {len(data.encode('utf-8'))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
