# FinOps CLI Visualization

This document explains how to use the visualization capabilities of the FinOps CLI to generate charts and graphs for FinOps metrics.

## Overview

The FinOps CLI includes a visualization module (`finops_lib.visualization`) that provides functions to generate visual representations of various FinOps metrics and analyses. These visualizations can be displayed in a web interface, saved to files, or returned as base64-encoded strings for embedding in reports.

## Requirements

The visualization module requires the following Python packages, which are specified in the project's `requirements.txt` file:

* matplotlib (>= 3.5.0)
* seaborn (>= 0.11.0)

Make sure these dependencies are installed in your environment:

```bash
pip install -r requirements.txt
```

## Available Visualizations

### Resource Utilization

Generates visualizations of resource utilization, showing utilization by service and distribution across resources.

```python
from finops_lib.visualization import plot_resource_utilization
import pandas as pd

# Example: Create visualization from resource data
data = pd.DataFrame({
    'service': ['EC2', 'S3', 'RDS', 'Lambda'],
    'utilization': [0.75, 0.45, 0.82, 0.30],
    'cost': [100, 50, 200, 75]
})

# Generate and save the visualization
output_path = plot_resource_utilization(data, threshold=0.5, filename='utilization_report.png')
print(f"Visualization saved to: {output_path}")
```

### Idle Resources

Visualizes idle resources by type and inactivity duration.

```python
from finops_lib.visualization import plot_idle_resources
import pandas as pd

# Example: Create visualization from idle resource data
data = pd.DataFrame({
    'resource_id': ['r-1', 'r-2', 'r-3', 'r-4'],
    'resource_type': ['EC2', 'Storage', 'Database', 'VM'],
    'provider': ['AWS', 'AWS', 'Azure', 'GCP'],
    'monthly_cost': [50, 120, 80, 45],
    'days_inactive': [12, 5, 30, 8]
})

# Generate and save the visualization
output_path = plot_idle_resources(data, by_type=True, filename='idle_resources.png')
print(f"Visualization saved to: {output_path}")
```

### Cost Efficiency Score

Creates a radar chart of component scores and a gauge chart of the overall efficiency score.

```python
from finops_lib.visualization import plot_cost_efficiency_score

# Example: Create visualization from efficiency scores
scores = {
    'composite_score': 1.4,
    'interpretation': 'Good efficiency with some room for improvement',
    'detailed_scores': {
        'resource_utilization': 1.5,
        'waste_percentage': 1.2,
        'discount_coverage': 1.8,
        'cost_allocation': 1.3,
        'forecast_accuracy': 1.1
    }
}

# Generate and save the visualization
output_path = plot_cost_efficiency_score(scores, filename='efficiency_score.png')
print(f"Visualization saved to: {output_path}")
```

### Sustainability Metrics

Visualizes sustainability metrics including carbon emissions, power usage, and carbon intensity by region.

```python
from finops_lib.visualization import plot_sustainability_metrics

# Example: Create visualization from sustainability report
report = {
    'summary': {
        'sustainability_score': 75,
        'rating': 'Good',
        'estimated_carbon_emissions_kg': 5000,
        'estimated_power_usage_kwh': 15000
    },
    'sustainable_regions': [
        {'provider': 'AWS', 'region': 'us-west-2', 'carbon_intensity': 0.1, 'sustainability_rating': 'High'},
        {'provider': 'Azure', 'region': 'westus', 'carbon_intensity': 0.21, 'sustainability_rating': 'Medium'},
        {'provider': 'GCP', 'region': 'us-central1', 'carbon_intensity': 0.15, 'sustainability_rating': 'Medium'}
    ]
}

# Generate and save the visualization
output_path = plot_sustainability_metrics(report, filename='sustainability_report.png')
print(f"Visualization saved to: {output_path}")
```

## Integration with CLI Commands

The visualizations can be integrated with the FinOps CLI commands by adding an `--export-chart` option to generate and save charts alongside the text-based reports:

```python
@cli.command()
@click.option('--start-date', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', required=True, help='End date (YYYY-MM-DD)')
@click.option('--test', is_flag=True, help='Run in test mode with dummy data')
@click.option('--threshold', default=0.5, type=float, help='Utilization threshold (0-1)')
@click.option('--export-chart', help='Export chart to file (e.g., "utilization_chart.png")')
def resource_utilization(start_date, end_date, test, threshold, export_chart):
    """Analyze resource utilization across cloud providers."""
    # ... existing command implementation ...
    
    # Add visualization export
    if export_chart:
        from finops_lib.visualization import plot_resource_utilization
        chart_path = plot_resource_utilization(combined_data, threshold, export_chart)
        click.echo(f"\nChart exported to: {chart_path}")
```

## Web Interface Integration

The visualizations can be embedded in the web interface by returning them as base64-encoded strings:

```python
from finops_lib.visualization import plot_resource_utilization

# For web integration, don't specify a filename
chart_data = plot_resource_utilization(combined_data, threshold)

# chart_data will be a base64-encoded string that can be used in HTML
html = f"""
<html>
<body>
    <h1>Resource Utilization Report</h1>
    <img src="{chart_data}" alt="Resource Utilization Chart">
</body>
</html>
"""
```

## Customization

You can customize the visualizations by modifying the source code in `finops_lib/visualization.py`. The module uses matplotlib and seaborn for plotting, so you can adjust colors, styles, and formats according to your preferences.

## Next Steps

1. Add `--export-chart` options to the CLI commands
2. Integrate visualizations with the web interface
3. Add more specialized visualizations for specific analyses
4. Create interactive plots for the web interface using libraries like Plotly 