import csv
import io
import json
import os
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


ENV_PATH = Path(os.path.expanduser("~/.codex/tableau-mcp.env"))
DEFAULT_TABLEAU_VIEWS = {
    "insurance_performance_csv": "d3bc93f4-3036-449c-84f8-0a4875cbfc5b",
    "insurance_traffic_csv": "d580ce59-6cc4-4e74-93e0-79b75b2f9154",
    "promotion_summary_csv": "5f8e8ee3-2a76-417b-91ab-e2f4e680e286",
}

app = FastAPI(title="Bé Hadi Tableau Bridge")


class LiveRequest(BaseModel):
    message: str = ""


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
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


load_env_file(ENV_PATH)


def env_value(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value.strip().strip('"').strip("'")
    return default


def parse_number(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_csv_text(text: str) -> List[Dict[str, str]]:
    if not text or not text.strip():
        return []
    reader = csv.DictReader(io.StringIO(text.strip()))
    return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def app_id_from_message(message: str) -> Optional[str]:
    match = re.search(r"\b\d{4,}\b", message or "")
    return match.group(0) if match else None


def split_env_list(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def safe_exception_message(exc: Exception, limit: int = 500) -> str:
    message = f"{exc.__class__.__name__}: {str(exc)}"
    if isinstance(exc, urllib.error.HTTPError):
        try:
            body = exc.read().decode("utf-8", errors="replace").strip()
            if body:
                body = re.sub(r"\s+", " ", body)
                message = f"{message}; body={body[:limit]}"
        except Exception:
            pass
    return message[:limit]


def http_json(url: str, payload: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    data = None
    request_headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=request_headers, method="POST" if payload is not None else "GET")
    timeout_seconds = parse_number(os.getenv("TABLEAU_HTTP_TIMEOUT_SECONDS")) or 45
    with urllib.request.urlopen(req, timeout=timeout_seconds, context=ssl.create_default_context()) as response:
        return json.loads(response.read().decode("utf-8"))


def http_text(url: str, headers: Optional[Dict[str, str]] = None) -> str:
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    timeout_seconds = parse_number(os.getenv("TABLEAU_HTTP_TIMEOUT_SECONDS")) or 45
    with urllib.request.urlopen(req, timeout=timeout_seconds, context=ssl.create_default_context()) as response:
        return response.read().decode("utf-8-sig")


def tableau_credentials() -> Dict[str, str]:
    return {
        "server": env_value("TABLEAU_SERVER_URL", "SERVER").rstrip("/"),
        "site": env_value("TABLEAU_SITE_CONTENT_URL", "SITE_NAME"),
        "pat_name": env_value("TABLEAU_PAT_NAME", "PAT_NAME"),
        "pat_secret": env_value("TABLEAU_PAT_SECRET", "PAT_VALUE"),
        "api_version": env_value("TABLEAU_API_VERSION", "REST_API_VERSION", default="3.19"),
    }


def tableau_sign_in() -> Dict[str, str]:
    creds = tableau_credentials()
    sign_in_url = f"{creds['server']}/api/{creds['api_version']}/auth/signin"
    payload = {
        "credentials": {
            "personalAccessTokenName": creds["pat_name"],
            "personalAccessTokenSecret": creds["pat_secret"],
            "site": {"contentUrl": creds["site"]},
        }
    }
    result = http_json(sign_in_url, payload=payload)
    credentials = result["credentials"]
    return {
        "server": creds["server"],
        "api_version": creds["api_version"],
        "token": credentials["token"],
        "site_id": credentials["site"]["id"],
    }


def tableau_view_id(data_key: str) -> str:
    env_keys = {
        "insurance_performance_csv": "TABLEAU_VIEW_INSURANCE_PERFORMANCE_ID",
        "insurance_product_performance_csv": "TABLEAU_VIEW_PRODUCT_PERFORMANCE_ID",
        "insurance_traffic_csv": "TABLEAU_VIEW_INSURANCE_TRAFFIC_ID",
        "promotion_summary_csv": "TABLEAU_VIEW_PROMOTION_SUMMARY_ID",
    }
    return env_value(env_keys.get(data_key, ""), default=DEFAULT_TABLEAU_VIEWS.get(data_key, ""))


def filter_attempts(message: str, data_key: str) -> List[Dict[str, str]]:
    app_id = app_id_from_message(message)
    if not app_id:
        return [{}]
    env_names = {
        "insurance_performance_csv": "TABLEAU_PERFORMANCE_APPID_FILTER_FIELDS",
        "insurance_product_performance_csv": "TABLEAU_PRODUCT_APPID_FILTER_FIELDS",
        "insurance_traffic_csv": "TABLEAU_TRAFFIC_APPID_FILTER_FIELDS",
        "promotion_summary_csv": "TABLEAU_PROMOTION_APPID_FILTER_FIELDS",
    }
    default_fields = {
        "insurance_performance_csv": "Sku,App ID",
        "insurance_product_performance_csv": "App ID,Sku,SKU Name",
        "insurance_traffic_csv": "SKU NAME,APP NAME,App ID",
        "promotion_summary_csv": "*App ID,App ID,Campaign Code,Campaign ID",
    }
    fields = env_value(env_names.get(data_key, ""), "TABLEAU_APPID_FILTER_FIELDS", default=default_fields.get(data_key, "Sku"))
    return [{field: app_id} for field in split_env_list(fields)] or [{}]


def fetch_view_csv(session: Dict[str, str], view_id: str, filters: Optional[Dict[str, str]] = None) -> str:
    query = {"maxAge": "1"}
    for field, value in (filters or {}).items():
        if value:
            query[f"vf_{field}"] = value
    url = (
        f"{session['server']}/api/{session['api_version']}/sites/{session['site_id']}"
        f"/views/{view_id}/data?{urllib.parse.urlencode(query)}"
    )
    return http_text(url, headers={"X-Tableau-Auth": session["token"]})


def fetch_live_data(message: str) -> Dict[str, Any]:
    metadata = {"enabled": True, "used": False, "errors": [], "views": {}, "source": "local-vpn-bridge"}
    data: Dict[str, str] = {}
    try:
        session = tableau_sign_in()
    except Exception as exc:
        metadata["errors"].append(f"Không sign in Tableau được: {safe_exception_message(exc)}")
        return {"data": data, "metadata": metadata}

    for data_key in [
        "insurance_performance_csv",
        "insurance_product_performance_csv",
        "insurance_traffic_csv",
        "promotion_summary_csv",
    ]:
        view_id = tableau_view_id(data_key)
        if not view_id:
            continue
        attempts = filter_attempts(message, data_key)
        for filters in attempts:
            try:
                csv_text = fetch_view_csv(session, view_id, filters)
                rows = parse_csv_text(csv_text)
                if filters and not rows and len(attempts) > 1:
                    metadata["errors"].append(f"{data_key} filters={filters}: 0 rows, trying next filter.")
                    continue
                data[data_key] = csv_text
                metadata["views"][data_key] = {
                    "view_id": view_id,
                    "rows": len(rows),
                    "filters": filters,
                    "filter_attempts": attempts,
                }
                metadata["used"] = True
                break
            except Exception as exc:
                metadata["errors"].append(f"{data_key} filters={filters}: {safe_exception_message(exc)}")
    return {"data": data, "metadata": metadata}


def check_auth(authorization: Optional[str]) -> None:
    expected = env_value("TABLEAU_PROXY_TOKEN")
    if not expected:
        raise HTTPException(status_code=500, detail="TABLEAU_PROXY_TOKEN is not configured on bridge.")
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="Unauthorized.")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/tableau/live")
def tableau_live(request: LiveRequest, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    check_auth(authorization)
    return fetch_live_data(request.message)
