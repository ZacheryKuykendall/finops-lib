from flask import Flask, render_template, request, jsonify, Response
from datetime import datetime, timedelta
import pandas as pd
from .azure import AzureCostProvider
from .scoring import calculate_composite_score
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge, REGISTRY
from flask_cors import CORS
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import click
from pathlib import Path
from .reporting import get_report
from .aws import AWSCostProvider
from .gcp import GCPCostProvider
from .anomaly import detect_anomalies
from .forecast import forecast_costs
from .optimize import optimize_costs
from .config import load_config

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clear any existing metrics
for collector in list(REGISTRY._collector_to_names.keys()):
    REGISTRY.unregister(collector)

# Define Prometheus metrics
COST_BY_SERVICE = Gauge('azure_cost_by_service', 'Cost by Azure service', ['service'])
COST_BY_RESOURCE_GROUP = Gauge('azure_cost_by_resource_group', 'Cost by resource group', ['resource_group'])
BUDGET_USAGE = Gauge('azure_budget_usage', 'Budget usage percentage', ['team'])
EFFICIENCY_SCORE = Gauge('azure_efficiency_score', 'FinOps efficiency score')

def update_metrics():
    """Update all Prometheus metrics with latest data"""
    try:
        logger.info("Updating metrics...")
        # Initialize Azure provider in test mode
        azure_provider = AzureCostProvider(subscription_id="test", test_mode=True)
        
        # Get current date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Get cost data
        cost_data = azure_provider.get_cost_data(start_date, end_date)
        
        # Update service costs
        service_costs = cost_data.groupby('service')['cost'].sum()
        for service, cost in service_costs.items():
            COST_BY_SERVICE.labels(service=service).set(cost)
        
        # Update resource group costs
        rg_costs = cost_data.groupby('resource_group')['cost'].sum()
        for rg, cost in rg_costs.items():
            COST_BY_RESOURCE_GROUP.labels(resource_group=rg).set(cost)
        
        # Update budget usage
        budget_data = azure_provider.get_budget_data(start_date, end_date)
        for budget in budget_data.to_dict('records'):
            if 'name' in budget and 'amount' in budget and 'currentSpend' in budget:
                usage_percent = (budget['currentSpend'] / budget['amount']) * 100
                BUDGET_USAGE.labels(team=budget['name']).set(usage_percent)
        
        # Update efficiency score
        score = calculate_composite_score(cost_data)
        EFFICIENCY_SCORE.set(score)
        
        logger.info("Metrics update completed successfully")
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_metrics, trigger="interval", minutes=1)  # Update more frequently for testing
scheduler.start()

# Update metrics immediately
update_metrics()

@app.route('/metrics')
def metrics():
    """Expose metrics for Prometheus"""
    try:
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Error generating metrics: {str(e)}", exc_info=True)
        return Response(str(e), status=500)

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('index.html')

@app.route('/api/cost-report', methods=['POST'])
def get_cost_report():
    """Generate a cost report based on the provided parameters"""
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        test_mode = data.get('test_mode', True)
        tags = data.get('tags', {})

        # Initialize Azure provider with test mode
        azure_provider = AzureCostProvider(subscription_id="test", test_mode=test_mode)

        # Get cost data from Azure
        azure_data = azure_provider.get_cost_data(start_date, end_date)

        # Calculate costs by different dimensions
        service_costs = azure_data.groupby('service')['cost'].sum().to_dict()
        region_costs = azure_data.groupby('region')['cost'].sum().to_dict()

        # Calculate RI metrics
        ri_metrics = {
            'average_utilization': azure_data['utilization'].mean() if 'utilization' in azure_data.columns else 0.8,
            'coverage': 0.6,  # Default coverage for test mode
            'potential_savings': azure_data['cost'].sum() * 0.3  # Estimate 30% potential savings
        }

        # Get budget data
        budget_data = azure_provider.get_budget_data(start_date, end_date).to_dict('records')
        if not budget_data:
            budget_data = [{
                'name': 'Monthly Budget',
                'amount': 10000,
                'currentSpend': azure_data['cost'].sum(),
                'forecastSpend': azure_data['cost'].sum() * 1.2
            }]

        # Prepare tabular data
        tabular_data = azure_data.groupby(['service', 'region'])['cost'].sum().reset_index()
        tabular_data['cost'] = tabular_data['cost'].round(2)

        return jsonify({
            'service_costs': service_costs,
            'region_costs': region_costs,
            'ri_metrics': ri_metrics,
            'budget_data': budget_data,
            'tabular_data': tabular_data.to_dict('records')
        })
    except Exception as e:
        logger.error(f"Error in cost report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/efficiency-score', methods=['POST'])
def get_efficiency_score():
    """Calculate and return the efficiency score"""
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        test_mode = data.get('test_mode', True)

        # Initialize Azure provider with test mode
        azure_provider = AzureCostProvider(subscription_id="test", test_mode=test_mode)

        # Get cost data from Azure
        azure_data = azure_provider.get_cost_data(start_date, end_date)

        # Calculate efficiency score
        score = calculate_composite_score(azure_data)

        # Generate interpretation
        interpretation = {
            'message': 'Your cloud efficiency is good, but there is room for improvement.',
            'suggestions': [
                'Consider rightsizing underutilized resources',
                'Review and clean up unused resources',
                'Implement auto-scaling for variable workloads'
            ]
        }

        if score > 1.5:
            interpretation['message'] = 'Excellent cloud efficiency!'
            interpretation['suggestions'].append('Maintain current optimization practices')
        elif score < 0.8:
            interpretation['message'] = 'Cloud efficiency needs improvement'
            interpretation['suggestions'].append('Schedule a detailed cost optimization review')

        return jsonify({
            'score': round(score, 2),
            'interpretation': interpretation
        })
    except Exception as e:
        logger.error(f"Error calculating efficiency score: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    """Get budget data"""
    try:
        # Initialize Azure provider in test mode
        azure_provider = AzureCostProvider(subscription_id="test", test_mode=True)
        
        # Get current date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Get budget data
        budget_data = azure_provider.get_budget_data(start_date, end_date)
        return jsonify(budget_data.to_dict('records'))
    except Exception as e:
        logger.error(f"Error getting budgets: {e}")
        return jsonify({'error': str(e)}), 500

def start_web_interface(port=5000):
    """Start the Flask web server"""
    try:
        # Start the metrics update scheduler
        scheduler.add_job(update_metrics, 'interval', minutes=1)
        scheduler.start()

        # Start the Flask app
        logger.info(f"Starting web interface on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f"Error starting web interface: {e}")
    finally:
        scheduler.shutdown() 