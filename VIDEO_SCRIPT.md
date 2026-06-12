# Demo Video Script

Target length: 2-3 minutes.

## 0:00-0:20 Problem

"Team Insurance currently tracks TPV, users, traffic funnel, and promotion cost manually from Tableau and Excel. Monthly report preparation is repetitive and depends on each analyst's interpretation."

## 0:20-0:45 Solution

"Bé Hadi Bảo hiểm is an AI Business Analyst. It reads a curated knowledge base and dashboard exports from Insurance Performance, Insurance Traffic, and Promotion Summary, then returns insight and recommended action in Vietnamese."

Show:

- `knowledge_base/`
- `README.md`
- `PROJECT_CHECKLIST.md`

## 0:45-1:30 Live Agent Call

Start the agent locally:

```bash
python main.py
```

In another terminal:

```bash
./scripts/demo_curl.sh
```

Explain the output:

- Performance TPV movement
- Traffic load/success conversion
- Promotion cost/TPV
- Recommended next action

## 1:30-2:15 Business Value

"Instead of manually reading dashboards, Product Owners can ask natural-language questions such as why TPV dropped, which product drives growth, or whether an incentive is efficient. The agent applies team-specific rules: MTD same-day comparison, MoM thresholds, key products, and promotion efficiency metrics."

## 2:15-2:45 Next Steps

"The MVP already works with CSV/dashboard exports. The next step is production automation: Tableau MCP live export through VPN or internal runtime, daily Outlook reports, monthly reminders on day 15/18/20, and AgentBase Memory for persistent product mapping and report context."

## Recording Checklist

- Show health endpoint works.
- Show one `POST /invocations` response.
- Show the knowledge base folder.
- Mention no secrets are committed.
- Keep video public before submission.
