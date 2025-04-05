"""
Scoring module for calculating cost efficiency and FinOps maturity scores.
This module implements industry standard metrics and scoring methods based on FinOps Foundation guidelines.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_resource_utilization(cost_data):
    """Calculate resource utilization rate.
    
    Returns a score between 0 and 1, where 1 represents optimal utilization.
    """
    # Use 'utilization' column if available
    if 'utilization' in cost_data.columns:
        utilization = cost_data['utilization'].mean()
        # Convert from 0-1 scale to a score where:
        # <40% utilization = poor (0.0-0.4 score)
        # 40-70% utilization = average (0.4-0.7 score)
        # >70% utilization = good (0.7-1.0 score)
        return min(1.0, utilization)
    else:
        # Default to 0.6 (average) if utilization data not available
        return 0.6

def calculate_resource_utilization_score(utilization_rate):
    """Calculate resource utilization score based on utilization rate.
    
    Args:
        utilization_rate: A float between 0 and 1 representing resource utilization.
        
    Returns:
        A score between 0 and 2, where higher is better.
    """
    # <40% utilization = poor (0.0-0.8 score)
    # 40-70% utilization = average (0.8-1.4 score)
    # >70% utilization = good (1.4-2.0 score)
    if utilization_rate < 0.4:
        return max(0.0, utilization_rate * 2.0)
    elif utilization_rate < 0.7:
        return 0.8 + ((utilization_rate - 0.4) / 0.3) * 0.6
    else:
        return 1.4 + ((utilization_rate - 0.7) / 0.3) * 0.6

def calculate_waste_percentage(cost_data):
    """Calculate percentage of cloud waste.
    
    Returns a score between 0 and 1, where 1 represents minimal waste.
    """
    # If we have specific waste indicators (e.g., idle resources)
    if 'is_idle' in cost_data.columns:
        waste_cost = cost_data[cost_data['is_idle']]['cost'].sum()
        total_cost = cost_data['cost'].sum()
        if total_cost > 0:
            waste_percentage = waste_cost / total_cost
            # Convert waste percentage to score (inverse relationship)
            # Industry average is ~30% waste, so we'll use that as baseline
            # 0% waste = 1.0 score, 30% waste = 0.5 score, 60%+ waste = 0.0 score
            return max(0.0, 1.0 - (waste_percentage / 0.6))
    
    # If utilization data available, use that as a proxy for waste
    if 'utilization' in cost_data.columns:
        avg_utilization = cost_data['utilization'].mean()
        # Assume waste is inverse of utilization (simplified model)
        waste_percentage = 1.0 - avg_utilization
        # Convert to score
        return max(0.0, 1.0 - (waste_percentage / 0.6))
    
    # Default to 0.5 (average) if waste data not available
    return 0.5

def calculate_waste_percentage_score(waste_percentage):
    """Calculate waste percentage score based on waste percentage.
    
    Args:
        waste_percentage: A float between 0 and 1 representing waste percentage.
        
    Returns:
        A score between 0 and 2, where higher is better (less waste).
    """
    # Convert waste percentage to score (inverse relationship)
    # 0% waste = 2.0 score, 30% waste = 1.0 score, 60%+ waste = 0.0 score
    return max(0.0, 2.0 - (waste_percentage / 0.3) * 1.0)

def calculate_discount_coverage(cost_data):
    """Calculate commitment discount coverage.
    
    Returns a score between 0 and 1, where 1 represents optimal discount coverage.
    """
    # Check if we have discount/reservation data
    if 'is_reserved_instance' in cost_data.columns or 'is_discounted' in cost_data.columns:
        discount_column = 'is_reserved_instance' if 'is_reserved_instance' in cost_data.columns else 'is_discounted'
        
        # Calculate what percentage of eligible spend is covered by discounts
        discounted_cost = cost_data[cost_data[discount_column]]['cost'].sum()
        total_cost = cost_data['cost'].sum()
        
        if total_cost > 0:
            coverage_percentage = discounted_cost / total_cost
            # Convert coverage to score
            # Industry target is ~70-80% coverage
            # <30% = poor (0.0-0.4), 30-70% = average (0.4-0.8), >70% = good (0.8-1.0)
            return min(1.0, coverage_percentage / 0.8)
    
    # If discount percentage is available
    if 'discount' in cost_data.columns:
        avg_discount = cost_data['discount'].mean()
        return min(1.0, avg_discount / 0.3)  # Assuming 30% average discount is good
    
    # Default to 0.4 (below average) if discount data not available
    return 0.4

def calculate_discount_coverage_score(coverage_percentage):
    """Calculate discount coverage score based on coverage percentage.
    
    Args:
        coverage_percentage: A float between 0 and 1 representing discount coverage.
        
    Returns:
        A score between 0 and 2, where higher is better.
    """
    # <30% = poor (0.0-0.8), 30-70% = average (0.8-1.6), >70% = good (1.6-2.0)
    if coverage_percentage < 0.3:
        return coverage_percentage * (0.8 / 0.3)
    elif coverage_percentage < 0.7:
        return 0.8 + ((coverage_percentage - 0.3) / 0.4) * 0.8
    else:
        return 1.6 + ((coverage_percentage - 0.7) / 0.3) * 0.4

def calculate_cost_allocation(cost_data):
    """Calculate cost allocation rate.
    
    Returns a score between 0 and 1, where 1 represents complete cost allocation.
    """
    # Check if we have tagging data
    if 'tags' in cost_data.columns:
        # Count resources with proper tags
        has_tags = cost_data['tags'].apply(lambda x: isinstance(x, dict) and len(x) > 0)
        tagged_cost = cost_data[has_tags]['cost'].sum()
        total_cost = cost_data['cost'].sum()
        
        if total_cost > 0:
            allocation_percentage = tagged_cost / total_cost
            # Convert to score
            # Industry benchmark aims for 95%+ tagged
            # <80% = poor, 80-95% = average, >95% = good
            return min(1.0, allocation_percentage / 0.95)
    
    # Default to 0.5 (average) if tagging data not available
    return 0.5

def calculate_cost_allocation_score(allocation_percentage):
    """Calculate cost allocation score based on allocation percentage.
    
    Args:
        allocation_percentage: A float between 0 and 1 representing cost allocation.
        
    Returns:
        A score between 0 and 2, where higher is better.
    """
    # <80% = poor (0.0-1.0), 80-95% = average (1.0-1.6), >95% = good (1.6-2.0)
    if allocation_percentage < 0.8:
        return allocation_percentage * (1.0 / 0.8)
    elif allocation_percentage < 0.95:
        return 1.0 + ((allocation_percentage - 0.8) / 0.15) * 0.6
    else:
        return 1.6 + ((allocation_percentage - 0.95) / 0.05) * 0.4

def calculate_forecast_accuracy(cost_data, forecast):
    """Calculate forecast accuracy.
    
    Returns a score between 0 and 1, where 1 represents high forecast accuracy.
    """
    if forecast:
        actual_cost = cost_data['cost'].sum()
        
        if actual_cost > 0 and forecast > 0:
            # Calculate variance as percentage
            variance_pct = abs(actual_cost - forecast) / forecast
            
            # Convert to score
            # <5% variance = excellent (0.8-1.0)
            # 5-10% variance = good (0.6-0.8)
            # 10-20% variance = average (0.4-0.6)
            # >20% variance = poor (0.0-0.4)
            if variance_pct < 0.05:
                return 1.0 - variance_pct
            elif variance_pct < 0.1:
                return 0.8 - (variance_pct - 0.05) * 4
            elif variance_pct < 0.2:
                return 0.6 - (variance_pct - 0.1) * 2
            else:
                return max(0.0, 0.4 - (variance_pct - 0.2))
    
    # Default to 0.5 (average) if forecast data not available
    return 0.5

def calculate_forecast_accuracy_score(accuracy_percentage):
    """Calculate forecast accuracy score based on accuracy percentage.
    
    Args:
        accuracy_percentage: A float between 0 and 1 representing forecast accuracy.
        
    Returns:
        A score between 0 and 2, where higher is better.
    """
    # <50% accuracy = poor (0.0-0.6), 50-80% = average (0.6-1.4), >80% = good (1.4-2.0)
    if accuracy_percentage < 0.5:
        return accuracy_percentage * (0.6 / 0.5)
    elif accuracy_percentage < 0.8:
        return 0.6 + ((accuracy_percentage - 0.5) / 0.3) * 0.8
    else:
        return 1.4 + ((accuracy_percentage - 0.8) / 0.2) * 0.6

def calculate_composite_score(scores_dict=None, cost_data=None, forecast=None):
    """Calculate a composite FinOps efficiency score based on multiple factors.
    
    This implements a comprehensive scoring model aligned with FinOps Foundation guidelines:
    - Resource Utilization (30%)
    - Discount Coverage (25%)
    - Cost Allocation (15%)
    - Forecast Accuracy (15%)
    - Waste Percentage (15%)
    
    Returns a score between 0 and 2, where higher is better:
    - 0.0-0.6: Poor efficiency
    - 0.6-1.0: Below average efficiency
    - 1.0-1.4: Average efficiency  
    - 1.4-1.8: Good efficiency
    - 1.8-2.0: Excellent efficiency
    """
    try:
        # Option 1: Use provided scores dictionary
        if scores_dict:
            weighted_score = (
                scores_dict.get('resource_utilization', 1.0) * 0.30 +     # Resource utilization (30%)
                scores_dict.get('discount_coverage', 0.8) * 0.25 +        # Discount coverage (25%)
                scores_dict.get('cost_allocation', 1.0) * 0.15 +          # Cost allocation (15%)
                scores_dict.get('forecast_accuracy', 1.0) * 0.15 +        # Forecast accuracy (15%)
                scores_dict.get('waste_percentage', 1.0) * 0.15           # Waste percentage (15%)
            )
            return weighted_score
            
        # Option 2: Calculate from cost data (legacy support)
        elif cost_data is not None:
            # Calculate individual metrics
            utilization_score = calculate_resource_utilization(cost_data)
            waste_score = calculate_waste_percentage(cost_data)
            discount_score = calculate_discount_coverage(cost_data)
            allocation_score = calculate_cost_allocation(cost_data)
            forecast_score = calculate_forecast_accuracy(cost_data, forecast)
            
            # Apply weights to each score according to FinOps Foundation recommendations
            weighted_score = (
                utilization_score * 0.30 +  # Resource utilization (30%)
                discount_score * 0.25 +     # Discount coverage (25%)
                allocation_score * 0.15 +   # Cost allocation (15%)
                forecast_score * 0.15 +     # Forecast accuracy (15%)
                waste_score * 0.15          # Waste percentage (15%)
            )
            
            # Scale to 0-2 range to provide more granularity
            final_score = weighted_score * 2
            
            logger.info(f"FinOps Composite Score: {final_score:.2f}")
            logger.info(f"Utilization: {utilization_score:.2f}, Waste: {waste_score:.2f}, "
                       f"Discount: {discount_score:.2f}, Allocation: {allocation_score:.2f}, "
                       f"Forecast: {forecast_score:.2f}")
            
            return final_score
        
        # Default fallback
        else:
            return 1.0
            
    except Exception as e:
        logger.error(f"Error calculating composite score: {e}")
        # Return a default value on error
        return 1.0

def get_score_interpretation(score):
    """Get a human-readable interpretation of the efficiency score.
    
    Returns a dict with message and list of suggestions.
    """
    interpretation = {
        "message": "Average cloud efficiency",
        "suggestions": [
            "Consider rightsizing underutilized resources",
            "Review and clean up unused resources",
            "Implement auto-scaling for variable workloads"
        ]
    }
    
    if score < 0.6:
        interpretation["message"] = "Poor cloud efficiency - significant improvements needed"
        interpretation["suggestions"] = [
            "Immediately address idle and unused resources",
            "Implement basic tagging for cost allocation",
            "Establish and track budgets for all teams",
            "Schedule a detailed cost optimization review"
        ]
    elif score < 1.0:
        interpretation["message"] = "Below average cloud efficiency - improvement opportunities exist"
        interpretation["suggestions"] = [
            "Focus on reducing waste by addressing idle resources",
            "Improve tagging compliance and cost allocation",
            "Consider reserved instances for steady-state workloads",
            "Implement basic governance policies for resource deployment"
        ]
    elif score < 1.4:
        interpretation["message"] = "Average cloud efficiency - good foundation but room to improve"
        interpretation["suggestions"] = [
            "Optimize reserved instance coverage and utilization",
            "Implement more granular cost allocation",
            "Assess storage optimization opportunities",
            "Consider automated scaling policies"
        ]
    elif score < 1.8:
        interpretation["message"] = "Good cloud efficiency - well optimized infrastructure"
        interpretation["suggestions"] = [
            "Fine-tune discount coverage strategies",
            "Advance to unit economics metrics (cost per transaction/user)",
            "Implement anomaly detection for cost spikes",
            "Explore sustainability optimizations"
        ]
    else:
        interpretation["message"] = "Excellent cloud efficiency - leading FinOps practices in place"
        interpretation["suggestions"] = [
            "Maintain current optimization practices",
            "Share FinOps practices across the organization",
            "Consider advanced rate optimization strategies",
            "Expand focus to cloud sustainability metrics"
        ]
    
    return interpretation 