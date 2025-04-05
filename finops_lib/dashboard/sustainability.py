"""
Sustainability visualizations module for the FinOps dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_carbon_emissions_chart(df, group_by='month', providers=None):
    """
    Create a chart showing carbon emissions over time.
    
    Args:
        df: DataFrame containing emissions data
        group_by: Time interval for grouping ('day', 'week', 'month')
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Carbon emissions visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No emissions data available for the selected period",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Group by time interval
    if group_by == 'week':
        df['date_group'] = df['date'].dt.to_period('W').apply(lambda x: x.start_time)
    elif group_by == 'month':
        df['date_group'] = df['date'].dt.to_period('M').apply(lambda x: x.start_time)
    else:  # default to day
        df['date_group'] = df['date']
    
    # Aggregate emissions
    grouped_df = df.groupby(['date_group', 'provider']).agg(
        total_emissions=('emissions_kg', 'sum')
    ).reset_index()
    
    # Create figure
    fig = px.area(
        grouped_df, 
        x='date_group', 
        y='total_emissions', 
        color='provider',
        title=f"Carbon Emissions by {group_by.capitalize()}",
        labels={
            'date_group': 'Date', 
            'total_emissions': 'Carbon Emissions (kg CO₂e)', 
            'provider': 'Cloud Provider'
        }
    )
    
    # Add total line
    total_by_date = grouped_df.groupby('date_group').agg(
        total_emissions=('total_emissions', 'sum')
    ).reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=total_by_date['date_group'],
            y=total_by_date['total_emissions'],
            name='Total',
            line=dict(color='black', width=2)
        )
    )
    
    # Customize layout
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def create_sustainable_regions_chart(df, providers=None):
    """
    Create a chart showing carbon intensity by region.
    
    Args:
        df: DataFrame containing region carbon intensity data
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Sustainable regions visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No region data available for sustainability analysis",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    
    # Sort by carbon intensity
    df = df.sort_values('carbon_intensity', ascending=True)
    
    # Categorize regions
    intensity_threshold_low = 100  # g CO2/kWh
    intensity_threshold_med = 300  # g CO2/kWh
    
    df['category'] = 'High Carbon'
    df.loc[df['carbon_intensity'] < intensity_threshold_med, 'category'] = 'Medium Carbon'
    df.loc[df['carbon_intensity'] < intensity_threshold_low, 'category'] = 'Low Carbon'
    
    # Create color map
    color_map = {
        'Low Carbon': 'green',
        'Medium Carbon': 'orange',
        'High Carbon': 'red'
    }
    
    # Create figure
    fig = px.bar(
        df,
        x='region',
        y='carbon_intensity',
        color='category',
        color_discrete_map=color_map,
        labels={
            'region': 'Region',
            'carbon_intensity': 'Carbon Intensity (g CO₂e/kWh)',
            'category': 'Category',
            'provider': 'Cloud Provider'
        },
        title='Carbon Intensity by Cloud Region',
        hover_data=['provider']
    )
    
    # Add threshold lines
    fig.add_shape(
        type='line',
        line=dict(color='orange', width=2, dash='dash'),
        y0=intensity_threshold_low,
        y1=intensity_threshold_low,
        x0=-0.5,
        x1=len(df) - 0.5,
        xref='x',
        yref='y'
    )
    
    fig.add_shape(
        type='line',
        line=dict(color='red', width=2, dash='dash'),
        y0=intensity_threshold_med,
        y1=intensity_threshold_med,
        x0=-0.5,
        x1=len(df) - 0.5,
        xref='x',
        yref='y'
    )
    
    # Add annotations for thresholds
    fig.add_annotation(
        x=len(df) - 1,
        y=intensity_threshold_low,
        text='Low Carbon Threshold',
        showarrow=False,
        yshift=10,
        font=dict(color='green')
    )
    
    fig.add_annotation(
        x=len(df) - 1,
        y=intensity_threshold_med,
        text='Medium Carbon Threshold',
        showarrow=False,
        yshift=10,
        font=dict(color='red')
    )
    
    # Customize layout
    fig.update_layout(
        xaxis={'categoryorder': 'total ascending'},
        margin=dict(l=40, r=40, t=60, b=100),
        xaxis_tickangle=-45
    )
    
    return fig

def create_efficiency_vs_sustainability_chart(df, providers=None):
    """
    Create a scatter plot comparing resource efficiency and sustainability.
    
    Args:
        df: DataFrame containing resource data with efficiency and sustainability metrics
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Efficiency vs sustainability visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No resource data available for analysis",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    
    # Create figure
    fig = px.scatter(
        df,
        x='utilization',
        y='sustainability_score',
        color='provider',
        size='monthly_cost',
        hover_name='resource_id',
        labels={
            'utilization': 'Resource Utilization',
            'sustainability_score': 'Sustainability Score (0-100)',
            'provider': 'Cloud Provider',
            'monthly_cost': 'Monthly Cost ($)'
        },
        title='Resource Efficiency vs Sustainability'
    )
    
    # Add quadrant lines
    fig.add_vline(
        x=0.5,
        line_dash='dash',
        line_color='gray'
    )
    
    fig.add_hline(
        y=50,
        line_dash='dash',
        line_color='gray'
    )
    
    # Add quadrant labels
    fig.add_annotation(
        x=0.25,
        y=25,
        text="Low Efficiency<br>Low Sustainability",
        showarrow=False,
        font=dict(color='red')
    )
    
    fig.add_annotation(
        x=0.25,
        y=75,
        text="Low Efficiency<br>High Sustainability",
        showarrow=False,
        font=dict(color='orange')
    )
    
    fig.add_annotation(
        x=0.75,
        y=25,
        text="High Efficiency<br>Low Sustainability",
        showarrow=False,
        font=dict(color='orange')
    )
    
    fig.add_annotation(
        x=0.75,
        y=75,
        text="High Efficiency<br>High Sustainability",
        showarrow=False,
        font=dict(color='green')
    )
    
    # Customize layout
    fig.update_layout(
        xaxis=dict(range=[0, 1], tickformat='.0%'),
        yaxis=dict(range=[0, 100]),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def create_carbon_savings_opportunity_chart(df, providers=None):
    """
    Create a chart showing carbon savings opportunities.
    
    Args:
        df: DataFrame containing carbon savings opportunities
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Carbon savings visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for carbon savings analysis",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    
    # Sort by potential savings
    df = df.sort_values('potential_carbon_savings', ascending=False)
    
    # Create figure
    fig = px.bar(
        df,
        x='recommendation',
        y='potential_carbon_savings',
        color='provider',
        labels={
            'recommendation': 'Recommendation',
            'potential_carbon_savings': 'Potential Carbon Savings (kg CO₂e/month)',
            'provider': 'Cloud Provider'
        },
        title='Carbon Savings Opportunities'
    )
    
    # Customize layout
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        margin=dict(l=40, r=40, t=60, b=80),
        xaxis_tickangle=-45
    )
    
    return fig

def create_sustainability_score_gauge(score):
    """
    Create a gauge chart showing the sustainability score.
    
    Args:
        score: Sustainability score (0-100)
    
    Returns:
        plotly.graph_objects.Figure: Sustainability score gauge
    """
    # Define zones for the gauge
    zones = [
        {'name': 'Poor', 'min': 0, 'max': 30, 'color': 'red'},
        {'name': 'Fair', 'min': 30, 'max': 50, 'color': 'orange'},
        {'name': 'Good', 'min': 50, 'max': 70, 'color': 'yellow'},
        {'name': 'Very Good', 'min': 70, 'max': 90, 'color': 'lightgreen'},
        {'name': 'Excellent', 'min': 90, 'max': 100, 'color': 'green'}
    ]
    
    # Find current zone
    current_zone = next((zone for zone in zones if zone['min'] <= score <= zone['max']), zones[0])
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': 'Sustainability Score'},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickvals': [0, 25, 50, 75, 100]},
            'bar': {'color': current_zone['color']},
            'steps': [
                {'range': [zone['min'], zone['max']], 'color': zone['color']} for zone in zones
            ],
            'threshold': {
                'line': {'color': 'black', 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    # Add rating text
    fig.add_annotation(
        x=0.5,
        y=0.25,
        text=f"Rating: {current_zone['name']}",
        showarrow=False,
        font=dict(size=16)
    )
    
    # Customize layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=60, b=40)
    )
    
    return fig 