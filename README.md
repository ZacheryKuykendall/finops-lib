# FinOps Multi-Cloud Python Library

## Overview

This Python library is designed to empower FinOps engineers to manage and optimize cloud spending across AWS, Azure, and Google Cloud. It provides real-time cost analysis by querying each cloud's billing APIs, normalizes the data into a common format, and lays the groundwork for future automation features such as anomaly detection, AI/ML-powered forecasting, and policy enforcement.

## Key FinOps Principles

- **Cost Visibility & Timeliness:** Immediate access to up-to-date cost data.
- **Accountability:** Empowering teams to monitor and own their cloud spending.
- **Collaboration:** Encouraging cross-functional teamwork between finance, engineering, and operations.
- **Centralized Governance:** Consolidating cost management and enforcing policies across clouds.
- **Optimization & Automation:** Continuously identifying and acting on cost-saving opportunities.

## High-Level Goals

- Provide a unified multi-cloud view of costs via real-time API queries.
- Offer modular design to support future enhancements such as automation, anomaly detection, and forecasting.
- Enable FinOps engineers to work via a command-line interface (CLI) with a moderate learning curve.

# FinOps CLI

A command-line tool for multi-cloud cost analysis and optimization.

## Features

- **Cost Reporting:** Generate detailed cost reports across AWS, Azure, and GCP.
- **Anomaly Detection:** Identify unusual spending patterns.
- **Cost Forecasting:** Predict future cloud costs.
- **Optimization Recommendations:** Get suggestions for reducing cloud spending.
- **Budget Management:** Set and track budgets for specific teams and projects.
- **Cost Efficiency Scoring:** Calculate and interpret cost efficiency scores to assess cloud spending efficiency.
- **Enhanced Reporting:** Generate cost breakdowns by service and region.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ZacheryKuykendall/finops-cli.git
   cd finops-cli
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the dependencies:
   ```bash
   pip install -e .
   ```

## Usage

```bash
finops-cli --help
```

### Cost Reporting

Generate cost reports for a specified date range:

```bash
finops-cli report --start-date YYYY-MM-DD --end-date YYYY-MM-DD --format [markdown|csv|json] --test
```

- `--start-date`: Start date for the report (YYYY-MM-DD).
- `--end-date`: End date for the report (YYYY-MM-DD).
- `--format`: Output format (markdown, csv, or json). Default is markdown.
- `--test`: Use test data instead of live cloud data.
- `--export`: Export the report to a file.

### Budget Management

Set a budget for a specific team and project:

```bash
finops-cli set-budget --team TEAM_NAME --project PROJECT_NAME --amount AMOUNT --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Track spending against the budget:

```bash
finops-cli track-budget --team TEAM_NAME --project PROJECT_NAME --start-date YYYY-MM-DD --end-date YYYY-MM-DD --test
```

- `--team`: Team name for the budget.
- `--project`: Project name for the budget.
- `--amount`: Budget amount in USD.
- `--start-date`: Start date for the budget (YYYY-MM-DD).
- `--end-date`: End date for the budget (YYYY-MM-DD).
- `--test`: Use test data instead of live cloud data.

### Cost Efficiency Scoring

Calculate and display the cost efficiency score:

```bash
finops-cli cost-efficiency-score --start-date YYYY-MM-DD --end-date YYYY-MM-DD --forecast FORECAST_AMOUNT --test
```

- `--start-date`: Start date for the score calculation (YYYY-MM-DD).
- `--end-date`: End date for the score calculation (YYYY-MM-DD).
- `--forecast`: Forecasted total spend for the period.
- `--test`: Use test data instead of live cloud data.

### Enhanced Reporting

Generate a cost breakdown by service:

```bash
finops-cli cost-by-service --start-date YYYY-MM-DD --end-date YYYY-MM-DD --test
```

Generate a cost breakdown by region:

```bash
finops-cli cost-by-region --start-date YYYY-MM-DD --end-date YYYY-MM-DD --test
```

- `--start-date`: Start date for the report (YYYY-MM-DD).
- `--end-date`: End date for the report (YYYY-MM-DD).
- `--test`: Use test data instead of live cloud data.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](documentation/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
