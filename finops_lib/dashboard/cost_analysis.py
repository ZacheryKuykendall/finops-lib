"""
Cost analysis visualizations module for the FinOps dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_cost_trend_chart(df, group_by='day', providers=None):
    """
    Create a chart showing cost trends over time.
    
    Args:
        df: DataFrame containing cost data with columns 'date', 'provider', 'cost'
        group_by: Time interval for grouping ('day', 'week', 'month')
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Cost trend visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No cost data available for the selected period",
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
    
    # Aggregate costs
    grouped_df = df.groupby(['date_group', 'provider']).agg(
        total_cost=('cost', 'sum')
    ).reset_index()
    
    # Create figure
    fig = px.line(
        grouped_df, 
        x='date_group', 
        y='total_cost', 
        color='provider',
        markers=True,
        title=f"Cost Trend by {group_by.capitalize()}",
        labels={'date_group': 'Date', 'total_cost': 'Cost ($)', 'provider': 'Cloud Provider'}
    )
    
    # Add total line
    total_by_date = grouped_df.groupby('date_group').agg(
        total_cost=('total_cost', 'sum')
    ).reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=total_by_date['date_group'],
            y=total_by_date['total_cost'],
            name='Total',
            line=dict(color='black', width=2, dash='dash')
        )
    )
    
    # Customize layout
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def create_cost_breakdown_chart(df, breakdown_by='service', providers=None):
    """
    Create a chart showing cost breakdown by a dimension.
    
    Args:
        df: DataFrame containing cost data
        breakdown_by: Dimension to break down by ('service', 'region', 'account')
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Cost breakdown visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No cost data available for the selected period",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    
    # Aggregate costs by the breakdown dimension
    grouped_df = df.groupby([breakdown_by, 'provider']).agg(
        total_cost=('cost', 'sum')
    ).reset_index()
    
    # Sort by cost descending
    grouped_df = grouped_df.sort_values('total_cost', ascending=False)
    
    # Get top categories
    top_categories = grouped_df.groupby(breakdown_by).agg(
        total_cost=('total_cost', 'sum')
    ).reset_index().sort_values('total_cost', ascending=False).head(10)[breakdown_by].tolist()
    
    # Filter for top categories
    grouped_df = grouped_df[grouped_df[breakdown_by].isin(top_categories)]
    
    # Create chart
    fig = px.bar(
        grouped_df,
        x=breakdown_by,
        y='total_cost',
        color='provider',
        title=f"Cost Breakdown by {breakdown_by.capitalize()}",
        labels={breakdown_by: breakdown_by.capitalize(), 'total_cost': 'Cost ($)', 'provider': 'Cloud Provider'}
    )
    
    # Customize layout
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=60)
    )
    
    return fig

def create_cost_forecast_chart(historical_df, forecast_days=30, providers=None):
    """
    Create a chart with historical costs and forecast.
    
    Args:
        historical_df: DataFrame containing historical cost data
        forecast_days: Number of days to forecast
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Forecast visualization
    """
    if historical_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No historical cost data available for forecasting",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers if specified
    if providers:
        historical_df = historical_df[historical_df['provider'].isin(providers)]
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(historical_df['date']):
        historical_df['date'] = pd.to_datetime(historical_df['date'])
    
    # Group by date and provider
    daily_costs = historical_df.groupby(['date', 'provider']).agg(
        cost=('cost', 'sum')
    ).reset_index()
    
    # Create figure
    fig = go.Figure()
    
    # Get list of providers
    all_providers = daily_costs['provider'].unique()
    
    for provider in all_providers:
        provider_data = daily_costs[daily_costs['provider'] == provider]
        
        # Add historical data
        fig.add_trace(
            go.Scatter(
                x=provider_data['date'],
                y=provider_data['cost'],
                name=f"{provider} (Actual)",
                mode='lines+markers',
                line=dict(width=2)
            )
        )
        
        # Simple linear forecast
        # In a real implementation, you would use a proper forecasting algorithm
        x = np.array((provider_data['date'] - provider_data['date'].min()).dt.days)
        y = provider_data['cost'].values
        
        # Fit linear model
        if len(x) > 1:  # Need at least 2 points for regression
            slope, intercept = np.polyfit(x, y, 1)
            
            # Generate forecast dates
            last_date = provider_data['date'].max()
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
            
            # Generate forecast values
            forecast_x = np.array([(date - provider_data['date'].min()).days for date in forecast_dates])
            forecast_y = slope * forecast_x + intercept
            
            # Add forecast data
            fig.add_trace(
                go.Scatter(
                    x=forecast_dates,
                    y=forecast_y,
                    name=f"{provider} (Forecast)",
                    mode='lines',
                    line=dict(dash='dash')
                )
            )
    
    # Add vertical line at current date
    fig.add_vline(
        x=historical_df['date'].max(),
        line_dash="dash",
        line_color="black",
        annotation_text="Today",
        annotation_position="top right"
    )
    
    # Customize layout
    fig.update_layout(
        title="Cost Forecast",
        xaxis_title="Date",
        yaxis_title="Cost ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def create_cost_anomaly_chart(df, providers=None, z_threshold=2.0):
    """
    Create a chart highlighting cost anomalies.
    
    Args:
        df: DataFrame containing cost data
        providers: List of cloud providers to include
        z_threshold: Z-score threshold for anomaly detection
    
    Returns:
        plotly.graph_objects.Figure: Anomaly visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No cost data available for anomaly detection",
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
    
    # Group by date
    daily_costs = df.groupby('date').agg(
        cost=('cost', 'sum')
    ).reset_index()
    
    # Calculate rolling mean and standard deviation
    window_size = min(7, len(daily_costs))  # Use 7 days window or available data
    if window_size > 2:  # Need at least 3 points for rolling window
        daily_costs['rolling_mean'] = daily_costs['cost'].rolling(window=window_size, center=False).mean()
        daily_costs['rolling_std'] = daily_costs['cost'].rolling(window=window_size, center=False).std()
        
        # Calculate z-scores
        daily_costs['z_score'] = (daily_costs['cost'] - daily_costs['rolling_mean']) / daily_costs['rolling_std']
        
        # Identify anomalies
        daily_costs['is_anomaly'] = abs(daily_costs['z_score']) > z_threshold
    else:
        # Not enough data for anomaly detection
        daily_costs['is_anomaly'] = False
    
    # Create figure
    fig = go.Figure()
    
    # Add normal cost line
    fig.add_trace(
        go.Scatter(
            x=daily_costs['date'],
            y=daily_costs['cost'],
            mode='lines+markers',
            name='Daily Cost',
            line=dict(color='blue')
        )
    )
    
    # Add anomalies
    anomalies = daily_costs[daily_costs['is_anomaly']]
    if not anomalies.empty:
        fig.add_trace(
            go.Scatter(
                x=anomalies['date'],
                y=anomalies['cost'],
                mode='markers',
                name='Anomalies',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='circle',
                    line=dict(
                        color='black',
                        width=2
                    )
                )
            )
        )
    
    # Customize layout
    fig.update_layout(
        title="Cost Anomaly Detection",
        xaxis_title="Date",
        yaxis_title="Cost ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def get_cost_summary_metrics(df, providers=None):
    """
    Calculate summary metrics from cost data.
    
    Args:
        df: DataFrame containing cost data
        providers: List of cloud providers to include
    
    Returns:
        dict: Summary metrics
    """
    if df.empty:
        return {
            "total_cost": 0,
            "avg_daily_cost": 0,
            "cost_trend": 0,
            "providers": {},
            "forecast": 0
        }
    
    # Filter by providers if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Calculate total cost
    total_cost = df['cost'].sum()
    
    # Calculate average daily cost
    days = (df['date'].max() - df['date'].min()).days + 1
    avg_daily_cost = total_cost / max(days, 1)
    
    # Calculate cost by provider
    provider_costs = df.groupby('provider').agg(
        cost=('cost', 'sum')
    ).reset_index().set_index('provider')['cost'].to_dict()
    
    # Calculate cost trend (% change over time)
    if days >= 14:  # Need at least two weeks of data
        half_point = df['date'].min() + (df['date'].max() - df['date'].min()) / 2
        first_half = df[df['date'] < half_point]
        second_half = df[df['date'] >= half_point]
        
        first_half_daily = first_half['cost'].sum() / max((half_point - df['date'].min()).days, 1)
        second_half_daily = second_half['cost'].sum() / max((df['date'].max() - half_point).days, 1)
        
        if first_half_daily > 0:
            cost_trend = (second_half_daily - first_half_daily) / first_half_daily
        else:
            cost_trend = 0
    else:
        cost_trend = 0
    
    # Simple forecast (30 days)
    forecast = total_cost * (30 / max(days, 1))
    
    return {
        "total_cost": total_cost,
        "avg_daily_cost": avg_daily_cost,
        "cost_trend": cost_trend,
        "providers": provider_costs,
        "forecast": forecast
    } 