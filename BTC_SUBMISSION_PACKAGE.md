# Bé Hadi Bảo hiểm - BTC Submission Package

## Required Submission Items

1. Public GitHub source code
   - Target repo: `https://github.com/legiabaohan04-hash/claw-agent`
   - Include: `main.py`, `knowledge_loader.py`, `knowledge_base/`, `Dockerfile`, `requirements.txt`, `preview.html`, `scripts/`, README files.
   - Do not include: `.env`, Tableau PAT, LLM API key, `.greennode.json`.

2. Public demo video, 2-3 minutes
   - Recommended flow:
     - Show Bé Hadi Bảo hiểm UI.
     - Ask: `Tình hình bảo hiểm 4326 như thế nào`.
     - Show AppID-specific output with TPV/MPU/change/status.
     - Ask an incentive question.
     - Show promotion cost/TPV and recommended actions.
     - Mention knowledge base + Tableau CSV/API path.

3. Use case description, 100-200 words
   - Draft is in `SUBMISSION.md`.

## Optional But Strong

- AgentBase deployed endpoint:
  - `https://endpoint-14358055-e169-46fc-9328-8e14537c46cd.agentbase-runtime.aiplatform.vngcloud.vn`
- LLM configured through GreenNode AI Platform or another OpenAI-compatible provider.
- Demo with real Tableau CSV export.

## Local Demo Commands

```bash
./scripts/configure_llm_env.sh
./scripts/start_preview.sh
```

If no LLM key is available, the deterministic fallback still demonstrates:

- product/AppID/SKU breakdown,
- traffic funnel checks,
- promotion efficiency,
- monthly report draft structure.

## Current Known Limitation

The agent only answers product/AppID-specific numbers when the payload includes product-level CSV fields such as:

- `App ID`
- `SKU Name`
- `Product Name`
- `TPV`
- `MPU`
- `NPU`
- `FPU`
- `AOV`
- period/date column

If the payload only has aggregate rows, the agent can summarize total business health but cannot infer individual product performance.
