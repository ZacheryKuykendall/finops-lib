import pandas as pd
from dataclasses import dataclass
from typing import List

@dataclass
class Recommendation:
    description: str
    estimated_savings: float
    priority: str
    category: str

def analyze_costs(cost_df: pd.DataFrame) -> List[Recommendation]:
    """Analyze cost data and return optimization recommendations."""
    recommendations = []
    
    # Check for high-cost services
    by_service = cost_df.groupby('service')['cost'].sum()
    expensive_services = by_service[by_service > by_service.mean() + by_service.std()]
    
    for service, cost in expensive_services.items():
        recommendations.append(
            Recommendation(
                description=f"High costs detected for {service}. Consider reviewing usage patterns.",
                estimated_savings=cost * 0.3,  # Assume 30% potential savings
                priority="high",
                category="optimization"
            )
        )
    
    # Check environment costs
    tags = cost_df['tags'].apply(lambda x: x.get('environment', 'unknown'))
    env_costs = cost_df.groupby(tags)['cost'].sum()
    
    if 'dev' in env_costs and env_costs['dev'] > cost_df['cost'].sum() * 0.3:
        recommendations.append(
            Recommendation(
                description="Development environment costs are unusually high (>30% of total)",
                estimated_savings=env_costs['dev'] * 0.5,
                priority="medium",
                category="environment"
            )
        )
    
    return recommendations
