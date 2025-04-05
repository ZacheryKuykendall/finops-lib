"""
Sustainability analysis module for measuring the environmental impact of cloud resources.

This module provides functions for estimating carbon emissions, analyzing resource efficiency
from a sustainability perspective, and recommending eco-friendly optimizations.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Average carbon intensity values by cloud provider region (kg CO2 per kWh)
# These are representative values - in a production system, these would come from 
# cloud provider APIs or more detailed datasets
CARBON_INTENSITY = {
    'AWS': {
        'us-east-1': 0.379,      # US East (N. Virginia)
        'us-west-1': 0.215,      # US West (N. California)
        'us-west-2': 0.136,      # US West (Oregon) - hydropower
        'eu-west-1': 0.316,      # Europe (Ireland)
        'eu-central-1': 0.338,   # Europe (Frankfurt)
        'ap-southeast-1': 0.493, # Asia Pacific (Singapore)
        'ap-southeast-2': 0.790, # Asia Pacific (Sydney)
        'default': 0.400         # Default if region not found
    },
    'Azure': {
        'eastus': 0.379,         # East US
        'westus': 0.215,         # West US
        'westus2': 0.136,        # West US 2
        'northeurope': 0.316,    # North Europe
        'westeurope': 0.232,     # West Europe
        'southeastasia': 0.493,  # Southeast Asia
        'australiaeast': 0.790,  # Australia East
        'default': 0.400         # Default if region not found
    },
    'GCP': {
        'us-east1': 0.379,       # South Carolina
        'us-west1': 0.120,       # Oregon - low carbon
        'us-central1': 0.462,    # Iowa
        'europe-west1': 0.096,   # Belgium - low carbon
        'europe-west2': 0.231,   # London
        'asia-east1': 0.626,     # Taiwan
        'asia-southeast1': 0.493, # Singapore
        'default': 0.400         # Default if region not found
    },
    'default': 0.400             # Default if provider not found
}

# Average power usage per vCPU-hour by cloud provider (kWh)
POWER_PER_VCPU_HOUR = {
    'AWS': 0.035,
    'Azure': 0.033,
    'GCP': 0.032,
    'default': 0.034
}

def get_carbon_intensity(provider, region):
    """Get carbon intensity for a specific cloud provider and region."""
    provider_dict = CARBON_INTENSITY.get(provider, CARBON_INTENSITY['default'])
    return provider_dict.get(region, provider_dict['default'])

def calculate_vcpu_hours(cost_data):
    """Estimate vCPU hours from cost data if not directly available."""
    if 'vcpu_hours' in cost_data.columns:
        return cost_data['vcpu_hours'].sum()
    
    # If CPU hours not directly available, estimate from cost and instance type
    # This is a simplified model - real implementation would be more sophisticated
    estimated_vcpu_hours = 0
    
    # If we have instance type or size data, use it to estimate
    if 'instance_type' in cost_data.columns:
        # Map common instance types to vCPU count (simplified)
        vcpu_map = {
            't2.micro': 1, 't2.small': 1, 't2.medium': 2, 't2.large': 2,
            'm5.large': 2, 'm5.xlarge': 4, 'm5.2xlarge': 8,
            'c5.large': 2, 'c5.xlarge': 4, 'c5.2xlarge': 8,
            'Standard_B1s': 1, 'Standard_B2s': 2, 'Standard_D2s_v3': 2,
            'n1-standard-1': 1, 'n1-standard-2': 2, 'n1-standard-4': 4
        }
        
        for _, row in cost_data.iterrows():
            if pd.notna(row.get('instance_type')):
                instance = row['instance_type']
                vcpus = vcpu_map.get(instance, 2)  # Default to 2 vCPUs if not found
                hours = row.get('usage_hours', 24)  # Default to 24 hours if not specified
                estimated_vcpu_hours += vcpus * hours
    else:
        # Very rough estimation based on cost
        # Assuming average cost of $0.05 per vCPU-hour
        estimated_vcpu_hours = cost_data['cost'].sum() / 0.05
    
    return max(1, estimated_vcpu_hours)  # Ensure at least 1 vCPU-hour

def estimate_power_usage(cost_data):
    """Estimate power usage in kWh based on cloud usage."""
    total_kwh = 0
    
    # If we have direct power usage data
    if 'power_usage_kwh' in cost_data.columns:
        total_kwh = cost_data['power_usage_kwh'].sum()
    else:
        # Estimate based on vCPU hours
        vcpu_hours = calculate_vcpu_hours(cost_data)
        
        # Get power usage per vCPU hour based on provider
        if 'cloud_provider' in cost_data.columns:
            providers = cost_data['cloud_provider'].unique()
            for provider in providers:
                provider_data = cost_data[cost_data['cloud_provider'] == provider]
                power_per_vcpu = POWER_PER_VCPU_HOUR.get(provider, POWER_PER_VCPU_HOUR['default'])
                provider_vcpu_hours = calculate_vcpu_hours(provider_data)
                total_kwh += provider_vcpu_hours * power_per_vcpu
        else:
            # If provider not specified, use default
            total_kwh = vcpu_hours * POWER_PER_VCPU_HOUR['default']
    
    return total_kwh

def estimate_carbon_emissions(cost_data):
    """Estimate carbon emissions (kg CO2) based on cloud usage."""
    total_emissions = 0
    
    # If we have direct carbon data
    if 'carbon_emissions_kg' in cost_data.columns:
        total_emissions = cost_data['carbon_emissions_kg'].sum()
        return total_emissions
    
    # Calculate emissions based on power usage and carbon intensity
    power_usage_kwh = estimate_power_usage(cost_data)
    
    # If we have provider and region data, use specific carbon intensity
    if 'cloud_provider' in cost_data.columns and 'region' in cost_data.columns:
        for provider in cost_data['cloud_provider'].unique():
            provider_data = cost_data[cost_data['cloud_provider'] == provider]
            
            for region in provider_data['region'].unique():
                region_data = provider_data[provider_data['region'] == region]
                
                # Get power usage for this provider/region
                region_power_kwh = estimate_power_usage(region_data)
                
                # Get carbon intensity for this provider/region
                carbon_intensity = get_carbon_intensity(provider, region)
                
                # Calculate emissions
                total_emissions += region_power_kwh * carbon_intensity
    else:
        # Use default carbon intensity
        total_emissions = power_usage_kwh * CARBON_INTENSITY['default']
    
    return total_emissions

def calculate_sustainability_score(cost_data):
    """Calculate a sustainability score from 0 to 1 based on resource efficiency and carbon emissions.
    
    A higher score means more sustainable practices.
    """
    # Calculate carbon emissions
    emissions = estimate_carbon_emissions(cost_data)
    
    # Get total cost
    total_cost = cost_data['cost'].sum()
    
    # Calculate carbon efficiency (kg CO2 per $)
    carbon_per_dollar = emissions / total_cost if total_cost > 0 else 0
    
    # Industry benchmarks (rough estimates):
    # Good: < 0.5 kg CO2 per $ 
    # Average: 0.5-1.5 kg CO2 per $
    # Poor: > 1.5 kg CO2 per $
    
    # Convert to score (0-1)
    if carbon_per_dollar <= 0.5:
        carbon_score = 1.0
    elif carbon_per_dollar <= 1.5:
        carbon_score = 1.0 - ((carbon_per_dollar - 0.5) / 1.0)
    else:
        carbon_score = max(0, 0.5 - ((carbon_per_dollar - 1.5) / 3.0))
    
    # Check resource utilization as another factor
    utilization_score = 0.5  # Default
    if 'utilization' in cost_data.columns:
        utilization_score = min(1.0, cost_data['utilization'].mean())
    
    # Check for sustainable regions
    region_score = 0.5  # Default
    if 'cloud_provider' in cost_data.columns and 'region' in cost_data.columns:
        # Calculate weighted average of region scores based on cost
        total_weighted_score = 0
        total_weight = 0
        
        for provider in cost_data['cloud_provider'].unique():
            provider_data = cost_data[cost_data['cloud_provider'] == provider]
            
            for region in provider_data['region'].unique():
                region_data = provider_data[provider_data['region'] == region]
                region_cost = region_data['cost'].sum()
                
                # Get carbon intensity for this region
                carbon_intensity = get_carbon_intensity(provider, region)
                
                # Normalize to score (lower carbon intensity = higher score)
                # 0.1 or less is excellent, 0.8 or more is poor
                region_carbon_score = max(0, min(1, 1 - (carbon_intensity / 0.8)))
                
                total_weighted_score += region_carbon_score * region_cost
                total_weight += region_cost
        
        if total_weight > 0:
            region_score = total_weighted_score / total_weight
    
    # Compute final sustainability score
    sustainability_score = (carbon_score * 0.4) + (utilization_score * 0.4) + (region_score * 0.2)
    
    return sustainability_score

def get_sustainable_regions(provider=None):
    """Get a list of the most sustainable regions for a given provider or all providers."""
    sustainable_regions = []
    
    providers = [provider] if provider else ['AWS', 'Azure', 'GCP']
    
    for p in providers:
        if p not in CARBON_INTENSITY:
            continue
            
        regions = CARBON_INTENSITY[p]
        # Filter out 'default'
        region_intensities = {r: i for r, i in regions.items() if r != 'default'}
        
        # Sort by carbon intensity (lower is better)
        sorted_regions = sorted(region_intensities.items(), key=lambda x: x[1])
        
        # Add top 3 most sustainable regions
        for region, intensity in sorted_regions[:3]:
            sustainable_regions.append({
                'provider': p,
                'region': region,
                'carbon_intensity': intensity,
                'sustainability_rating': 'High' if intensity < 0.2 else 'Medium'
            })
    
    return sustainable_regions

def generate_sustainability_recommendations(cost_data):
    """Generate sustainability-focused recommendations based on cost data."""
    recommendations = []
    
    # Calculate sustainability score
    sustainability_score = calculate_sustainability_score(cost_data)
    
    # Add general score-based recommendations
    if sustainability_score < 0.4:
        recommendations.append({
            'priority': 'High',
            'category': 'Overall',
            'recommendation': 'Significant sustainability improvements needed - consider resource optimization and workload placement',
            'estimated_impact': 'High'
        })
    
    # Check resource utilization
    if 'utilization' in cost_data.columns:
        avg_utilization = cost_data['utilization'].mean()
        if avg_utilization < 0.5:
            recommendations.append({
                'priority': 'High',
                'category': 'Resource Efficiency',
                'recommendation': 'Low resource utilization detected. Consider consolidating workloads or rightsizing resources',
                'estimated_impact': 'High'
            })
    
    # Check for resources in high-carbon regions
    if 'cloud_provider' in cost_data.columns and 'region' in cost_data.columns:
        high_carbon_costs = 0
        total_cost = cost_data['cost'].sum()
        
        for provider in cost_data['cloud_provider'].unique():
            provider_data = cost_data[cost_data['cloud_provider'] == provider]
            
            for region in provider_data['region'].unique():
                region_data = provider_data[provider_data['region'] == region]
                region_cost = region_data['cost'].sum()
                
                # Get carbon intensity for this region
                carbon_intensity = get_carbon_intensity(provider, region)
                
                # If high carbon intensity and significant cost
                if carbon_intensity > 0.5 and region_cost > (0.1 * total_cost):
                    high_carbon_costs += region_cost
                    
                    # Get alternative sustainable regions
                    alternatives = get_sustainable_regions(provider)
                    alt_regions = ', '.join([f"{a['region']} ({a['sustainability_rating']})" for a in alternatives])
                    
                    recommendations.append({
                        'priority': 'Medium',
                        'category': 'Region Selection',
                        'recommendation': f"Consider migrating workloads from {region} (high carbon intensity) to more sustainable regions: {alt_regions}",
                        'estimated_impact': 'Medium' if region_cost > (0.2 * total_cost) else 'Low'
                    })
        
        # If high percentage of costs in high-carbon regions
        if high_carbon_costs > (0.5 * total_cost):
            recommendations.append({
                'priority': 'High',
                'category': 'Region Selection',
                'recommendation': 'More than 50% of cloud spend is in high-carbon regions. Consider a sustainability-focused cloud region strategy',
                'estimated_impact': 'High'
            })
    
    # Recommend instance type improvements for compute-intensive workloads
    if 'service' in cost_data.columns:
        compute_services = ['EC2', 'Virtual Machines', 'Compute Engine', 'Kubernetes']
        compute_data = cost_data[cost_data['service'].isin(compute_services)]
        
        if not compute_data.empty and compute_data['cost'].sum() > (0.3 * cost_data['cost'].sum()):
            recommendations.append({
                'priority': 'Medium',
                'category': 'Instance Selection',
                'recommendation': 'Consider using energy-efficient instance types (e.g., AWS Graviton, AMD-based instances) for compute-intensive workloads',
                'estimated_impact': 'Medium'
            })
    
    # Add general recommendations if list is empty
    if not recommendations:
        recommendations.append({
            'priority': 'Low',
            'category': 'Best Practices',
            'recommendation': 'Implement autoscaling to match resource provisioning with actual demand',
            'estimated_impact': 'Medium'
        })
        recommendations.append({
            'priority': 'Low',
            'category': 'Best Practices',
            'recommendation': 'Consider carbon awareness in your cloud architecture decisions',
            'estimated_impact': 'Medium'
        })
    
    return recommendations

def generate_sustainability_report(cost_data):
    """Generate a comprehensive sustainability report."""
    # Calculate key sustainability metrics
    emissions = estimate_carbon_emissions(cost_data)
    power_usage = estimate_power_usage(cost_data)
    sustainability_score = calculate_sustainability_score(cost_data)
    recommendations = generate_sustainability_recommendations(cost_data)
    
    # Normalize score to 0-100 scale
    normalized_score = int(sustainability_score * 100)
    
    # Create report
    report = {
        'summary': {
            'estimated_carbon_emissions_kg': round(emissions, 2),
            'estimated_power_usage_kwh': round(power_usage, 2),
            'sustainability_score': normalized_score,
            'rating': 'Excellent' if normalized_score >= 80 else
                     'Good' if normalized_score >= 60 else
                     'Average' if normalized_score >= 40 else
                     'Below Average' if normalized_score >= 20 else
                     'Poor'
        },
        'recommendations': recommendations,
        'sustainable_regions': get_sustainable_regions(),
        'details': {
            'carbon_intensity_by_region': {},
            'power_usage_by_service': {}
        }
    }
    
    # Add regional carbon intensity details if available
    if 'cloud_provider' in cost_data.columns and 'region' in cost_data.columns:
        for provider in cost_data['cloud_provider'].unique():
            provider_data = cost_data[cost_data['cloud_provider'] == provider]
            
            for region in provider_data['region'].unique():
                region_data = provider_data[provider_data['region'] == region]
                region_cost = region_data['cost'].sum()
                carbon_intensity = get_carbon_intensity(provider, region)
                
                key = f"{provider}-{region}"
                report['details']['carbon_intensity_by_region'][key] = {
                    'carbon_intensity': carbon_intensity,
                    'cost_percentage': round((region_cost / cost_data['cost'].sum()) * 100, 2)
                }
    
    # Add service power usage details if available
    if 'service' in cost_data.columns:
        for service in cost_data['service'].unique():
            service_data = cost_data[cost_data['service'] == service]
            service_power = estimate_power_usage(service_data)
            
            report['details']['power_usage_by_service'][service] = {
                'power_usage_kwh': round(service_power, 2),
                'percentage': round((service_power / power_usage) * 100, 2) if power_usage > 0 else 0
            }
    
    return report 