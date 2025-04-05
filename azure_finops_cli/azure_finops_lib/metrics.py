from prometheus_client import Gauge, CollectorRegistry, generate_latest
import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create a registry for our metrics
registry = CollectorRegistry()

# Define our metrics
AZURE_COST_TOTAL = Gauge('azure_cost_total', 'Total Azure costs in USD', ['subscription_id', 'service'], registry=registry)
AZURE_BUDGET_USAGE = Gauge('azure_budget_usage_percent', 'Budget usage percentage', ['subscription_id', 'budget_name'], registry=registry)
AZURE_RESOURCE_COST = Gauge('azure_resource_cost', 'Cost by resource', ['subscription_id', 'resource_group', 'resource_type'], registry=registry)
AZURE_EFFICIENCY_SCORE = Gauge('azure_efficiency_score', 'FinOps efficiency score', ['subscription_id'], registry=registry)

def update_cost_metrics(cost_data: pd.DataFrame) -> None:
    """Update Prometheus metrics with latest cost data"""
    try:
        # Reset all metrics
        AZURE_COST_TOTAL._metrics.clear()
        AZURE_RESOURCE_COST._metrics.clear()
        
        # Update total costs by service
        service_costs = cost_data.groupby(['subscription_id', 'service'])['cost'].sum()
        for (sub_id, service), cost in service_costs.items():
            AZURE_COST_TOTAL.labels(subscription_id=sub_id, service=service).set(cost)
            
        # Update resource costs
        resource_costs = cost_data.groupby(['subscription_id', 'resource_group', 'resource_type'])['cost'].sum()
        for (sub_id, rg, rtype), cost in resource_costs.items():
            AZURE_RESOURCE_COST.labels(
                subscription_id=sub_id,
                resource_group=rg,
                resource_type=rtype
            ).set(cost)
            
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")

def update_budget_metrics(budget_data: Dict[str, Any]) -> None:
    """Update budget-related metrics"""
    try:
        AZURE_BUDGET_USAGE._metrics.clear()
        
        for budget in budget_data['value']:
            current_spend = budget['properties']['currentSpend']['amount']
            total_amount = budget['properties']['amount']
            usage_percent = (current_spend / total_amount) * 100
            
            # Extract subscription ID from budget ID
            sub_id = budget['id'].split('/')[2]
            
            AZURE_BUDGET_USAGE.labels(
                subscription_id=sub_id,
                budget_name=budget['name']
            ).set(usage_percent)
            
    except Exception as e:
        logger.error(f"Error updating budget metrics: {e}")

def update_efficiency_score(scores: Dict[str, float]) -> None:
    """Update efficiency score metrics"""
    try:
        AZURE_EFFICIENCY_SCORE._metrics.clear()
        
        for sub_id, score in scores.items():
            AZURE_EFFICIENCY_SCORE.labels(subscription_id=sub_id).set(score)
            
    except Exception as e:
        logger.error(f"Error updating efficiency score metrics: {e}")

def get_metrics() -> bytes:
    """Get all metrics in Prometheus format"""
    return generate_latest(registry) 