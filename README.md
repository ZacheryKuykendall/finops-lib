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

A command-line tool for FinOps (Cloud Financial Operations) to analyze, optimize, and report on cloud costs.

## Features

- Multi-cloud cost analysis (AWS, Azure, GCP)
- Cost reporting by service, region, and resource
- Cost anomaly detection
- Cost forecasting
- Budget tracking and alerts
- Cost optimization recommendations
- Resource tagging compliance
- Comprehensive cost efficiency scoring
- Resource utilization analysis
- Idle resource detection
- Sustainability reporting and carbon footprint analysis
- Web interface for dashboards and visualizations

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/finops-cli.git
cd finops-cli

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Show help
python -m finops_lib.cli --help

# Generate a cost report
python -m finops_lib.cli report --start-date 2023-01-01 --end-date 2023-01-31 --test

# Check for cost anomalies
python -m finops_lib.cli anomaly-check --start-date 2023-01-01 --end-date 2023-01-31 --test

# Generate a cost forecast
python -m finops_lib.cli forecast --start-date 2023-01-01 --end-date 2023-01-31 --days 30 --test

# Get optimization recommendations
python -m finops_lib.cli optimize --start-date 2023-01-01 --end-date 2023-01-31 --test

# Analyze resource utilization
python -m finops_lib.cli resource-utilization --start-date 2023-01-01 --end-date 2023-01-31 --test

# Detect idle resources
python -m finops_lib.cli idle-resources --start-date 2023-01-01 --end-date 2023-01-31 --test

# Generate comprehensive cost efficiency score
python -m finops_lib.cli cost-efficiency-score --start-date 2023-01-01 --end-date 2023-01-31 --test

# Generate sustainability report
python -m finops_lib.cli sustainability-report --start-date 2023-01-01 --end-date 2023-01-31 --test

# Start web interface
python -m finops_lib.cli web --port 5000
```

## New Commands

The FinOps CLI has been enhanced with the following new commands:

### Resource Utilization Analysis

```bash
python -m finops_lib.cli resource-utilization --start-date 2023-01-01 --end-date 2023-01-31 --test
```

Analyzes resource utilization across cloud providers, identifying underutilized resources and calculating potential savings from rightsizing.

### Idle Resource Detection

```bash
python -m finops_lib.cli idle-resources --start-date 2023-01-01 --end-date 2023-01-31 --test
```

Detects idle resources across cloud providers by analyzing last activity dates, calculating potential cost savings from removing unused resources.

### Cost Efficiency Score

```bash
python -m finops_lib.cli cost-efficiency-score --start-date 2023-01-01 --end-date 2023-01-31 --test
```

Generates a comprehensive FinOps score based on multiple metrics aligned with industry standards, including resource utilization, waste percentage, discount coverage, cost allocation, and forecast accuracy.

### Sustainability Report

```bash
python -m finops_lib.cli sustainability-report --start-date 2023-01-01 --end-date 2023-01-31 --test
```

Generates a sustainability report with carbon estimates, sustainability scores, and eco-friendly recommendations based on cloud usage patterns.

## Documentation

For detailed documentation, see the [docs](docs/) directory:

- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [Configuration](docs/configuration.md)
- [New Commands](docs/new_commands.md)

## Development

```bash
# Run tests
python -m unittest discover

# Run specific test
python -m unittest tests.test_commands.test_new_commands
```

## License

This project is licensed under the [MIT License](LICENSE).
