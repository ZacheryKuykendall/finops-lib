import click
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from .reporting import get_report
from .aws import AWSCostProvider
from .azure import AzureCostProvider
from .gcp import GCPCostProvider
from .anomaly import detect_anomalies
from .forecast import forecast_costs
import pandas as pd
from .optimize import optimize_costs
import json
from .scoring import calculate_composite_score, get_score_interpretation
from .sustainability import (
    generate_sustainability_report,
    estimate_carbon_emissions,
    get_sustainable_regions
)
import numpy as np

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
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
@click.option('--output', type=click.Choice(['console', 'json']), default='console', 
              help='Output format')
@click.option('--export', type=click.Path(), help='Export results to file')
def cost_efficiency_score(start_date, end_date, test, output, export):
    """Generate a comprehensive cost efficiency score based on multiple FinOps metrics."""
    from finops_lib.scoring import (
        calculate_resource_utilization_score,
        calculate_waste_percentage_score,
        calculate_discount_coverage_score,
        calculate_cost_allocation_score,
        calculate_forecast_accuracy_score,
        calculate_composite_score
    )
    
    click.echo("Generating comprehensive cost efficiency score...")
    
    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch cost data
    aws_data = aws_provider.get_cost_data(start_date, end_date)
    azure_data = azure_provider.get_cost_data(start_date, end_date)
    gcp_data = gcp_provider.get_cost_data(start_date, end_date)
    
    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])
    
    # If test mode and no or limited data, generate synthetic metrics
    if test and (combined_data.empty or len(combined_data) < 10):
        click.echo("Using synthetic test data for scoring.")
        metrics = {
            'resource_utilization': np.random.uniform(0.6, 0.8),
            'waste_percentage': np.random.uniform(0.2, 0.4),
            'discount_coverage': np.random.uniform(0.3, 0.7),
            'cost_allocation': np.random.uniform(0.7, 0.95),
            'forecast_accuracy': np.random.uniform(0.7, 0.9)
        }
    else:
        # Calculate real metrics from data
        # In a real implementation, these would extract actual values from the data
        metrics = {
            'resource_utilization': 0.75 if test else combined_data.get('utilization', pd.Series()).mean(),
            'waste_percentage': 0.25 if test else 1.0 - combined_data.get('utilization', pd.Series()).mean(),
            'discount_coverage': 0.60 if test else combined_data.get('discount_coverage', pd.Series()).mean(),
            'cost_allocation': 0.85 if test else combined_data.get('allocation_rate', pd.Series()).mean(),
            'forecast_accuracy': 0.80 if test else 1.0 - abs(combined_data.get('forecast_variance', pd.Series())).mean()
        }
    
    # Calculate scores for each metric
    scores = {
        'resource_utilization': calculate_resource_utilization_score(metrics['resource_utilization']),
        'waste_percentage': calculate_waste_percentage_score(metrics['waste_percentage']),
        'discount_coverage': calculate_discount_coverage_score(metrics['discount_coverage']),
        'cost_allocation': calculate_cost_allocation_score(metrics['cost_allocation']),
        'forecast_accuracy': calculate_forecast_accuracy_score(metrics['forecast_accuracy'])
    }
    
    # Calculate composite score
    composite_score = calculate_composite_score(scores)
    
    # Determine score interpretation
    if composite_score >= 1.5:
        interpretation = "Excellent - Your organization is following FinOps best practices"
    elif composite_score >= 1.0:
        interpretation = "Good - Solid cost management with room for improvement"
    elif composite_score >= 0.5:
        interpretation = "Fair - Several areas need attention to improve efficiency"
    else:
        interpretation = "Poor - Urgent attention needed to reduce waste and improve efficiency"
    
    # Generate recommendations based on lowest scores
    recommendations = []
    if scores['resource_utilization'] < 1.0:
        recommendations.append("Improve resource utilization through rightsizing and auto-scaling")
    if scores['waste_percentage'] < 1.0:
        recommendations.append("Reduce cloud waste by identifying and removing idle resources")
    if scores['discount_coverage'] < 1.0:
        recommendations.append("Increase commitment-based discount coverage through reserved instances or savings plans")
    if scores['cost_allocation'] < 1.0:
        recommendations.append("Improve tagging and cost allocation to understand spending by business unit")
    if scores['forecast_accuracy'] < 1.0:
        recommendations.append("Enhance cost forecasting accuracy to better predict and plan cloud spending")
    
    # Format and display results
    results = {
        "composite_score": round(composite_score, 2),
        "interpretation": interpretation,
        "detailed_scores": {k: round(v, 2) for k, v in scores.items()},
        "metrics": {k: round(v, 2) for k, v in metrics.items()},
        "recommendations": recommendations,
        "period": f"{start_date} to {end_date}"
    }
    
    if output == 'json':
        import json
        output_str = json.dumps(results, indent=2)
        click.echo(output_str)
    else:
        click.echo("\n📊 Cost Efficiency Score Report:")
        click.echo("=" * 50)
        click.echo(f"Period: {results['period']}")
        click.echo(f"Overall Score: {results['composite_score']:.2f} / 2.00")
        click.echo(f"Interpretation: {results['interpretation']}")
        
        click.echo("\n📈 Detailed Scores:")
        click.echo("=" * 50)
        for metric, score in results['detailed_scores'].items():
            metric_name = metric.replace('_', ' ').title()
            click.echo(f"{metric_name}: {score:.2f} / 2.00")
        
        click.echo("\n🔍 Current Metrics:")
        click.echo("=" * 50)
        for metric, value in results['metrics'].items():
            metric_name = metric.replace('_', ' ').title()
            if metric == 'waste_percentage':
                click.echo(f"{metric_name}: {value*100:.1f}%")
            elif metric in ['resource_utilization', 'discount_coverage', 'cost_allocation', 'forecast_accuracy']:
                click.echo(f"{metric_name}: {value*100:.1f}%")
            else:
                click.echo(f"{metric_name}: {value:.2f}")
        
        click.echo("\n💡 Recommendations:")
        click.echo("=" * 50)
        for i, rec in enumerate(results['recommendations'], 1):
            click.echo(f"{i}. {rec}")
    
    # Export results if requested
    if export:
        import json
        with open(export, 'w') as f:
            json.dump(results, f, indent=2)
        click.echo(f"\nResults exported to {export}")

@cli.command()
@click.option('--port', default=5000, help='Port to run the web interface on')
def web(port):
    """Launch the web interface."""
    click.echo(f"Starting web interface on http://localhost:{port}")
    from .web import start_web_interface
    start_web_interface(port)

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
@click.option('--output', default='console', type=click.Choice(['console', 'json']), 
              help='Output format (console or json file)')
@click.option('--export', help='Export to file (e.g., "sustainability_report.json")')
def sustainability_report(start_date, end_date, test, output, export):
    """Generate a sustainability report with carbon estimates and recommendations."""
    click.echo("Generating sustainability report...")
    
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
    
    # Generate report
    report = generate_sustainability_report(combined_data)
    
    # Output formatting
    if output == 'json' or export:
        report_json = json.dumps(report, indent=2)
        if export:
            with open(export, 'w') as f:
                f.write(report_json)
            click.echo(f"Report exported to: {os.path.abspath(export)}")
        else:
            click.echo(report_json)
    else:
        # Console friendly output
        summary = report['summary']
        click.echo("\n🌿 Sustainability Report Summary:")
        click.echo("=" * 50)
        click.echo(f"Sustainability Score: {summary['sustainability_score']}/100 ({summary['rating']})")
        click.echo(f"Estimated Carbon Emissions: {summary['estimated_carbon_emissions_kg']} kg CO2")
        click.echo(f"Estimated Power Usage: {summary['estimated_power_usage_kwh']} kWh")
        
        click.echo("\n🔍 Top Recommendations:")
        click.echo("=" * 50)
        for i, rec in enumerate(report['recommendations'][:5], 1):
            click.echo(f"{i}. [{rec['priority']}] {rec['recommendation']}")
            click.echo(f"   Impact: {rec['estimated_impact']}")
        
        click.echo("\n🌎 Most Sustainable Regions:")
        click.echo("=" * 50)
        for region in report['sustainable_regions'][:5]:
            click.echo(f"{region['provider']} {region['region']}: {region['carbon_intensity']} kg CO2/kWh ({region['sustainability_rating']} sustainability)")
        
        if 'carbon_intensity_by_region' in report['details'] and report['details']['carbon_intensity_by_region']:
            click.echo("\n📊 Carbon Intensity by Region:")
            click.echo("=" * 50)
            for key, data in report['details']['carbon_intensity_by_region'].items():
                click.echo(f"{key}: {data['carbon_intensity']} kg CO2/kWh ({data['cost_percentage']}% of spend)")
        
        click.echo("\nFor complete details, export the report using --export option.")

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
@click.option('--threshold', default=0.5, type=float, help='Utilization threshold (0-1) for highlighting underutilized resources')
def resource_utilization(start_date, end_date, test, threshold):
    """Analyze resource utilization across cloud providers."""
    click.echo("Analyzing resource utilization...")
    
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
    
    if 'utilization' not in combined_data.columns:
        click.echo("Warning: Utilization data not available. Using synthetic test data.")
        # Add synthetic utilization data for test mode
        if test:
            combined_data['utilization'] = np.random.uniform(0.2, 0.9, size=len(combined_data))
        else:
            click.echo("Error: No utilization data available. Please run with --test flag for demo data.")
            return
    
    # Calculate utilization metrics by service
    service_utilization = combined_data.groupby('service')['utilization'].agg(['mean', 'min', 'max']).reset_index()
    service_utilization['mean'] = service_utilization['mean'].round(2)
    service_utilization['min'] = service_utilization['min'].round(2)
    service_utilization['max'] = service_utilization['max'].round(2)
    
    # Find underutilized resources
    underutilized = combined_data[combined_data['utilization'] < threshold]
    underutilized_cost = underutilized['cost'].sum()
    total_cost = combined_data['cost'].sum()
    
    # Calculate potential savings from rightsizing
    # Assume we can save 50% of the cost of underutilized resources
    potential_savings = underutilized_cost * 0.5
    
    # Output results
    click.echo("\n📊 Resource Utilization Summary:")
    click.echo("=" * 50)
    click.echo(f"Average Utilization: {combined_data['utilization'].mean().round(2) * 100}%")
    click.echo(f"Underutilized Resources: {len(underutilized)} resources below {threshold * 100}% threshold")
    click.echo(f"Underutilized Cost: ${underutilized_cost:.2f} ({(underutilized_cost / total_cost * 100):.1f}% of total spend)")
    click.echo(f"Potential Savings from Rightsizing: ${potential_savings:.2f}")
    
    click.echo("\n📊 Utilization by Service:")
    click.echo("=" * 50)
    click.echo(service_utilization.to_markdown(index=False))
    
    if not underutilized.empty:
        click.echo("\n🔍 Top Underutilized Resources:")
        click.echo("=" * 50)
        # Sort by cost and select top 10
        top_underutilized = underutilized.sort_values(by='cost', ascending=False).head(10)
        formatted_data = top_underutilized[['service', 'region', 'utilization', 'cost']].copy()
        formatted_data['utilization'] = formatted_data['utilization'].apply(lambda x: f"{x*100:.1f}%")
        formatted_data['cost'] = formatted_data['cost'].apply(lambda x: f"${x:.2f}")
        click.echo(formatted_data.to_markdown(index=False))
        
        click.echo("\n💡 Recommendations:")
        click.echo("=" * 50)
        click.echo("1. Consider rightsizing resources with low utilization")
        click.echo("2. Implement auto-scaling for variable workloads")
        click.echo("3. Schedule non-production resources to shut down during off-hours")
        click.echo("4. Consolidate underutilized resources where possible")
        click.echo(f"5. Review resources with utilization below {threshold * 100}% threshold")

@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
@click.option('--inactive-threshold', default=7, type=int, help='Number of days of inactivity to consider a resource idle')
def idle_resources(start_date, end_date, test, inactive_threshold):
    """Detect idle resources across cloud providers."""
    click.echo("Detecting idle resources...")
    
    # Initialize providers
    aws_provider = AWSCostProvider(test_mode=test)
    azure_provider = AzureCostProvider(subscription_id="test", test_mode=test)
    gcp_provider = GCPCostProvider(project_id="test", test_mode=test)

    # Fetch data from each provider
    aws_data = aws_provider.get_resource_data(start_date, end_date, include_activity=True)
    azure_data = azure_provider.get_resource_data(start_date, end_date, include_activity=True)
    gcp_data = gcp_provider.get_resource_data(start_date, end_date, include_activity=True)

    # Combine data
    combined_data = pd.concat([aws_data, azure_data, gcp_data])
    
    # For test mode, generate synthetic data if needed
    if test and ('last_activity_date' not in combined_data.columns or combined_data.empty):
        click.echo("Using synthetic test data for idle resource detection.")
        # Create sample dataset with resource IDs, types, regions, costs, and last activity dates
        data = {
            'resource_id': [f'resource-{i}' for i in range(1, 21)],
            'resource_type': np.random.choice(['VM', 'Storage', 'Database', 'Network'], 20),
            'provider': np.random.choice(['AWS', 'Azure', 'GCP'], 20),
            'region': np.random.choice(['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'], 20),
            'monthly_cost': np.round(np.random.uniform(10, 500, 20), 2),
            'last_activity_date': [
                (datetime.now() - timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d')
                for _ in range(20)
            ]
        }
        combined_data = pd.DataFrame(data)
    
    if combined_data.empty:
        click.echo("No resource data available. Please run with --test flag for demo data.")
        return
        
    # Calculate days since last activity
    combined_data['last_activity_date'] = pd.to_datetime(combined_data['last_activity_date'])
    current_date = datetime.now()
    combined_data['days_inactive'] = (current_date - combined_data['last_activity_date']).dt.days
    
    # Identify idle resources
    idle_resources = combined_data[combined_data['days_inactive'] >= inactive_threshold].copy()
    
    # Calculate potential savings
    total_idle_cost = idle_resources['monthly_cost'].sum()
    
    # Group by resource type
    idle_by_type = idle_resources.groupby('resource_type').agg(
        count=('resource_id', 'count'),
        total_cost=('monthly_cost', 'sum'),
        avg_days_inactive=('days_inactive', 'mean')
    ).reset_index()
    
    # Group by cloud provider
    idle_by_provider = idle_resources.groupby('provider').agg(
        count=('resource_id', 'count'),
        total_cost=('monthly_cost', 'sum')
    ).reset_index()
    
    # Format the output
    idle_by_type['avg_days_inactive'] = idle_by_type['avg_days_inactive'].round(1)
    idle_by_type['total_cost'] = idle_by_type['total_cost'].round(2)
    idle_by_provider['total_cost'] = idle_by_provider['total_cost'].round(2)
    
    # Output results
    click.echo("\n🔍 Idle Resource Detection Results:")
    click.echo("=" * 50)
    click.echo(f"Total Idle Resources: {len(idle_resources)} resources inactive for {inactive_threshold}+ days")
    click.echo(f"Total Monthly Cost of Idle Resources: ${total_idle_cost:.2f}")
    click.echo(f"Potential Annual Savings: ${total_idle_cost * 12:.2f}")
    
    click.echo("\n📊 Idle Resources by Type:")
    click.echo("=" * 50)
    click.echo(idle_by_type.to_markdown(index=False))
    
    click.echo("\n📊 Idle Resources by Cloud Provider:")
    click.echo("=" * 50)
    click.echo(idle_by_provider.to_markdown(index=False))
    
    if not idle_resources.empty:
        click.echo("\n🔍 Top Idle Resources by Cost:")
        click.echo("=" * 50)
        # Sort by cost and select top 10
        top_idle = idle_resources.sort_values(by='monthly_cost', ascending=False).head(10)
        formatted_data = top_idle[['resource_id', 'resource_type', 'provider', 'days_inactive', 'monthly_cost']].copy()
        formatted_data['monthly_cost'] = formatted_data['monthly_cost'].apply(lambda x: f"${x:.2f}")
        click.echo(formatted_data.to_markdown(index=False))
        
        click.echo("\n💡 Recommendations:")
        click.echo("=" * 50)
        click.echo("1. Terminate or delete resources idle for more than 30 days")
        click.echo("2. Right-size resources with low utilization but occasional activity")
        click.echo("3. Implement automated shutdown policies for non-production resources")
        click.echo("4. Tag idle resources for review by resource owners")
        click.echo("5. Consider reserved instances or savings plans for predictable workloads")

@cli.command()
@click.option('--port', '-p', default=5050, help='Port to run the dashboard server on')
@click.option('--debug/--no-debug', default=False, help='Run the server in debug mode')
def dashboard(port, debug):
    """Start the interactive FinOps dashboard server."""
    try:
        from finops_lib.dashboard.dashboard_server import run_dashboard_server
        click.echo(f"Starting interactive dashboard server on port {port}...")
        click.echo(f"Open your browser and navigate to http://localhost:{port}")
        click.echo("Press CTRL+C to stop the server")
        run_dashboard_server(port=port, debug=debug)
    except ImportError as e:
        click.echo("Error: Required dashboard dependencies not found.")
        click.echo("Please install them with: pip install dash dash-bootstrap-components plotly")
        logger.error(f"Dashboard startup error: {e}")
    except Exception as e:
        click.echo(f"Error starting dashboard server: {e}")
        logger.error(f"Dashboard startup error: {e}")

if __name__ == '__main__':
    cli()
