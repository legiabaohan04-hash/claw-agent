# Bé Hadi Bảo hiểm AI Agent

Bé Hadi Bảo hiểm is an AI Business Analyst for insurance product performance.

The agent helps the Insurance team analyze TPV, MPU/users, traffic funnel, incentive cost, product contribution, and monthly report insights from Tableau/Atlas dashboard exports.

## What It Does

- Loads business knowledge from `knowledge_base/` at startup through `knowledge_loader.py`.
- Accepts exported CSV text from:
  - Insurance Performance
  - Insurance Traffic Dashboard
  - Promotion Summary
- Computes KPI summaries for performance, traffic funnel, and promotion efficiency.
- Builds product/AppID/SKU/source breakdowns when Tableau CSV exports include those columns.
- Produces Vietnamese business insights and recommended actions.
- Uses GreenNode MaaS LLM when `LLM_API_KEY` or `AI_PLATFORM_API_KEY` is configured. `LLM_BASE_URL` defaults to the OpenAI-compatible `/v1` endpoint and `LLM_MODEL` defaults to `qwen/qwen3-5-27b`.
- Falls back to deterministic analysis when no LLM key is present, so demo/testing still works.
- Important: AppID/product-specific answers require product-level CSV in `insurance_product_performance_csv`.

## AgentBase Runtime

The container listens on port `8080`.

- Health check: `GET /health`
- Invocation: `POST /invocations`
- Public endpoint: `https://endpoint-14358055-e169-46fc-9328-8e14537c46cd.agentbase-runtime.aiplatform.vngcloud.vn`

Test the deployed endpoint:

```bash
AGENT_ENDPOINT="https://endpoint-14358055-e169-46fc-9328-8e14537c46cd.agentbase-runtime.aiplatform.vngcloud.vn" \
  ./scripts/demo_curl.sh
```

## Local Run

```bash
./scripts/run_local.sh
```

Test:

```bash
curl -s http://localhost:8080/health

curl -s -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -H "X-GreenNode-AgentBase-User-Id: demo-user" \
  -H "X-GreenNode-AgentBase-Session-Id: demo-session" \
  -d '{"message":"Phan tich nhanh tinh hinh insurance hom nay"}'
```

Check that the knowledge base is loaded:

```bash
./scripts/test_kb_status.sh
```

## Web Preview

Fast path:

```bash
./scripts/start_preview.sh
```

Manual path:

```bash
./scripts/run_local.sh
```

Then open `preview.html` in your browser.

Stop background server started by `start_preview.sh`:

```bash
./scripts/stop_local.sh
```

## LLM Setup

Recommended provider for the competition: GreenNode AI Platform, because it is OpenAI-compatible and fits AgentBase deployment.

Create a local `.env` file:

```bash
./scripts/configure_llm_env.sh
```

Or create `.env` from `.env.example`, then fill:

```bash
LLM_API_KEY=...
AI_PLATFORM_API_KEY=...
LLM_BASE_URL=https://maas-llm-aiplatform-hcm.api.vngcloud.vn/v1
LLM_MODEL=qwen/qwen3-5-27b
LLM_TIMEOUT_SECONDS=90
```

Do not commit `.env`.

LLM configuration makes answers richer and more flexible, but it does not replace data. For questions such as `Tình hình bảo hiểm 4326 như thế nào`, the request must include product-level rows containing AppID/SKU/product metrics.

Use the model path from the API usage sample, not the display name. For example, use `qwen/qwen3-5-27b`, not `Qwen` or `Qwen 3.5 27B`. The code calls the OpenAI-compatible `POST /v1/chat/completions` API.

If the UI says `APITimeoutError`, the model path is usually recognized but the request is too slow or the machine cannot reach the MAAS endpoint. Keep `LLM_TIMEOUT_SECONDS=90`; if it still times out, check VPN/DNS/network access to `maas-llm-aiplatform-hcm.api.vngcloud.vn`.

## Tableau Live Data

Local app can import the existing Tableau MCP config:

```bash
./scripts/import_tableau_mcp_env.sh
```

This enables `TABLEAU_AUTO_REFRESH=true` and fetches CSV directly from Tableau REST API with `maxAge=1`, so Tableau live is the default data path. Important: AppID-level answers are only reliable when Tableau export contains AppID/SKU/product-level rows or the view filter is verified. If Tableau live fails, Bé Hadi reports that live data is unavailable instead of silently using demo data. Set `ALLOW_DEMO_DATA_WHEN_TABLEAU_FAILS=true` only for offline demos.

For AppID/SKU questions, Bé Hadi tries Tableau view filters such as `vf_Sku=<appID>` and `vf_App ID=<appID>` based on these env values:

```bash
TABLEAU_PERFORMANCE_APPID_FILTER_FIELDS=Sku,App ID
TABLEAU_PRODUCT_APPID_FILTER_FIELDS=App ID,Sku,SKU Name
TABLEAU_TRAFFIC_APPID_FILTER_FIELDS=SKU NAME,APP NAME,App ID
TABLEAU_PROMOTION_APPID_FILTER_FIELDS=*App ID,App ID,Campaign Code,Campaign ID
```

If Atlas uses a different filter caption, update the matching env var with the exact filter name shown on the dashboard. If a promotion question asks for one AppID but no campaign code/AppID-level row is available, the agent asks for the missing code/export instead of using total `All` promotion cost.

## Tableau Bridge For AgentBase

If AgentBase PUBLIC runtime gets `HTTP 403 Forbidden` from Atlas while the laptop can access Tableau over VPN, run a local bridge on the laptop and expose it through an approved tunnel. Bé Hadi will still be deployed on AgentBase, but Tableau live data is fetched from the VPN-enabled machine.

Terminal 1, with VPN enabled:

```bash
./scripts/start_tableau_bridge.sh
```

The script prints `TABLEAU_PROXY_TOKEN`. Keep the terminal open.

Terminal 2, test local bridge:

```bash
export TABLEAU_PROXY_TOKEN="<token printed by Terminal 1>"
./scripts/check_tableau_bridge_local.sh
```

Expose `http://localhost:3928` with an approved tunnel, then save the public bridge URL and token:

```bash
./scripts/configure_tableau_bridge_env.sh
```

Redeploy AgentBase after that:

```bash
./work/deploy-be-hadi-agentbase.sh
```

## Tableau MCP Option

The project can reuse a Tableau MCP server configured with:

```bash
TRANSPORT=http
DANGEROUSLY_DISABLE_OAUTH=true
SERVER=https://atlas.vng.com.vn
SITE_NAME=ZLPDataServices
PAT_NAME=...
PAT_VALUE=...
```

The MCP HTTP transport defaults to `http://localhost:3927/tableau-mcp`. This is useful for local Codex/MCP testing. For AgentBase runtime, `localhost:3927` would point to the runtime container itself, not the user's laptop, so the MCP server must be hosted somewhere the runtime can reach. Until that is available, Bé Hadi uses Tableau REST exports directly with the same PAT settings.

## Request Payload

```json
{
  "message": "Phân tích MTD theo từng sản phẩm insurance",
  "mode": "product",
  "data": {
    "insurance_performance_csv": "Period_Type,Switch Break View,AOV,TPV,TRANS,USERS_DAILY,Max. Ymd\nMay-26,All,\"30,448\",\"432,581,700\",\"14,207\",\"12,486\",5/31/2026\nJun-26,All,\"31,652\",\"346,752,031\",\"10,955\",\"9,825\",6/10/2026",
    "insurance_product_performance_csv": "Period_Type,App ID,SKU Name,Product Name,TPV,MPU,AOV\nMay-26,3394,3394_Bảo hiểm màn hình điện thoại 7.000 VND,Bảo hiểm màn hình điện thoại,\"100,000,000\",\"4,000\",\"25,000\"\nJun-26,3394,3394_Bảo hiểm màn hình điện thoại 7.000 VND,Bảo hiểm màn hình điện thoại,\"85,000,000\",\"3,200\",\"26,562\"",
    "insurance_traffic_csv": "Time,LOAD VALUE,SUCCESS RATE,SUCCESS VALUE,Max. report_date\n09-Jun,\"279,007\",0.002150484,600,6/9/2026\n10-Jun,\"316,155\",0.002495611,789,6/10/2026",
    "promotion_summary_csv": "C0,C1,Campaign View,Measure Names,Period,Measure Values\nAll,All,All,*Final Cost,All,\"211,126,017\"\nAll,All,All,TPV,All,\"423,108,652\"\nAll,All,All,%Cost/TPV,All,0.498987709"
  }
}
```

For product-specific questions, export/paste columns such as `App ID`, `SKU Name`, `Product Name`, `App Name`, `TPV`, `MPU`, `NPU`, `FPU`, `AOV`, and a period/date column. The agent will answer by product/AppID/SKU when those fields exist.

## Notes

- Do not commit Tableau PAT tokens or LLM API keys.
- Current Tableau Server has VizQL Data Service disabled, so the MVP uses dashboard CSV exports rather than direct datasource queries.
- Tableau MCP works locally through the user's VPN and should be called sequentially to avoid intermittent `401`.
