"""Web interface module for Azure FinOps CLI"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union
import os

from flask import Flask, jsonify, render_template, request, send_from_directory, Response

from .azure import AzureCostProvider
from .scoring import calculate_composite_score
from .metrics import update_cost_metrics, update_budget_metrics, update_efficiency_score, get_metrics
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()
cost_provider = None

def load_config():
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'azure_subscriptions': [],
            'budgets': []
        }

def update_all_metrics():
    """Update all metrics periodically"""
    try:
        config = load_config()
        subscription_ids = [sub['id'] for sub in config['azure_subscriptions']]
        
        # Initialize Azure provider
        provider = AzureCostProvider(subscription_ids=subscription_ids)
        
        # Get latest cost data
        cost_data = provider.get_cost_data()
        budget_data = provider.get_budgets()
        
        # Calculate efficiency scores
        scores = {}
        for sub_id in subscription_ids:
            sub_data = cost_data[cost_data['subscription_id'] == sub_id]
            scores[sub_id] = calculate_composite_score(sub_data)
        
        # Update all metrics
        update_cost_metrics(cost_data)
        update_budget_metrics(budget_data)
        update_efficiency_score(scores)
        
    except Exception as e:
        app.logger.error(f"Error updating metrics: {e}")

@app.route('/metrics')
def metrics():
    """Expose metrics for Prometheus"""
    return Response(get_metrics(), mimetype='text/plain')

@app.route('/')
def index():
    """Redirect to Grafana"""
    return """
    <html>
        <head>
            <meta http-equiv="refresh" content="0; url=http://localhost:3000">
        </head>
        <body>
            <p>Redirecting to Grafana dashboard...</p>
        </body>
    </html>
    """

def start_web_interface(port=5000, subscription_id=None):
    """Start the web interface.
    
    Args:
        port: Port number to run the web server on (default: 5000)
        subscription_id: Optional subscription ID or list of IDs
    """
    global cost_provider
    # Use test subscription IDs if none provided
    if not subscription_id:
        subscription_id = ['sub-1', 'sub-2']
    cost_provider = AzureCostProvider(subscription_id)
    
    # Ensure template directory is properly set
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        
    app.template_folder = template_dir
    app.static_folder = static_dir
    
    # Start the metrics update scheduler
    scheduler.add_job(update_all_metrics, 'interval', minutes=15)
    scheduler.start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=port, debug=True)
    
    # Shut down scheduler when app stops
    scheduler.shutdown()

@app.route('/api/costs')
def get_cost_report():
    df = cost_provider.get_cost_data()
    budgets = cost_provider.get_budgets()
    
    # Process cost data
    total_cost = df['Cost'].sum()
    cost_by_service = df.groupby('ServiceName')['Cost'].sum().to_dict()
    cost_by_location = df.groupby('ResourceLocation')['Cost'].sum().to_dict()
    cost_by_resource_group = df.groupby('ResourceGroupName')['Cost'].sum().to_dict()
    
    # Get budget status
    budget_status = []
    for budget in budgets:
        budget_status.append({
            'name': budget['name'],
            'amount': budget['properties']['amount'],
            'current_spend': budget['properties']['currentSpend']['amount'],
            'forecast_spend': budget['properties']['forecastSpend']['amount']
        })
    
    return jsonify({
        'total_cost': total_cost,
        'cost_by_service': cost_by_service,
        'cost_by_location': cost_by_location,
        'cost_by_resource_group': cost_by_resource_group,
        'budgets': budget_status
    })

@app.route('/api/subscriptions', methods=['GET'])
def get_subscriptions():
    """Get list of available subscriptions."""
    config = load_config()
    return jsonify(config['azure_subscriptions'])

@app.route('/api/cost-report', methods=['POST'])
def get_cost_report_old():
    """Get cost data for the specified date range and subscriptions."""
    try:
        data = request.get_json()
        start_date = data['start_date']  # Already in YYYY-MM-DD format
        end_date = data['end_date']      # Already in YYYY-MM-DD format
        test_mode = data.get('test_mode', False)
        selected_subscriptions = data.get('subscriptions', [])  # List of selected subscription IDs

        # Get current period cost data
        cost_data = cost_provider.get_cost_data(start_date, end_date)

        # Calculate previous period dates
        current_start = datetime.strptime(start_date, '%Y-%m-%d')
        current_end = datetime.strptime(end_date, '%Y-%m-%d')
        date_diff = current_end - current_start
        prev_end = current_start - timedelta(days=1)
        prev_start = prev_end - date_diff

        # Get previous period cost data
        prev_cost_data = cost_provider.get_cost_data(
            prev_start.strftime('%Y-%m-%d'),
            prev_end.strftime('%Y-%m-%d')
        )

        # Filter by selected subscriptions if specified
        if selected_subscriptions:
            cost_data = cost_data[cost_data['subscription_id'].isin(selected_subscriptions)]
            prev_cost_data = prev_cost_data[prev_cost_data['subscription_id'].isin(selected_subscriptions)]

        # Process the data for visualization
        service_costs = cost_data.groupby(['subscription_name', 'service'])['cost'].sum().unstack(fill_value=0).to_dict()
        region_costs = cost_data.groupby(['subscription_name', 'region'])['cost'].sum().unstack(fill_value=0).to_dict()
        resource_group_costs = cost_data.groupby(['subscription_name', 'resource_group'])['cost'].sum().unstack(fill_value=0).to_dict()

        # Calculate daily trend per subscription
        daily_costs = cost_data.groupby(['date', 'subscription_name'])['cost'].sum().unstack(fill_value=0)
        daily_trend = {
            'dates': daily_costs.index.tolist(),
            'costs': {sub: daily_costs[sub].tolist() for sub in daily_costs.columns}
        }

        # Calculate month-over-month comparison
        current_total = cost_data['cost'].sum()
        prev_total = prev_cost_data['cost'].sum()
        
        month_over_month = {
            'current_period': {
                'start_date': start_date,
                'end_date': end_date,
                'total_cost': float(current_total)
            },
            'previous_period': {
                'start_date': prev_start.strftime('%Y-%m-%d'),
                'end_date': prev_end.strftime('%Y-%m-%d'),
                'total_cost': float(prev_total)
            },
            'percent_change': float(((current_total - prev_total) / prev_total) * 100) if prev_total > 0 else 0.0
        }

        # Calculate RI metrics per subscription
        ri_metrics = {}
        for sub_name in cost_data['subscription_name'].unique():
            sub_data = cost_data[cost_data['subscription_name'] == sub_name]
            ri_data = sub_data[sub_data['is_reserved_instance'] == True]
            total_instances = len(sub_data)
            ri_metrics[sub_name] = {
                'average_utilization': float(ri_data['utilization'].mean() if 'utilization' in ri_data and not ri_data.empty else 0.0),
                'coverage': float(len(ri_data) / total_instances if total_instances > 0 else 0.0),
                'potential_savings': float(sub_data['cost'].sum() * 0.3)  # Example: 30% potential savings
            }

        return jsonify({
            'service_costs': service_costs,
            'region_costs': region_costs,
            'resource_group_costs': resource_group_costs,
            'daily_trend': daily_trend,
            'ri_metrics': ri_metrics,
            'month_over_month': month_over_month
        })

    except Exception as e:
        import traceback
        print(f"Failed to get Azure cost data: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/api/efficiency-score', methods=['POST'])
def get_efficiency_score():
    """Calculate efficiency score and provide optimization recommendations."""
    try:
        data = request.get_json()
        start_date = data['start_date']  # Already in YYYY-MM-DD format
        end_date = data['end_date']      # Already in YYYY-MM-DD format
        forecast = float(data.get('forecast', 1000))
        test_mode = data.get('test_mode', False)
        selected_subscriptions = data.get('subscriptions', [])

        # Get cost data
        cost_data = cost_provider.get_cost_data(start_date, end_date)

        # Filter by selected subscriptions if specified
        if selected_subscriptions:
            cost_data = cost_data[cost_data['subscription_id'].isin(selected_subscriptions)]

        # Calculate scores per subscription
        scores = {}
        for sub_name in cost_data['subscription_name'].unique():
            sub_data = cost_data[cost_data['subscription_name'] == sub_name]
            sub_score = calculate_composite_score(sub_data, forecast)
            scores[sub_name] = {
                'score': sub_score,
                'interpretation': interpret_score(sub_score, sub_data)
            }
        
        # Calculate overall score
        overall_score = calculate_composite_score(cost_data, forecast)
        scores['overall'] = {
            'score': overall_score,
            'interpretation': interpret_score(overall_score, cost_data)
        }
        
        return jsonify(scores)

    except Exception as e:
        print(f"Failed to calculate efficiency score: {str(e)}")
        return jsonify({'error': str(e)}), 500

def interpret_score(score: float, cost_data: 'pd.DataFrame') -> Dict[str, Union[str, List[str]]]:
    """Interpret the efficiency score and generate recommendations."""
    message = ""
    suggestions = []

    if score >= 0.8:
        message = "Excellent cost optimization!"
        suggestions = [
            "Consider sharing your best practices with other teams",
            "Monitor for any changes in usage patterns",
            "Review any remaining unoptimized resources"
        ]
    elif score >= 0.6:
        message = "Good cost management, with room for improvement"
        suggestions = [
            "Review underutilized reserved instances",
            "Check for resources running in non-business hours",
            "Analyze resource sizing for potential downsizing"
        ]
    else:
        message = "Significant optimization opportunities identified"
        suggestions = [
            "Implement automated resource scheduling",
            "Review and consolidate redundant resources",
            "Consider reserved instances for stable workloads",
            "Implement strict tagging policies for better cost allocation"
        ]

    # Add data-driven suggestions
    if 'utilization' in cost_data.columns and cost_data['utilization'].mean() < 0.6:
        suggestions.append("Multiple resources have low utilization - consider rightsizing")
    
    if 'is_reserved_instance' in cost_data.columns:
        ri_coverage = len(cost_data[cost_data['is_reserved_instance']]) / len(cost_data)
        if ri_coverage < 0.3:
            suggestions.append("Low reserved instance coverage - analyze stable workloads for RI opportunities")

    return {
        'message': message,
        'suggestions': suggestions[:5]  # Limit to top 5 suggestions
    } 