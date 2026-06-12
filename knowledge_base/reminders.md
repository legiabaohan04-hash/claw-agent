# Reminder Rules

## Monthly Report Inputs

The monthly report is expected near the end of each month, but the agent should start preparing around the 20th.

Reminder schedule:

- Day 15: first reminder to provide monthly KPI, incentive plan, and campaign context.
- Day 18: second reminder if inputs are still missing.
- Day 20: generate a draft report anyway using available Tableau data.

If KPI/incentive inputs are missing on day 20:

- Generate performance/trend sections from Tableau.
- Mark KPI and incentive commentary as incomplete.
- Ask the user for final KPI/incentive details.

## Promotion Code Tracking

The user may upload monthly promotion codes as plain text.

Agent behavior:

- Parse code list as raw tracking codes.
- Use codes to filter Promotion Summary if matching fields are available.
- If code fields are unavailable in exported dashboard CSV, state the limitation and summarize campaign data by Campaign Source, Campaign Code, Campaign Sub Code, Campaign ID, or Reward ID when available.

## Daily Report Email

Daily report should be sent to:

- hanlgb@vng.com.vn
- mynt5@vng.com.vn
- tramntq@vng.com.vn
- tranvhd@vng.com.vn

The exact sending mechanism can be SMTP, Microsoft Graph, or draft generation, depending on available credentials.

Report timing and content:

- Send every morning using T-1 data. Example: on the 11th, report numbers for the 10th.
- Performance section: TPV and MPU for active/key AppID products. If there are too many active AppIDs, prioritize key products highlighted red in the product catalog.
- Split performance commentary by PIC:
  - Hân: key products managed by Hân.
  - Trân: remaining key products managed by Trân.
- For each product, state current TPV/MPU, change versus previous comparable period, and status.
- Traffic section: summarize each app overall when available.
- Traffic source section: list top 3 sources by Success. Show Load, Cashier, and Success for each top source.
- Use only dashboard fields that exist. Do not include NPU/FPU in daily report unless a future dashboard explicitly provides those fields.
