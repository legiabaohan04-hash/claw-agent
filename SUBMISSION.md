# Claw-a-thon Submission Draft

## Use Case Description (100-200 words)

Bé Hadi Bảo hiểm is an AI Business Analyst for the insurance team. The team currently spends significant time opening Tableau dashboards, exporting data, checking TPV/MPU movement, reviewing incentive cost, and writing monthly reports manually. Bé Hadi turns those dashboards into a natural-language analysis assistant. Users can ask questions such as "Why did insurance TPV drop?", "Which product is driving growth?", or "Is this promotion efficient?" The agent reads a curated knowledge base, analyzes Insurance Performance, Insurance Traffic, and Promotion Summary data, then returns concise Vietnamese business insights with risks and recommended actions. It understands insurance KPIs such as MPU, NPU, FPU, TPV, AOV, traffic funnel stages, and internal business rules for MoM/MTD health checks. The goal is to reduce manual reporting time, standardize insight quality, and help product owners make faster decisions from existing dashboard data.

## Demo Video Flow (2-3 minutes)

1. Show the problem: manual Tableau/Excel/report workflow.
2. Show knowledge base folder and explain business rules are encoded.
3. Call `POST /invocations` with a performance question and sample dashboard CSV.
4. Show output: TPV trend, traffic funnel, promotion cost/TPV, recommendations.
5. Mention future automation: daily Outlook email, monthly reminders, Tableau MCP live exports.

## Current Status

- Knowledge base prepared.
- Tableau MCP tested locally with Atlas VPN.
- Agent MVP scaffold prepared.
- Needs final sync into `/Users/lap14183/Documents/Claw/claw-agent`, local test, GitHub push, and demo video recording.
