# Bé Hadi Bảo hiểm Project Checklist

## Done

- Agent idea and business scope defined.
- Claw-a-thon guide and recap reviewed.
- GreenNode AgentBase skills cloned next to `claw-agent`.
- Tableau MCP connected locally through VPN.
- Main Tableau dashboards identified:
  - Insurance Performance
  - Insurance Traffic Dashboard
  - Promotion Summary
- Knowledge base created under `knowledge_base/`.
- Agent MVP source prepared:
  - `main.py`
  - `Dockerfile`
  - `requirements.txt`
  - `.env.example`
  - `.dockerignore`
  - README and submission draft
- Demo payload prepared.
- Product/AppID/SKU breakdown supported for product-level CSV exports.
- AppID-specific fallback tested with AppID 4326.
- Local LLM configuration script prepared at `scripts/configure_llm_env.sh`.
- AgentBase/IAM + LLM setup script prepared at `scripts/setup_agentbase_credentials.sh`.
- AgentBase deployment runbook prepared at `AGENTBASE_DEPLOYMENT_RUNBOOK.md`.

## Still Needed Before Submission

- Sync MVP files into `/Users/lap14183/Documents/Claw/claw-agent`.
- Run local or Docker test.
- Configure IAM + LLM key/model locally using `scripts/setup_agentbase_credentials.sh`.
- Commit and push source code to public GitHub.
- Record and upload a public 2-3 minute demo video.
- Submit public GitHub link, video link, and 100-200 word use case description.

## Optional But Valuable

- Deploy to AgentBase Runtime and include the endpoint in the submission.
- Add Outlook/Graph/SMTP credentials later for actual daily email sending.
- Add AgentBase Memory later for durable reminders and learned product mapping corrections.

## Inputs That Are Enough For MVP

- Business idea and KPI definitions.
- Tableau dashboard URLs and IDs.
- Product group/product-code mapping from the screenshot.
- Business rules for MTD and MoM health.
- Monthly report examples and structure.
- Email recipients.
- Promotion code input preference.

## Inputs Still Missing For Full Production

- Exact monthly KPI targets by product/category.
- Monthly incentive plan and campaign objective.
- Final preferred LLM model/key.
- Email sending method and credentials.
- Confirmation whether cloud runtime can access Atlas/Tableau directly, or whether data export will remain local.
- Final product owner mapping if dashboard labels differ from screenshot mapping.
