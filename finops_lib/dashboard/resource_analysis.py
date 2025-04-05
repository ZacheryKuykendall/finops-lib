"""
Resource analysis visualizations module for the FinOps dashboard.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_utilization_heatmap(df, resource_types=None, providers=None):
    """
    Create a heatmap showing resource utilization across resource types.
    
    Args:
        df: DataFrame containing utilization data
        resource_types: List of resource types to include
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Utilization heatmap
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No utilization data available",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers and resource types if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    if resource_types:
        df = df[df['resource_type'].isin(resource_types)]
    
    # Group by resource type and provider
    grouped_df = df.groupby(['resource_type', 'provider']).agg(
        avg_utilization=('utilization', 'mean'),
        resource_count=('resource_id', 'count')
    ).reset_index()
    
    # Create figure
    fig = px.density_heatmap(
        grouped_df,
        x='provider',
        y='resource_type',
        z='avg_utilization',
        size='resource_count',
        color_continuous_scale='RdYlGn',
        labels={
            'provider': 'Cloud Provider',
            'resource_type': 'Resource Type',
            'avg_utilization': 'Average Utilization'
        },
        title='Resource Utilization Heatmap'
    )
    
    # Customize layout
    fig.update_layout(
        margin=dict(l=40, r=40, t=60, b=40),
        coloraxis_colorbar=dict(
            title='Utilization',
            tickformat='.0%'
        )
    )
    
    return fig

def create_utilization_trend_chart(df, resource_type=None, providers=None):
    """
    Create a chart showing utilization trends over time.
    
    Args:
        df: DataFrame containing utilization data over time
        resource_type: Resource type to filter for
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Utilization trend visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No utilization data available for trend analysis",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers and resource type if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    if resource_type:
        df = df[df['resource_type'] == resource_type]
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Group by date, resource type, and provider
    grouped_df = df.groupby(['date', 'resource_type', 'provider']).agg(
        avg_utilization=('utilization', 'mean')
    ).reset_index()
    
    # Create figure
    fig = px.line(
        grouped_df,
        x='date',
        y='avg_utilization',
        color='provider',
        facet_row='resource_type',
        markers=True,
        labels={
            'date': 'Date',
            'avg_utilization': 'Average Utilization',
            'provider': 'Cloud Provider',
            'resource_type': 'Resource Type'
        },
        title='Utilization Trend by Resource Type'
    )
    
    # Add threshold line
    threshold = 0.5  # 50% utilization
    for i in range(len(fig.data)):
        fig.add_shape(
            type='line',
            line=dict(dash='dash', color='red', width=1),
            y0=threshold,
            y1=threshold,
            xref=f'x{i+1}',
            yref=f'y{i+1}',
            x0=grouped_df['date'].min(),
            x1=grouped_df['date'].max()
        )
    
    # Customize layout
    fig.update_layout(
        margin=dict(l=40, r=40, t=60, b=40),
        yaxis=dict(tickformat='.0%')
    )
    
    # Update y-axis for all subplots
    for annotation in fig.layout.annotations:
        annotation.text = annotation.text.split('=')[1]
    
    for axis in fig.layout:
        if axis.startswith('yaxis'):
            fig.layout[axis].update(tickformat='.0%')
    
    return fig

def create_efficiency_radar_chart(scores_df):
    """
    Create a radar chart showing different efficiency scores.
    
    Args:
        scores_df: DataFrame containing efficiency scores
    
    Returns:
        plotly.graph_objects.Figure: Efficiency radar chart
    """
    if scores_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No efficiency scores available",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Create figure
    fig = go.Figure()
    
    categories = scores_df['metric'].tolist()
    values = scores_df['score'].tolist()
    
    # Add trace
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Efficiency Scores'
    ))
    
    # Add reference circle for target score
    target_score = 1.5  # Target score on 0-2 scale
    fig.add_trace(go.Scatterpolar(
        r=[target_score] * len(categories),
        theta=categories,
        fill=None,
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='Target Score'
    ))
    
    # Customize layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 2],
                tickvals=[0, 0.5, 1, 1.5, 2],
                ticktext=['0', '0.5', '1', '1.5', '2']
            )
        ),
        title='Efficiency Score Breakdown',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig

def create_efficiency_gauge_chart(overall_score):
    """
    Create a gauge chart showing the overall efficiency score.
    
    Args:
        overall_score: Overall efficiency score (0-2)
    
    Returns:
        plotly.graph_objects.Figure: Efficiency gauge chart
    """
    # Define zones for the gauge
    zones = [
        {'name': 'Poor', 'min': 0, 'max': 0.6, 'color': 'red'},
        {'name': 'Below Average', 'min': 0.6, 'max': 1.0, 'color': 'orange'},
        {'name': 'Average', 'min': 1.0, 'max': 1.4, 'color': 'yellow'},
        {'name': 'Good', 'min': 1.4, 'max': 1.8, 'color': 'lightgreen'},
        {'name': 'Excellent', 'min': 1.8, 'max': 2.0, 'color': 'green'}
    ]
    
    # Find current zone
    current_zone = next((zone for zone in zones if zone['min'] <= overall_score <= zone['max']), zones[0])
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=overall_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': 'Overall Efficiency Score'},
        delta={'reference': 1.4, 'increasing': {'color': 'green'}},
        gauge={
            'axis': {'range': [0, 2], 'tickwidth': 1, 'tickvals': [0, 0.5, 1, 1.5, 2]},
            'bar': {'color': current_zone['color']},
            'steps': [
                {'range': [zone['min'], zone['max']], 'color': zone['color']} for zone in zones
            ],
            'threshold': {
                'line': {'color': 'black', 'width': 4},
                'thickness': 0.75,
                'value': overall_score
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

def create_rightsizing_opportunity_chart(df, utilization_threshold=0.5, providers=None):
    """
    Create a chart showing rightsizing opportunities.
    
    Args:
        df: DataFrame containing resource data
        utilization_threshold: Threshold for identifying underutilized resources
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Rightsizing opportunity visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No resource data available for rightsizing analysis",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    
    # Identify underutilized resources
    df['underutilized'] = df['utilization'] < utilization_threshold
    
    # Group by resource type and calculate potential savings
    grouped_df = df[df['underutilized']].groupby(['resource_type', 'provider']).agg(
        resource_count=('resource_id', 'count'),
        avg_utilization=('utilization', 'mean'),
        total_cost=('monthly_cost', 'sum')
    ).reset_index()
    
    # Calculate potential savings (simplified)
    # In a real implementation, you would have more complex logic based on resource types
    grouped_df['savings_potential'] = grouped_df['total_cost'] * (1 - grouped_df['avg_utilization'])
    
    # Sort by savings potential
    grouped_df = grouped_df.sort_values('savings_potential', ascending=False)
    
    # Create figure
    fig = px.bar(
        grouped_df,
        x='resource_type',
        y='savings_potential',
        color='provider',
        text='resource_count',
        labels={
            'resource_type': 'Resource Type',
            'savings_potential': 'Potential Monthly Savings ($)',
            'provider': 'Cloud Provider',
            'resource_count': 'Resource Count'
        },
        title='Rightsizing Opportunities by Resource Type'
    )
    
    # Customize layout
    fig.update_traces(texttemplate='%{text} resources', textposition='outside')
    fig.update_layout(
        xaxis={'categoryorder': 'total descending'},
        margin=dict(l=40, r=40, t=60, b=60)
    )
    
    return fig

def create_idle_resources_chart(df, inactive_threshold_days=7, providers=None):
    """
    Create a chart showing idle resources.
    
    Args:
        df: DataFrame containing resource activity data
        inactive_threshold_days: Threshold in days for considering a resource idle
        providers: List of cloud providers to include
    
    Returns:
        plotly.graph_objects.Figure: Idle resources visualization
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No resource activity data available",
            showarrow=False,
            font=dict(size=16)
        )
        return fig
    
    # Filter by providers if specified
    if providers:
        df = df[df['provider'].isin(providers)]
    
    # Identify idle resources
    df['is_idle'] = df['days_inactive'] >= inactive_threshold_days
    
    # Group by resource type and calculate idle resource metrics
    idle_df = df[df['is_idle']].groupby(['resource_type', 'provider']).agg(
        resource_count=('resource_id', 'count'),
        avg_inactive_days=('days_inactive', 'mean'),
        total_cost=('monthly_cost', 'sum')
    ).reset_index()
    
    # Create figure
    fig = go.Figure()
    
    for provider in idle_df['provider'].unique():
        provider_df = idle_df[idle_df['provider'] == provider]
        
        fig.add_trace(go.Bar(
            x=provider_df['resource_type'],
            y=provider_df['total_cost'],
            name=provider,
            text=provider_df['resource_count'],
            customdata=np.stack((
                provider_df['avg_inactive_days'],
                provider_df['resource_count']
            ), axis=-1)
        ))
    
    # Customize layout
    fig.update_traces(
        texttemplate='%{text} resources',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>' +
                      'Provider: %{data.name}<br>' +
                      'Monthly Cost: $%{y:.2f}<br>' +
                      'Resource Count: %{customdata[1]}<br>' +
                      'Avg. Inactive Days: %{customdata[0]:.1f}<br>'
    )
    
    fig.update_layout(
        barmode='group',
        title='Idle Resources by Type',
        xaxis_title='Resource Type',
        yaxis_title='Monthly Cost ($)',
        legend_title='Cloud Provider',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig 