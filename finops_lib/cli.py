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

# Set up logging at module level
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

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

if __name__ == '__main__':
    cli()
