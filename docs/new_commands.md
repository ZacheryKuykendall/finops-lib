# FinOps CLI New Commands

This document describes the new commands added to the FinOps CLI to enhance cloud cost analysis capabilities.

## Table of Contents

1. [Sustainability Report](#sustainability-report)
2. [Resource Utilization Analysis](#resource-utilization-analysis)
3. [Idle Resource Detection](#idle-resource-detection)
4. [Cost Efficiency Score](#cost-efficiency-score)

## Sustainability Report

Generates a sustainability report with carbon estimates and recommendations based on your cloud resource usage.

### Usage

```bash
python -m finops_lib.cli sustainability-report --start-date START_DATE --end-date END_DATE [OPTIONS]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--start-date` | Start date in YYYY-MM-DD format | Yes |
| `--end-date` | End date in YYYY-MM-DD format | Yes |
| `--test` | Run with test data | No |
| `--output` | Output format (`console` or `json`) | No (default: `console`) |
| `--export` | Export path for report (e.g., "sustainability_report.json") | No |

### Example

```bash
python -m finops_lib.cli sustainability-report --start-date 2023-01-01 --end-date 2023-01-31 --test
```

### Output

The command produces a comprehensive sustainability report including:

* Sustainability score (0-100)
* Estimated carbon emissions (in kg CO2)
* Estimated power usage (in kWh)
* Top recommendations for improving cloud sustainability
* Most sustainable regions for workload placement
* Carbon intensity by region

## Resource Utilization Analysis

Analyzes resource utilization across cloud providers, identifying underutilized resources and potential savings.

### Usage

```bash
python -m finops_lib.cli resource-utilization --start-date START_DATE --end-date END_DATE [OPTIONS]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--start-date` | Start date in YYYY-MM-DD format | Yes |
| `--end-date` | End date in YYYY-MM-DD format | Yes |
| `--test` | Run with test data | No |
| `--threshold` | Utilization threshold (0-1) for highlighting underutilized resources | No (default: 0.5) |

### Example

```bash
python -m finops_lib.cli resource-utilization --start-date 2023-01-01 --end-date 2023-01-31 --test --threshold 0.6
```

### Output

The command produces a resource utilization analysis including:

* Average utilization across all resources
* Count of underutilized resources (below threshold)
* Cost of underutilized resources and potential savings
* Utilization breakdown by service
* List of top underutilized resources by cost
* Recommendations for improving utilization

## Idle Resource Detection

Detects idle resources across cloud providers, calculating potential savings from removing or optimizing these resources.

### Usage

```bash
python -m finops_lib.cli idle-resources --start-date START_DATE --end-date END_DATE [OPTIONS]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--start-date` | Start date in YYYY-MM-DD format | Yes |
| `--end-date` | End date in YYYY-MM-DD format | Yes |
| `--test` | Run with test data | No |
| `--inactive-threshold` | Number of days of inactivity to consider a resource idle | No (default: 7) |

### Example

```bash
python -m finops_lib.cli idle-resources --start-date 2023-01-01 --end-date 2023-01-31 --test --inactive-threshold 14
```

### Output

The command produces an idle resource detection report including:

* Total number of idle resources based on the threshold
* Monthly cost of idle resources
* Potential annual savings from removing idle resources
* Breakdown of idle resources by type
* Breakdown of idle resources by cloud provider
* Top idle resources by cost
* Recommendations for addressing idle resources

## Cost Efficiency Score

Generates a comprehensive cost efficiency score based on multiple FinOps metrics aligned with industry standards.

### Usage

```bash
python -m finops_lib.cli cost-efficiency-score --start-date START_DATE --end-date END_DATE [OPTIONS]
```

### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--start-date` | Start date in YYYY-MM-DD format | Yes |
| `--end-date` | End date in YYYY-MM-DD format | Yes |
| `--test` | Run with test data | No |
| `--output` | Output format (`console` or `json`) | No (default: `console`) |
| `--export` | Export path for report | No |

### Example

```bash
python -m finops_lib.cli cost-efficiency-score --start-date 2023-01-01 --end-date 2023-01-31 --test --output json
```

### Output

The command produces a cost efficiency score report including:

* Overall composite score (0-2.00 scale)
* Score interpretation (Poor, Below Average, Average, Good, Excellent)
* Detailed scores for each component metric:
  * Resource Utilization
  * Waste Percentage
  * Discount Coverage
  * Cost Allocation
  * Forecast Accuracy
* Current metric values
* Customized recommendations based on the score profile

## Scoring Methodology

The cost efficiency score is calculated using a methodology based on FinOps Foundation guidelines:

* **Resource Utilization (30%)**: How effectively provisioned cloud resources are being used
* **Discount Coverage (25%)**: How much of eligible cloud spend is covered by commitment-based discounts
* **Cost Allocation (15%)**: How effectively costs are mapped to business units/teams
* **Forecast Accuracy (15%)**: How accurately cloud spend was predicted
* **Waste Percentage (15%)**: How much spend is attributed to waste (idle/unused resources)

Scores range from 0.0 to 2.0, with higher scores indicating better cost efficiency. 