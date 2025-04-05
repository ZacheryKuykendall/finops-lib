"""
Visualization module for FinOps CLI.
This module provides functions to generate charts and graphs for various FinOps metrics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

# Set default style for all plots
plt.style.use('ggplot')
sns.set_context("talk")
colors = sns.color_palette("Set2")

def setup_plot(figsize=(10, 6)):
    """Set up a new matplotlib figure with default styling."""
    fig, ax = plt.subplots(figsize=figsize)
    return fig, ax

def save_plot(fig, filename=None, format='png', dpi=100):
    """Save plot to file or return as base64 encoded string.
    
    Args:
        fig: Matplotlib figure
        filename: Path to save the figure
        format: Image format (png, jpg, svg, pdf)
        dpi: Resolution
        
    Returns:
        If filename is None, returns base64 encoded string
        Otherwise, saves to file and returns the path
    """
    if filename is None:
        # Return as base64 encoded string
        buffer = io.BytesIO()
        fig.savefig(buffer, format=format, bbox_inches='tight', dpi=dpi)
        buffer.seek(0)
        image_data = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        return f"data:image/{format};base64,{image_data}"
    else:
        # Save to file
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        fig.savefig(filename, format=format, bbox_inches='tight', dpi=dpi)
        plt.close(fig)
        return os.path.abspath(filename)

def plot_resource_utilization(data, threshold=0.5, filename=None):
    """Generate a resource utilization visualization.
    
    Args:
        data: DataFrame with resource utilization data
        threshold: Utilization threshold (0-1)
        filename: Optional path to save the plot
        
    Returns:
        Path to saved file or base64 encoded string
    """
    try:
        # Create service utilization chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Service utilization bar chart
        if 'service' in data.columns and 'utilization' in data.columns:
            service_util = data.groupby('service')['utilization'].mean().sort_values()
            
            # Plot bars
            colors = ['#e74c3c' if x < threshold else '#2ecc71' for x in service_util]
            service_util.plot(kind='barh', ax=ax1, color=colors)
            
            # Add a vertical line at the threshold
            ax1.axvline(x=threshold, color='#3498db', linestyle='--', alpha=0.7)
            ax1.text(threshold, -0.5, f'Threshold ({threshold*100:.0f}%)', 
                    color='#3498db', ha='center', va='top', rotation=90)
            
            # Format axes
            ax1.set_xlabel('Average Utilization')
            ax1.set_title('Resource Utilization by Service')
            ax1.set_xlim(0, 1)
            
            # Format tick labels to show percentage
            ax1.set_xticklabels([f'{x:.0%}' for x in ax1.get_xticks()])
        
        # Utilization distribution chart
        if 'utilization' in data.columns:
            # Create histogram with density plot
            sns.histplot(data['utilization'], bins=20, kde=True, ax=ax2, color='#3498db')
            
            # Add a vertical line at the threshold
            ax2.axvline(x=threshold, color='#e74c3c', linestyle='--')
            ax2.text(threshold, ax2.get_ylim()[1]*0.9, f'Threshold\n({threshold*100:.0f}%)', 
                    color='#e74c3c', ha='center', va='top')
            
            # Calculate percentage below threshold
            below_threshold = (data['utilization'] < threshold).mean() * 100
            ax2.text(0.05, ax2.get_ylim()[1]*0.9, 
                   f'{below_threshold:.1f}% of resources\nbelow threshold', 
                   color='#e74c3c', ha='left', va='top')
            
            # Format axes
            ax2.set_xlabel('Utilization')
            ax2.set_ylabel('Count')
            ax2.set_title('Distribution of Resource Utilization')
            
            # Format x-axis as percentage
            ax2.set_xticklabels([f'{x:.0%}' for x in ax2.get_xticks()])
        
        plt.tight_layout()
        return save_plot(fig, filename)
        
    except Exception as e:
        logger.error(f"Error creating resource utilization plot: {e}")
        return None

def plot_idle_resources(data, by_type=True, filename=None):
    """Generate idle resources visualization.
    
    Args:
        data: DataFrame with idle resource data
        by_type: Whether to group by resource type (True) or provider (False)
        filename: Optional path to save the plot
        
    Returns:
        Path to saved file or base64 encoded string
    """
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Check required columns
        required_cols = ['resource_type', 'provider', 'monthly_cost', 'days_inactive']
        if not all(col in data.columns for col in required_cols):
            logger.error(f"Missing required columns for idle resources plot: {required_cols}")
            return None
        
        # Select group column based on parameter
        group_col = 'resource_type' if by_type else 'provider'
        
        # Count and total cost by group
        grouped = data.groupby(group_col).agg(
            count=('resource_type', 'count'),
            total_cost=('monthly_cost', 'sum')
        ).sort_values('total_cost', ascending=False)
        
        # Cost by group (pie chart)
        plt.sca(ax1)
        plt.pie(grouped['total_cost'], labels=grouped.index, autopct='%1.1f%%', 
                startangle=90, shadow=False, 
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
        ax1.set_title(f'Idle Resource Cost by {group_col.title()}')
        ax1.set_ylabel('')
        
        # Inactivity distribution (box plot)
        plt.sca(ax2)
        order = data.groupby(group_col)['days_inactive'].median().sort_values(ascending=False).index
        sns.boxplot(x=group_col, y='days_inactive', data=data, ax=ax2, order=order)
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
        ax2.set_title('Days Inactive by Resource Type')
        ax2.set_xlabel('')
        ax2.set_ylabel('Days Inactive')
        
        plt.tight_layout()
        return save_plot(fig, filename)
        
    except Exception as e:
        logger.error(f"Error creating idle resources plot: {e}")
        return None

def plot_cost_efficiency_score(scores, filename=None):
    """Generate a cost efficiency score visualization.
    
    Args:
        scores: Dictionary with component scores and composite score
        filename: Optional path to save the plot
        
    Returns:
        Path to saved file or base64 encoded string
    """
    try:
        # Extract scores
        component_scores = scores.get('detailed_scores', {})
        composite_score = scores.get('composite_score', 0)
        
        # Create radar chart for component scores
        fig = plt.figure(figsize=(12, 8))
        
        # Left subplot: Radar chart
        ax1 = plt.subplot2grid((1, 2), (0, 0), polar=True)
        
        # Component scores for radar chart
        categories = list(component_scores.keys())
        values = list(component_scores.values())
        
        # Clean categories for display
        categories = [cat.replace('_', ' ').title() for cat in categories]
        
        # Number of variables
        N = len(categories)
        
        # Angle for each category
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Values for radar chart
        values += values[:1]  # Close the loop
        
        # Draw the polygon
        ax1.plot(angles, values, linewidth=2, linestyle='solid')
        ax1.fill(angles, values, alpha=0.4)
        
        # Add labels
        plt.xticks(angles[:-1], categories, size=10)
        ax1.set_yticklabels([])
        
        # Draw axis lines for each angle and label
        ax1.set_rlabel_position(180)
        ax1.set_ylim(0, 2)
        ax1.set_rticks([0.5, 1, 1.5, 2])  # Less radial ticks
        ax1.set_yticklabels(['0.5', '1.0', '1.5', '2.0'], color='grey', size=8)
        
        # Add title
        ax1.set_title('Component Scores', size=15)
        
        # Right subplot: Gauge chart for composite score
        ax2 = plt.subplot2grid((1, 2), (0, 1))
        
        # Create gauge chart
        gauge_min, gauge_max = 0, 2
        gauge_range = gauge_max - gauge_min
        
        # Determine color based on score
        if composite_score < 0.6:
            color = '#e74c3c'  # red - poor
            label = 'Poor'
        elif composite_score < 1.0:
            color = '#f39c12'  # orange - below average
            label = 'Below Average'
        elif composite_score < 1.4:
            color = '#f1c40f'  # yellow - average
            label = 'Average'
        elif composite_score < 1.8:
            color = '#2ecc71'  # green - good
            label = 'Good'
        else:
            color = '#27ae60'  # dark green - excellent
            label = 'Excellent'
        
        # Draw gauge
        segments = 5
        theta = np.linspace(np.pi*0.75, np.pi*2.25, 100)
        r = 1.0
        
        # Background segments
        segment_colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
        segment_boundaries = [0, 0.6, 1.0, 1.4, 1.8, 2.0]
        
        for i in range(len(segment_boundaries)-1):
            start = (segment_boundaries[i] - gauge_min) / gauge_range
            end = (segment_boundaries[i+1] - gauge_min) / gauge_range
            start_angle = np.pi * 0.75 + start * np.pi * 1.5
            end_angle = np.pi * 0.75 + end * np.pi * 1.5
            segment_theta = np.linspace(start_angle, end_angle, 30)
            ax2.plot(segment_theta, [r] * len(segment_theta), linewidth=20, color=segment_colors[i], alpha=0.3)
        
        # Draw needle based on composite score
        needle_angle = np.pi * 0.75 + (composite_score - gauge_min) / gauge_range * np.pi * 1.5
        ax2.plot([0, np.cos(needle_angle)], [0, np.sin(needle_angle)], 'k-', linewidth=2)
        
        # Add a dot at the needle base
        ax2.plot(0, 0, 'ko', markersize=10)
        
        # Add score text
        ax2.text(0, -0.2, f"{composite_score:.2f} / 2.00", horizontalalignment='center', 
                 verticalalignment='center', fontsize=24, fontweight='bold', color=color)
        ax2.text(0, -0.35, label, horizontalalignment='center', 
                 verticalalignment='center', fontsize=18, color=color)
        
        # Add score interpretation
        interpretation = scores.get('interpretation', '')
        ax2.text(0, -0.6, interpretation, horizontalalignment='center',
                 verticalalignment='center', fontsize=12, wrap=True)
        
        # Remove axes
        ax2.set_aspect('equal')
        ax2.axis('off')
        
        plt.tight_layout()
        return save_plot(fig, filename)
        
    except Exception as e:
        logger.error(f"Error creating cost efficiency score plot: {e}")
        return None

def plot_sustainability_metrics(report, filename=None):
    """Generate sustainability metrics visualization.
    
    Args:
        report: Dictionary with sustainability report data
        filename: Optional path to save the plot
        
    Returns:
        Path to saved file or base64 encoded string
    """
    try:
        # Extract data from report
        summary = report.get('summary', {})
        regions = report.get('sustainable_regions', [])
        
        fig = plt.figure(figsize=(14, 8))
        
        # Left subplot: Sustainability score gauge
        ax1 = plt.subplot2grid((2, 2), (0, 0))
        
        # Create gauge for sustainability score
        score = summary.get('sustainability_score', 50)
        
        # Determine color based on score
        if score < 30:
            color = '#e74c3c'  # red - poor
            label = 'Poor'
        elif score < 50:
            color = '#f39c12'  # orange - below average
            label = 'Below Average'
        elif score < 70:
            color = '#f1c40f'  # yellow - average
            label = 'Average'
        elif score < 90:
            color = '#2ecc71'  # green - good
            label = 'Good'
        else:
            color = '#27ae60'  # dark green - excellent
            label = 'Excellent'
        
        # Draw sustainability score gauge
        gauge_min, gauge_max = 0, 100
        
        # Background segments
        segment_colors = ['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60']
        segment_boundaries = [0, 30, 50, 70, 90, 100]
        
        for i in range(len(segment_boundaries)-1):
            ax1.barh(0, 
                    segment_boundaries[i+1] - segment_boundaries[i], 
                    left=segment_boundaries[i], 
                    height=0.5, 
                    color=segment_colors[i], 
                    alpha=0.3)
        
        # Add score marker
        ax1.barh(0, 2, left=score-1, height=0.5, color=color)
        
        # Add score text
        ax1.text(50, -0.5, f"Sustainability Score: {score}/100", 
                horizontalalignment='center', fontsize=14, fontweight='bold')
        ax1.text(50, -0.8, label, horizontalalignment='center', fontsize=12, color=color)
        
        # Remove axes and set limits
        ax1.set_xlim(0, 100)
        ax1.set_ylim(-1, 1)
        ax1.set_yticks([])
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.set_title('Sustainability Score', fontsize=14)
        
        # Right subplot: Carbon emissions
        ax2 = plt.subplot2grid((2, 2), (0, 1))
        
        # Extract data
        carbon = summary.get('estimated_carbon_emissions_kg', 0)
        power = summary.get('estimated_power_usage_kwh', 0)
        
        # Create bar chart
        metrics = ['Carbon Emissions\n(kg CO2)', 'Power Usage\n(kWh)']
        values = [carbon, power]
        
        ax2.bar(metrics, values, color=['#3498db', '#9b59b6'])
        
        # Add value labels on top of bars
        for i, v in enumerate(values):
            ax2.text(i, v + (max(values) * 0.02), f"{v:,.0f}", 
                    horizontalalignment='center', fontsize=12)
        
        ax2.set_ylabel('Amount')
        ax2.set_title('Environmental Impact', fontsize=14)
        
        # Bottom subplot: Sustainable regions
        ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
        
        if regions:
            # Convert regions list to DataFrame
            region_df = pd.DataFrame(regions)
            
            # Sort by carbon intensity
            region_df = region_df.sort_values('carbon_intensity')
            
            # Plot horizontal bar chart
            colors = []
            for rating in region_df['sustainability_rating']:
                if rating.lower() == 'high':
                    colors.append('#27ae60')
                elif rating.lower() == 'medium':
                    colors.append('#f1c40f')
                else:
                    colors.append('#e74c3c')
            
            bars = ax3.barh(region_df['region'] + ' (' + region_df['provider'] + ')', 
                          region_df['carbon_intensity'], color=colors)
            
            # Add labels
            ax3.set_xlabel('Carbon Intensity (kg CO2/kWh)')
            ax3.set_title('Carbon Intensity by Region', fontsize=14)
            
            # Add value labels to bars
            for bar in bars:
                width = bar.get_width()
                ax3.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                        f"{width:.3f}", va='center')
        else:
            ax3.text(0.5, 0.5, "No region data available", 
                    horizontalalignment='center', verticalalignment='center')
            ax3.set_title('Carbon Intensity by Region', fontsize=14)
            ax3.axis('off')
        
        plt.tight_layout()
        return save_plot(fig, filename)
        
    except Exception as e:
        logger.error(f"Error creating sustainability metrics plot: {e}")
        return None 