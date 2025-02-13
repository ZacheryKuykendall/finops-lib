# FinOps Requirements Across AWS, Azure, and Google Cloud

## Common Challenges

- **Centralized Visibility:** Need for a single view of costs across disparate cloud platforms.
- **Disparate Billing Models:** Normalizing different pricing units, discount programs, and billing cycles.
- **Tagging & Cost Allocation:** Inconsistent resource tagging leads to unallocated costs.
- **Budgeting & Forecasting:** Setting budgets and predicting future costs from historical data.
- **Compliance & Governance:** Enforcing policies (e.g., tagging rules, spending limits) across clouds.

## Provider-Specific APIs & Tools

### AWS
- **Cost Explorer API:** Use `GetCostAndUsage` to retrieve cost data (via boto3).
- **Budgets API & Anomaly Detection:** Built-in capabilities that can be accessed programmatically.

### Azure
- **Cost Management & Consumption APIs:** Use the `azure-mgmt-costmanagement` and `azure-mgmt-consumption` SDKs.
- **Tagging:** Azure Resource Tags can be used to group and filter cost data.

### Google Cloud
- **Cloud Billing API & BigQuery Export:** Detailed cost data is usually exported to BigQuery. Use `google-cloud-bigquery` for querying.
- **Budgets API:** Supports alerting on spending against budgets.

## Compliance & Governance Considerations

- Enforce consistent tagging and resource allocation.
- Respect data residency and sensitive billing data handling.
- Maintain a unified cost model even if underlying data formats differ.
