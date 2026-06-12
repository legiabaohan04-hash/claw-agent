# Business Context

## Product Idea

Bé Hadi Bảo hiểm is an AI Business Analyst for insurance products. It helps the team analyze business performance, visualize data, and generate insight from existing dashboards.

The agent should reduce manual work currently done through Tableau/Excel/monthly reports.

## Main Problems

- Daily tracking of TPV and MPU.
- Monitoring incentive/campaign performance.
- Diagnosing product growth or decline.
- Preparing monthly reports.
- Turning dashboards from static reporting into decision support.

## KPI Definitions

- `MPU`: Monthly Paying Users.
- `NPU`: New Paying Users.
- `FPU`: First Paying Users.
- `TPV`: Total Payment Value.
- `AOV`: Average Order Value.
- `TRANS`: transactions.
- `Discount Amount`: total discount/subsidy amount.

## Traffic Funnel Definitions

- `Load` or `Access Users`: number of users/page loads reaching the insurance purchase page.
- `Cashier Users`: users reaching the payment information summary/cashier step.
- `Success Users`: users successfully buying insurance.
- `Success Rate`: successful purchases divided by load/access volume, depending on dashboard definition.

## Main Capabilities

### Daily Business Monitoring

- Analyze TPV and MPU today and MTD.
- Compare with previous day/period/month.
- Identify top product contributors.
- Detect anomalies.
- Analyze contribution from traffic source, including new sources.
- Send daily reports to the Insurance team by email.

### Incentive Performance Analysis

- Evaluate TPV/MPU uplift.
- Compare before and after incentive launch.
- Track campaign by source when new campaigns are tagged with tracking source.
- Use Promotion Summary for cost, cost/TPV, AOV, CAC, CPU, NPU/FPU, promo users, and promo transactions.
- Ask for monthly promotion code input at the beginning of each month or before report generation.

### Product Performance Diagnosis

Example questions:

- Why did Chubb Life decline?
- Which product is driving growth?
- Which group/product/source needs attention?

### Automated Monthly Report

Generate:

- Executive Summary
- What Went Well
- What Didn't Go Well
- Key Insights
- Recommended Actions

When KPI/incentive context is missing, generate the data-driven performance sections using available Tableau data and clearly mark missing inputs.

## Email Recipients

- hanlgb@vng.com.vn
- mynt5@vng.com.vn
- tramntq@vng.com.vn
- tranvhd@vng.com.vn
