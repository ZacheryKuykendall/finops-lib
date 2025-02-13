# FinOps Multi-Cloud Python Library

## Overview

This Python library is designed to empower FinOps engineers to manage and optimize cloud spending across AWS, Azure, and Google Cloud. It provides real-time cost analysis by querying each cloud’s billing APIs, normalizes the data into a common format, and lays the groundwork for future automation features such as anomaly detection, AI/ML-powered forecasting, and policy enforcement.

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

### Anomaly Detection

Detect cost anomalies within a specified date range:

```bash
finops-cli anomaly-check --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

- `--start-date`: Start date for anomaly detection (YYYY-MM-DD).
- `--end-date`: End date for anomaly detection (YYYY-MM-DD).

### Cost Forecasting

Produce cost forecasts based on historical data:

```bash
finops-cli forecast --start-date YYYY-MM-DD --end-date YYYY-MM-DD --days [number]
```

- `--start-date`: Start date for forecasting (YYYY-MM-DD).
- `--end-date`: End date for forecasting (YYYY-MM-DD).
- `--days`: Number of days to forecast. Default is 30.

### Optimization Recommendations

Analyze spending patterns and suggest cost optimization opportunities:

```bash
finops-cli optimize --start-date YYYY-MM-DD --end-date YYYY-MM-DD --test
```

- `--start-date`: Start date for analysis (YYYY-MM-DD).
- `--end-date`: End date for analysis (YYYY-MM-DD).
- `--test`: Use test data instead of live cloud data.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](documentation/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
