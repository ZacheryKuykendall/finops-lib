import click
import os
import logging
from pathlib import Path
from .reporting import get_report
from .aws import AWSCostProvider
from .azure import AzureCostProvider
from .gcp import GCPCostProvider
from .anomaly import detect_anomalies
from .forecast import forecast_costs
import pandas as pd
from .optimize import optimize_costs
import json
from .scoring import calculate_composite_score

# Set up logging at module level
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

BUDGET_FILE = 'budgets.json'

# Helper function to load budgets
def load_budgets():
    if not os.path.exists(BUDGET_FILE):
        return {}
    with open(BUDGET_FILE, 'r') as f:
        return json.load(f)

# Helper function to save budgets
def save_budgets(budgets):
    with open(BUDGET_FILE, 'w') as f:
        json.dump(budgets, f, indent=4)

@click.group()
def cli():
    """FinOps CLI tool for multi-cloud cost analysis."""
    pass

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--format', default="markdown", type=click.Choice(['markdown', 'csv', 'json']), 
              help='Report output format')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
@click.option('--export', help='Export to file (e.g., "costs.csv")')
def report(start_date, end_date, format, test, export):
    """Generate and display cost reports."""
    click.echo("Generating report...")
    output = get_report(start_date, end_date, output_format=format, test_mode=test)
    
    if export:
        with open(export, 'w', newline='') as f:  # Added newline='' to fix extra line issue
            f.write(output)
        click.echo(f"Report exported to: {os.path.abspath(export)}")
    else:
        click.echo(output)

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
def anomaly_check(start_date, end_date):
    """Run anomaly detection on cost data."""
    click.echo("Fetching cost data for anomaly detection...")
    # Aggregate data from all providers (reuse reporting module for simplicity)
    report_csv = get_report(start_date, end_date, output_format="csv")
    cost_df = pd.read_csv(pd.compat.StringIO(report_csv))
    anomalies = detect_anomalies(cost_df)
    if anomalies.empty:
        click.echo("No anomalies detected.")
    else:
        click.echo("Anomalies found:")
        click.echo(anomalies.to_markdown(index=False))

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--days', default=30, help='Number of days to forecast')
def forecast(start_date, end_date, days):
    """Produce cost forecasts based on historical data."""
    click.echo("Fetching cost data for forecasting...")
    report_csv = get_report(start_date, end_date, output_format="csv")
    cost_df = pd.read_csv(pd.compat.StringIO(report_csv))
    forecast_df = forecast_costs(cost_df, n_days=days)
    click.echo("Forecast:")
    click.echo(forecast_df.to_markdown(index=False))

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
def optimize(start_date, end_date, test):
    """Optimize cloud costs."""
    click.echo("Running cost optimization...")
    results = optimize_costs(start_date, end_date, test)
    click.echo(results)

@cli.command()
@click.option('--resource-id', required=True, help='Resource ID to analyze')
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
def analyze_resource(resource_id, start_date, end_date, test):
    """Analyze costs for a specific resource."""
    click.echo(f"Analyzing costs for resource {resource_id}...")
    
    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch data from each provider
    aws_data = aws_provider.get_cost_data(start_date, end_date, resource_id)
    azure_data = azure_provider.get_cost_data(start_date, end_date, resource_id)
    gcp_data = gcp_provider.get_cost_data(start_date, end_date, resource_id)

    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])

    # Display results
    if combined_data.empty:
        click.echo("No cost data found for the specified resource.")
    else:
        click.echo("Resource Cost Analysis:")
        click.echo(combined_data.to_markdown(index=False))

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
def tag_audit(start_date, end_date, test):
    """Audit resource tags and identify missing or inconsistent tags."""
    click.echo("Auditing resource tags...")
    
    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch data from each provider
    aws_data = aws_provider.get_cost_data(start_date, end_date)
    azure_data = azure_provider.get_cost_data(start_date, end_date)
    gcp_data = gcp_provider.get_cost_data(start_date, end_date)

    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])

    # Analyze tags
    missing_tags = combined_data[combined_data['tags'].apply(lambda x: not x)]
    inconsistent_tags = combined_data[combined_data['tags'].apply(lambda x: 'environment' not in x or 'team' not in x or 'project' not in x)]

    # Display results
    if missing_tags.empty and inconsistent_tags.empty:
        click.echo("All resources have consistent tags.")
    else:
        if not missing_tags.empty:
            click.echo("Resources with missing tags:")
            click.echo(missing_tags.to_markdown(index=False))
        if not inconsistent_tags.empty:
            click.echo("Resources with inconsistent tags:")
            click.echo(inconsistent_tags.to_markdown(index=False))

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
def tag_compliance_report(start_date, end_date, test):
    """Generate a report showing tag compliance across resources."""
    click.echo("Generating tag compliance report...")
    
    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch data from each provider
    aws_data = aws_provider.get_cost_data(start_date, end_date)
    azure_data = azure_provider.get_cost_data(start_date, end_date)
    gcp_data = gcp_provider.get_cost_data(start_date, end_date)

    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])

    # Analyze tag compliance
    def check_compliance(tags):
        required_tags = ['environment', 'team', 'project']
        return all(tag in tags and tags[tag] for tag in required_tags)

    compliance_summary = combined_data['tags'].apply(check_compliance)
    combined_data['compliant'] = compliance_summary.map({True: 'Passed', False: 'Failed'})

    # Display results
    click.echo("Tag Compliance Report:")
    click.echo(combined_data[['service', 'compliant']].to_markdown(index=False))

@cli.command()
@click.option('--team', required=True, help='Team name to set budget for')
@click.option('--project', required=True, help='Project name to set budget for')
@click.option('--amount', required=True, type=float, help='Budget amount in USD')
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
def set_budget(team, project, amount, start_date, end_date):
    """Set a budget for a specific team and project."""
    click.echo(f"Setting budget for team {team}, project {project}...")
    budgets = load_budgets()
    budgets[f"{team}-{project}"] = {
        "amount": amount,
        "start_date": start_date,
        "end_date": end_date
    }
    save_budgets(budgets)
    click.echo(f"Budget of ${amount} set from {start_date} to {end_date}.")

@cli.command()
@click.option('--team', required=True, help='Team name to track budget for')
@click.option('--project', required=True, help='Project name to track budget for')
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
def track_budget(team, project, start_date, end_date, test):
    """Track spending against the budget for a specific team and project."""
    click.echo(f"Tracking budget for team {team}, project {project}...")
    budgets = load_budgets()
    key = f"{team}-{project}"
    if key not in budgets:
        click.echo("No budget set for this team and project.")
        return
    budget = budgets[key]

    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch data from each provider
    aws_data = aws_provider.get_cost_data(start_date, end_date)
    azure_data = azure_provider.get_cost_data(start_date, end_date)
    gcp_data = gcp_provider.get_cost_data(start_date, end_date)

    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])

    # Filter data for the specified team and project
    filtered_data = combined_data[combined_data['tags'].apply(lambda x: x.get('team') == team and x.get('project') == project)]

    # Calculate actual spending
    actual_spending = filtered_data['cost'].sum()

    click.echo(f"Budget: ${budget['amount']}, Actual Spending: ${actual_spending}")
    if actual_spending > budget['amount']:
        click.echo("Warning: Budget exceeded!")
    else:
        click.echo("Spending is within budget.")

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
def cost_by_service(start_date, end_date, test):
    """Generate a report showing cost breakdown by service."""
    click.echo("Generating cost breakdown by service...")
    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch data from each provider
    aws_data = aws_provider.get_cost_data(start_date, end_date)
    azure_data = azure_provider.get_cost_data(start_date, end_date)
    gcp_data = gcp_provider.get_cost_data(start_date, end_date)

    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])

    # Group by service and sum costs
    service_breakdown = combined_data.groupby('service')['cost'].sum().reset_index()

    # Display results
    click.echo("Cost Breakdown by Service:")
    click.echo(service_breakdown.to_markdown(index=False))

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
def cost_by_region(start_date, end_date, test):
    """Generate a report showing cost breakdown by region."""
    click.echo("Generating cost breakdown by region...")
    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch data from each provider
    aws_data = aws_provider.get_cost_data(start_date, end_date)
    azure_data = azure_provider.get_cost_data(start_date, end_date)
    gcp_data = gcp_provider.get_cost_data(start_date, end_date)

    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])

    # Group by region and sum costs
    region_breakdown = combined_data.groupby('region')['cost'].sum().reset_index()

    # Display results
    click.echo("Cost Breakdown by Region:")
    click.echo(region_breakdown.to_markdown(index=False))

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--forecast', required=True, type=float, help='Forecasted total spend for the period')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
def cost_efficiency_score(start_date, end_date, forecast, test):
    """Calculate and display the cost efficiency score."""
    click.echo("Calculating cost efficiency score...")
    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch data from each provider
    aws_data = aws_provider.get_cost_data(start_date, end_date)
    azure_data = azure_provider.get_cost_data(start_date, end_date)
    gcp_data = gcp_provider.get_cost_data(start_date, end_date)

    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])

    # Calculate composite score
    score = calculate_composite_score(combined_data, forecast)

    # Display results with additional information
    click.echo(f"Cost Efficiency Score: {score:.2f}")
    click.echo("Score Interpretation:")
    click.echo("- A score close to 1 indicates high cost efficiency.")
    click.echo("- A score close to 0 or negative indicates inefficiency.")
    click.echo("- Consider optimizing resources and reducing waste for better efficiency.")

if __name__ == '__main__':
    cli()
