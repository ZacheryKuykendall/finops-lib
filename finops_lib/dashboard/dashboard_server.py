"""
Dashboard server module for the FinOps CLI.

This module sets up a Flask server and initializes the dashboard application.
"""

import os
from flask import Flask, render_template, jsonify, request
import logging
from threading import Thread
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json

from finops_lib.dashboard.dashboard import create_dashboard_app

logger = logging.getLogger(__name__)

def create_server(port=5050, debug=False):
    """
    Create a Flask server for the dashboard.
    
    Args:
        port: Port to run the server on
        debug: Whether to run in debug mode
        
    Returns:
        Flask: The Flask server
    """
    server = Flask(__name__)
    
    # Initialize dashboard
    dashboard_app = create_dashboard_app(server)
    
    # API routes for the dashboard data
    
    @server.route('/')
    def home():
        """Home page route that redirects to the dashboard."""
        return render_template('index.html')
    
    @server.route('/api/cost-data')
    def cost_data():
        """API endpoint for cost data."""
        try:
            # Get query parameters
            start_date = request.args.get('start_date', 
                                         (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
            providers = request.args.getlist('providers')
            
            # Generate sample data for demonstration
            # In a real implementation, you would fetch this from your database or cloud APIs
            data = generate_sample_cost_data(start_date, end_date, providers)
            
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting cost data: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @server.route('/api/resource-data')
    def resource_data():
        """API endpoint for resource utilization data."""
        try:
            # Get query parameters
            providers = request.args.getlist('providers')
            
            # Generate sample data for demonstration
            data = generate_sample_resource_data(providers)
            
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting resource data: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @server.route('/api/sustainability-data')
    def sustainability_data():
        """API endpoint for sustainability data."""
        try:
            # Get query parameters
            start_date = request.args.get('start_date', 
                                         (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
            providers = request.args.getlist('providers')
            
            # Generate sample data for demonstration
            data = generate_sample_sustainability_data(start_date, end_date, providers)
            
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting sustainability data: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @server.route('/api/efficiency-scores')
    def efficiency_scores():
        """API endpoint for efficiency scores."""
        try:
            # Generate sample data for demonstration
            data = generate_sample_efficiency_scores()
            
            return jsonify(data)
        except Exception as e:
            logger.error(f"Error getting efficiency scores: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @server.route('/templates/index.html')
    def index_template():
        """Serve the index template."""
        return render_template('index.html')
    
    # Create templates directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    
    # Create index.html template
    index_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinOps Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .container-fluid {
                margin-top: 20px;
            }
            .redirect-message {
                text-align: center;
                margin-top: 50px;
            }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body redirect-message">
                            <h1>FinOps Dashboard</h1>
                            <p class="lead">Welcome to the FinOps Dashboard</p>
                            <p>You will be redirected to the dashboard in a moment...</p>
                            <a href="/dashboard/" class="btn btn-primary">Go to Dashboard</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
            // Redirect to dashboard after 2 seconds
            setTimeout(function() {
                window.location.href = "/dashboard/";
            }, 2000);
        </script>
    </body>
    </html>
    """
    
    # Save the template
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    with open(template_path, 'w') as f:
        f.write(index_html)
    
    return server

def run_dashboard_server(port=5050, debug=False):
    """
    Run the dashboard server.
    
    Args:
        port: Port to run the server on
        debug: Whether to run in debug mode
    """
    server = create_server(port, debug)
    
    logger.info(f"Starting dashboard server on port {port}")
    server.run(host='0.0.0.0', port=port, debug=debug)

def start_dashboard_server_thread(port=5050, debug=False):
    """
    Start the dashboard server in a separate thread.
    
    Args:
        port: Port to run the server on
        debug: Whether to run in debug mode
        
    Returns:
        Thread: The server thread
    """
    server_thread = Thread(
        target=run_dashboard_server,
        args=(port, debug),
        daemon=True
    )
    server_thread.start()
    logger.info(f"Dashboard server thread started on port {port}")
    return server_thread

# Helper functions for generating sample data

def generate_sample_cost_data(start_date, end_date, providers=None):
    """Generate sample cost data for demonstration."""
    # Convert string dates to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Use default providers if none specified
    if not providers:
        providers = ['AWS', 'Azure', 'GCP']
    
    # Generate date range
    date_range = [start_date + timedelta(days=i) for i in 
                 range((end_date - start_date).days + 1)]
    
    # Services by provider
    services = {
        'AWS': ['EC2', 'S3', 'RDS', 'Lambda', 'ECS', 'CloudFront'],
        'Azure': ['Virtual Machines', 'Storage', 'SQL Database', 'Functions', 'App Service', 'CDN'],
        'GCP': ['Compute Engine', 'Cloud Storage', 'Cloud SQL', 'Cloud Functions', 'GKE', 'CDN']
    }
    
    # Regions by provider
    regions = {
        'AWS': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'sa-east-1'],
        'Azure': ['eastus', 'westus2', 'westeurope', 'southeastasia', 'brazilsouth'],
        'GCP': ['us-east1', 'us-west1', 'europe-west1', 'asia-southeast1', 'southamerica-east1']
    }
    
    data = []
    
    # Generate random cost data for each date, provider, service, and region
    for date in date_range:
        for provider in providers:
            for service in services.get(provider, []):
                for region in regions.get(provider, [])[:2]:  # Limit to 2 regions per service for brevity
                    # Generate random cost with some time-based trends
                    base_cost = {
                        'AWS': 100,
                        'Azure': 80,
                        'GCP': 60
                    }.get(provider, 50)
                    
                    # Add some randomness and trends
                    day_factor = date.weekday() / 7  # Weekend dip
                    trend_factor = (date - start_date).days / max((end_date - start_date).days, 1)  # Upward trend
                    random_factor = np.random.normal(1, 0.2)  # Random variation
                    
                    cost = base_cost * (1 - 0.3 * day_factor + 0.5 * trend_factor) * random_factor
                    
                    data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'provider': provider,
                        'service': service,
                        'region': region,
                        'cost': round(cost, 2)
                    })
    
    return data

def generate_sample_resource_data(providers=None):
    """Generate sample resource utilization data."""
    # Use default providers if none specified
    if not providers:
        providers = ['AWS', 'Azure', 'GCP']
    
    # Resource types by provider
    resource_types = {
        'AWS': ['EC2', 'RDS', 'ElastiCache', 'ECS'],
        'Azure': ['Virtual Machine', 'SQL Database', 'Redis Cache', 'AKS'],
        'GCP': ['Compute Engine', 'Cloud SQL', 'Memorystore', 'GKE']
    }
    
    # Sizes by provider
    sizes = {
        'AWS': ['t3.micro', 't3.small', 't3.medium', 'm5.large', 'm5.xlarge', 'r5.large'],
        'Azure': ['B2s', 'B2ms', 'D2s_v3', 'D4s_v3', 'E2s_v3', 'E4s_v3'],
        'GCP': ['e2-micro', 'e2-small', 'e2-medium', 'n1-standard-2', 'n1-standard-4', 'n1-highmem-2']
    }
    
    data = []
    
    # Generate ~100 resources
    for i in range(100):
        provider = np.random.choice(providers)
        resource_type = np.random.choice(resource_types.get(provider, ['Generic']))
        size = np.random.choice(sizes.get(provider, ['Medium']))
        
        # Generate random utilization with some patterns
        if resource_type in ['EC2', 'Virtual Machine', 'Compute Engine']:
            # VMs tend to have lower utilization
            utilization = np.random.beta(2, 3)
        elif resource_type in ['RDS', 'SQL Database', 'Cloud SQL']:
            # Databases tend to have medium utilization
            utilization = np.random.beta(3, 3)
        else:
            # Other services have varied utilization
            utilization = np.random.beta(2, 2)
        
        # Larger instances tend to have lower utilization
        if 'large' in size.lower() or 'xlarge' in size.lower():
            utilization *= 0.8
        
        # Calculate cost based on size and type
        base_cost = 20  # Base monthly cost
        if 'micro' in size.lower() or 'small' in size.lower():
            size_factor = 0.5
        elif 'medium' in size.lower() or 'standard-2' in size.lower():
            size_factor = 1.0
        else:
            size_factor = 2.0
            
        if resource_type in ['RDS', 'SQL Database', 'Cloud SQL']:
            type_factor = 2.0  # Databases cost more
        else:
            type_factor = 1.0
            
        monthly_cost = base_cost * size_factor * type_factor
        
        # Generate days inactive (most resources are active)
        if np.random.random() < 0.2:  # 20% chance of being inactive
            days_inactive = np.random.randint(1, 30)
        else:
            days_inactive = 0
        
        data.append({
            'resource_id': f"{provider.lower()}-{resource_type.lower().replace(' ', '-')}-{i}",
            'provider': provider,
            'resource_type': resource_type,
            'size': size,
            'utilization': round(utilization, 2),
            'monthly_cost': round(monthly_cost, 2),
            'days_inactive': days_inactive
        })
    
    return data

def generate_sample_sustainability_data(start_date, end_date, providers=None):
    """Generate sample sustainability data."""
    # Convert string dates to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Use default providers if none specified
    if not providers:
        providers = ['AWS', 'Azure', 'GCP']
    
    # Generate monthly data points
    months = []
    current = start_date.replace(day=1)
    while current <= end_date:
        months.append(current)
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    
    # Carbon intensity by region
    region_intensity = {
        # AWS regions
        'us-east-1': 460,       # N. Virginia - high carbon
        'us-west-2': 120,       # Oregon - low carbon (hydro)
        'eu-west-1': 250,       # Ireland - medium
        'eu-central-1': 350,    # Frankfurt - medium-high
        'ap-southeast-2': 790,  # Sydney - very high
        
        # Azure regions
        'eastus': 470,          # Virginia - high
        'westus2': 130,         # Washington - low
        'westeurope': 230,      # Netherlands - medium
        'northeurope': 170,     # Ireland - medium-low
        'australiaeast': 780,   # NSW - very high
        
        # GCP regions
        'us-east1': 450,        # S. Carolina - high
        'us-west1': 110,        # Oregon - low
        'europe-west1': 210,    # Belgium - medium
        'europe-north1': 70,    # Finland - very low
        'australia-southeast1': 770  # Sydney - very high
    }
    
    # Regions by provider
    provider_regions = {
        'AWS': ['us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-southeast-2'],
        'Azure': ['eastus', 'westus2', 'westeurope', 'northeurope', 'australiaeast'],
        'GCP': ['us-east1', 'us-west1', 'europe-west1', 'europe-north1', 'australia-southeast1']
    }
    
    # Generate emissions data
    emissions_data = []
    regions_data = []
    
    # Emissions over time
    for month in months:
        for provider in providers:
            for region in provider_regions.get(provider, []):
                # Base power usage in kWh
                base_power = {
                    'AWS': 10000,
                    'Azure': 8000,
                    'GCP': 6000
                }.get(provider, 5000)
                
                # Add some randomness and trends
                month_factor = 1 + 0.1 * (month.month % 12) / 12  # Seasonal variation
                trend_factor = 1 + 0.3 * (month - start_date).days / max((end_date - start_date).days, 1)  # Growth trend
                random_factor = np.random.normal(1, 0.1)  # Random variation
                
                power_usage_kwh = base_power * month_factor * trend_factor * random_factor
                
                # Calculate emissions
                carbon_intensity = region_intensity.get(region, 300)  # g CO2/kWh
                emissions_kg = power_usage_kwh * carbon_intensity / 1000  # Convert g to kg
                
                emissions_data.append({
                    'date': month.strftime('%Y-%m-%d'),
                    'provider': provider,
                    'region': region,
                    'power_usage_kwh': round(power_usage_kwh, 2),
                    'carbon_intensity': carbon_intensity,
                    'emissions_kg': round(emissions_kg, 2)
                })
    
    # Region sustainability data
    for provider in providers:
        for region in provider_regions.get(provider, []):
            carbon_intensity = region_intensity.get(region, 300)
            
            # Determine sustainability score (0-100)
            if carbon_intensity < 100:
                sustainability_score = 90 + np.random.randint(0, 10)
            elif carbon_intensity < 200:
                sustainability_score = 70 + np.random.randint(0, 20)
            elif carbon_intensity < 300:
                sustainability_score = 50 + np.random.randint(0, 20)
            elif carbon_intensity < 500:
                sustainability_score = 30 + np.random.randint(0, 20)
            else:
                sustainability_score = 10 + np.random.randint(0, 20)
            
            regions_data.append({
                'provider': provider,
                'region': region,
                'carbon_intensity': carbon_intensity,
                'sustainability_score': sustainability_score
            })
    
    # Generate carbon savings opportunities
    recommendations = [
        'Migrate to low-carbon regions',
        'Utilize renewable energy purchases',
        'Rightsize overprovisioned resources',
        'Implement autoscaling for variable workloads',
        'Utilize modern, energy-efficient instance types',
        'Turn off development/test environments outside business hours'
    ]
    
    opportunities_data = []
    
    for provider in providers:
        for recommendation in recommendations:
            # Generate random potential savings
            if recommendation == 'Migrate to low-carbon regions':
                savings = np.random.uniform(5000, 15000)
            elif recommendation == 'Rightsize overprovisioned resources':
                savings = np.random.uniform(2000, 8000)
            else:
                savings = np.random.uniform(1000, 5000)
                
            opportunities_data.append({
                'provider': provider,
                'recommendation': recommendation,
                'potential_carbon_savings': round(savings, 2),
                'difficulty': np.random.choice(['Low', 'Medium', 'High'])
            })
    
    return {
        'emissions': emissions_data,
        'regions': regions_data,
        'opportunities': opportunities_data
    }

def generate_sample_efficiency_scores():
    """Generate sample efficiency scores."""
    # Overall score (0-2 scale)
    overall_score = round(np.random.uniform(0.8, 1.8), 2)
    
    # Component scores
    scores = [
        {'metric': 'Resource Utilization', 'score': round(np.random.uniform(0.6, 2.0), 2)},
        {'metric': 'Waste Percentage', 'score': round(np.random.uniform(0.5, 1.8), 2)},
        {'metric': 'Discount Coverage', 'score': round(np.random.uniform(0.7, 1.9), 2)},
        {'metric': 'Cost Allocation', 'score': round(np.random.uniform(0.9, 2.0), 2)},
        {'metric': 'Forecast Accuracy', 'score': round(np.random.uniform(0.6, 1.7), 2)}
    ]
    
    # Score interpretation
    if overall_score < 0.6:
        interpretation = "Poor: Significant improvement needed in multiple areas."
    elif overall_score < 1.0:
        interpretation = "Below Average: Several areas need attention."
    elif overall_score < 1.4:
        interpretation = "Average: Some improvements could yield benefits."
    elif overall_score < 1.8:
        interpretation = "Good: Strong practices with minor improvement opportunities."
    else:
        interpretation = "Excellent: Mature FinOps practices across all dimensions."
    
    return {
        'overall_score': overall_score,
        'scores': scores,
        'interpretation': interpretation
    } 