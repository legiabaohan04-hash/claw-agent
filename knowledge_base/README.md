# Bé Hadi Bảo hiểm Knowledge Base

This folder contains the operating knowledge for the Bé Hadi Bảo hiểm AI Agent.

It is intentionally stored as plain Markdown/YAML so the agent can load it at startup, reviewers can inspect it in GitHub, and the team can update business rules without changing code.

## Files

- `agent-operating-rules.md`: how the agent should behave, analyze, and communicate.
- `business-context.md`: product/business background and KPI definitions.
- `tableau-sources.yaml`: Tableau workbook/view IDs and data access notes.
- `product-catalog.yaml`: important insurance product groups, owners, and product code hints.
- `monthly-report-template.md`: report structure inferred from March and April 2026 reports.
- `reminders.md`: monthly reminder rules for KPI, incentive, and promotion-code input.

## Recommended Loading Order

1. `agent-operating-rules.md`
2. `business-context.md`
3. `tableau-sources.yaml`
4. `product-catalog.yaml`
5. `monthly-report-template.md`
6. `reminders.md`

## Secret Policy

Do not store Tableau PAT secrets, passwords, Outlook credentials, or API keys in this folder.
Store secrets in environment variables or a local secret manager only.
