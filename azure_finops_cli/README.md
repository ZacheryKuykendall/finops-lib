# Azure FinOps CLI

A command-line interface tool for Azure cloud cost management and optimization.

## Features

- Real-time cost tracking and analysis
- Cost breakdown by Azure services, regions, and resource groups
- Reserved Instance (RI) utilization tracking
- Budget monitoring and alerts
- Efficiency scoring and optimization recommendations
- Interactive web dashboard

## Installation

```bash
pip install az-finops-cli
```

## Configuration

1. Create a `config.json` file in your working directory:

```json
{
    "azure_subscription_id": "YOUR_SUBSCRIPTION_ID",
    "budgets": [
        {
            "name": "Azure Development",
            "amount": 1000.0,
            "timeGrain": "Monthly",
            "startDate": "2024-01-01",
            "endDate": "2024-12-31"
        }
    ]
}
```

2. Set up Azure authentication:
   - Install Azure CLI
   - Run `az login`
   - Set your subscription: `az account set --subscription YOUR_SUBSCRIPTION_ID`

## Usage

### Web Dashboard

Start the web interface:

```bash
az-finops-cli web
```

Access the dashboard at `http://localhost:5000`

### CLI Commands

Get cost report:
```bash
az-finops-cli report --start-date 2024-01-01 --end-date 2024-01-31
```

Calculate efficiency score:
```bash
az-finops-cli score --start-date 2024-01-01 --end-date 2024-01-31
```

Get optimization recommendations:
```bash
az-finops-cli optimize
```

## Requirements

- Python 3.8 or higher
- Azure subscription
- Azure CLI
- Cost Management permissions on your Azure subscription

## License

MIT License 