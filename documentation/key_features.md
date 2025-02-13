# Key Features & Functionality

## Cost Visibility & Reporting

- **Real-Time Data Retrieval:** Query AWS Cost Explorer, Azure Cost Management, and GCP BigQuery for the latest cost data.
- **Aggregation & Normalization:** Combine results into unified reports (e.g., by cloud, service, tag, account).
- **Filtering & Drill-Down:** Allow filtering by time range, tag, or account.
- **Output Formats:** Support Pandas DataFrame, CSV, JSON, and CLI table outputs.

### Example Code Snippet
```python
from finops_lib import CostAnalyzer

analyzer = CostAnalyzer(aws_credentials, azure_credentials, gcp_credentials)
report = analyzer.get_cost_breakdown(period="month_to_date", group_by=["cloud", "service"])
print(report.to_markdown())
```
## Anomaly Detection
- **Baseline Modeling:** Use historical cost data to compute moving averages and standard deviations.
- **Alerting Mechanism:** Flag and report cost anomalies (e.g., unexpected spikes).
- **Pluggable Algorithms:** Support both simple rule-based and advanced ML-based anomaly detection.

## Budgeting & Forecasting
- **Budget Alerts:** Compare current spend against predefined budgets.
- **Forecasting Models:** Implement AI/ML-powered forecasting (using linear extrapolation or time-series models like ARIMA or Prophet).
- **Output:** Provide forecasts with confidence intervals and daily breakdowns.

## Tagging & Cost Allocation
- **Tag-Based Grouping:** Retrieve and aggregate cost data by tag (e.g., team, project).
- **Unallocated Costs Reporting:** Identify and report resources missing required tags.
- **Hierarchical Allocation:** Support multi-level grouping (e.g., Business Unit > Project > Team).

## Automated Cost Optimization (Future Scope)
- **Rightsizing Recommendations:** Integrate with AWS Compute Optimizer, Azure Advisor, and GCP Recommender.
- **Idle Resource Detection:** Identify underutilized resources using cloud-native checks.
- **Scheduled Optimizations:** Plan for automated actions (e.g., shutting down non-prod resources outside working hours).

## Policy Enforcement & Governance (Future Scope)
- **Policy-as-Code:** Define policies in YAML or Python (e.g., require specific tags, auto-stop idle resources).
- **Actionable Reports:** Generate governance reports and possibly trigger automated remediation.