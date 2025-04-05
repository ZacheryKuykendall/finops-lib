"""
Efficiency scoring module for Azure FinOps CLI
"""

import pandas as pd

def calculate_composite_score(cost_data: pd.DataFrame, forecast: float = None) -> float:
    """
    Calculate a composite efficiency score based on various metrics.
    
    Args:
        cost_data: DataFrame containing cost data
        forecast: Optional forecast amount for comparison
        
    Returns:
        float: Composite efficiency score between 0 and 1
    """
    scores = []
    
    # Resource utilization score
    if 'utilization' in cost_data.columns:
        utilization_score = cost_data['utilization'].mean()
        scores.append(utilization_score)
    
    # Cost variance score
    if forecast and not cost_data.empty:
        total_cost = cost_data['cost'].sum()
        variance = abs(total_cost - forecast) / forecast
        variance_score = max(0, 1 - variance)
        scores.append(variance_score)
    
    # Resource group distribution score
    if 'resource_group' in cost_data.columns:
        group_costs = cost_data.groupby('resource_group')['cost'].sum()
        total_cost = group_costs.sum()
        if total_cost > 0:
            distribution = (group_costs / total_cost) ** 2
            distribution_score = 1 - distribution.sum()
            scores.append(distribution_score)
    
    # Reserved instance coverage score
    if 'is_reserved_instance' in cost_data.columns:
        ri_coverage = cost_data['is_reserved_instance'].mean()
        scores.append(ri_coverage)
    
    # Return average of all available scores
    return sum(scores) / len(scores) if scores else 0.5 