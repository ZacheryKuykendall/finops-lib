"""
Dashboard module for creating interactive FinOps dashboards.
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def create_dashboard_app(server):
    """
    Create a Dash application with interactive visualizations.
    
    Args:
        server: Flask server object to integrate with
        
    Returns:
        dash.Dash: Configured Dash application
    """
    # Create Dash app
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dashboard/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )
    
    # Layout
    app.layout = html.Div([
        dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("FinOps Interactive Dashboard", className="display-4 my-4"),
                    html.P("Interactive visualizations for cloud cost management", className="lead")
                ])
            ]),
            
            # Filters
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Filters", className="card-title"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Date Range:"),
                                    dcc.DatePickerRange(
                                        id='date-range',
                                        start_date=(datetime.now() - timedelta(days=30)).date(),
                                        end_date=datetime.now().date(),
                                        display_format='YYYY-MM-DD'
                                    )
                                ]),
                                dbc.Col([
                                    html.Label("Cloud Provider:"),
                                    dbc.Checklist(
                                        id='provider-filter',
                                        options=[
                                            {"label": "AWS", "value": "AWS"},
                                            {"label": "Azure", "value": "Azure"},
                                            {"label": "GCP", "value": "GCP"}
                                        ],
                                        value=["AWS", "Azure", "GCP"],
                                        inline=True
                                    )
                                ])
                            ])
                        ])
                    ], className="mb-4")
                ])
            ]),
            
            # Main dashboard
            dbc.Row([
                # Cost overview
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Cost Overview"),
                        dbc.CardBody([
                            dcc.Graph(id="cost-overview-chart")
                        ])
                    ], className="mb-4")
                ], md=6),
                
                # Metrics
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Key Metrics"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id="total-cost-metric", className="metric-box")
                                ]),
                                dbc.Col([
                                    html.Div(id="efficiency-score-metric", className="metric-box")
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id="waste-metric", className="metric-box")
                                ]),
                                dbc.Col([
                                    html.Div(id="sustainability-metric", className="metric-box")
                                ])
                            ])
                        ])
                    ], className="mb-4")
                ], md=6)
            ]),
            
            # Detailed analysis
            dbc.Tabs([
                # Resource utilization tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Resource Utilization"),
                                dbc.CardBody([
                                    dcc.Graph(id="utilization-chart")
                                ])
                            ])
                        ], md=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Utilization Distribution"),
                                dbc.CardBody([
                                    dcc.Graph(id="utilization-distribution")
                                ])
                            ])
                        ], md=6)
                    ], className="mb-4")
                ], label="Resource Utilization"),
                
                # Idle resources tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Idle Resources by Type"),
                                dbc.CardBody([
                                    dcc.Graph(id="idle-resources-chart")
                                ])
                            ])
                        ], md=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Days Inactive Distribution"),
                                dbc.CardBody([
                                    dcc.Graph(id="inactive-days-distribution")
                                ])
                            ])
                        ], md=6)
                    ], className="mb-4")
                ], label="Idle Resources"),
                
                # Cost efficiency tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Efficiency Radar"),
                                dbc.CardBody([
                                    dcc.Graph(id="efficiency-radar")
                                ])
                            ])
                        ], md=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Efficiency Score"),
                                dbc.CardBody([
                                    dcc.Graph(id="efficiency-gauge")
                                ])
                            ])
                        ], md=6)
                    ], className="mb-4")
                ], label="Cost Efficiency"),
                
                # Sustainability tab
                dbc.Tab([
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Carbon Emissions"),
                                dbc.CardBody([
                                    dcc.Graph(id="carbon-emissions-chart")
                                ])
                            ])
                        ], md=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Sustainable Regions"),
                                dbc.CardBody([
                                    dcc.Graph(id="sustainable-regions-chart")
                                ])
                            ])
                        ], md=6)
                    ], className="mb-4")
                ], label="Sustainability")
            ], className="mb-4")
        ], fluid=True)
    ])
    
    # Register callbacks
    _register_callbacks(app)
    
    return app

def _register_callbacks(app):
    """Register all callbacks for the dashboard."""
    
    @app.callback(
        Output("cost-overview-chart", "figure"),
        [Input("date-range", "start_date"),
         Input("date-range", "end_date"),
         Input("provider-filter", "value")]
    )
    def update_cost_overview(start_date, end_date, providers):
        """Update the cost overview chart."""
        # Generate sample data for demonstration
        dates = pd.date_range(start=start_date, end=end_date)
        data = []
        
        for provider in providers:
            for date in dates:
                if provider == "AWS":
                    cost = np.random.uniform(100, 150)
                elif provider == "Azure":
                    cost = np.random.uniform(80, 120)
                else:  # GCP
                    cost = np.random.uniform(60, 90)
                    
                data.append({
                    "date": date,
                    "provider": provider,
                    "cost": cost
                })
        
        df = pd.DataFrame(data)
        
        # Create figure
        fig = px.bar(
            df, 
            x="date", 
            y="cost", 
            color="provider",
            barmode="group",
            title="Daily Cloud Costs by Provider",
            labels={"date": "Date", "cost": "Cost ($)", "provider": "Cloud Provider"}
        )
        
        # Customize layout
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        return fig
    
    @app.callback(
        [Output("total-cost-metric", "children"),
         Output("efficiency-score-metric", "children"),
         Output("waste-metric", "children"),
         Output("sustainability-metric", "children")],
        [Input("date-range", "start_date"),
         Input("date-range", "end_date"),
         Input("provider-filter", "value")]
    )
    def update_metrics(start_date, end_date, providers):
        """Update the dashboard metrics."""
        # Generate sample metrics
        # In a real implementation, you would fetch this data from your backend
        total_cost = np.random.uniform(5000, 10000)
        efficiency_score = np.random.uniform(1.2, 1.8)
        waste_percentage = np.random.uniform(10, 30)
        sustainability_score = np.random.uniform(60, 90)
        
        # Create metric cards
        total_cost_card = html.Div([
            html.H5("Total Cost", className="metric-title"),
            html.H3(f"${total_cost:.2f}", className="metric-value"),
            html.P(f"For period {start_date} to {end_date}", className="metric-subtitle")
        ])
        
        # Efficiency score color based on value
        if efficiency_score < 0.6:
            efficiency_color = "danger"
            rating = "Poor"
        elif efficiency_score < 1.0:
            efficiency_color = "warning"
            rating = "Below Average"
        elif efficiency_score < 1.4:
            efficiency_color = "info"
            rating = "Average"
        elif efficiency_score < 1.8:
            efficiency_color = "success"
            rating = "Good"
        else:
            efficiency_color = "success"
            rating = "Excellent"
            
        efficiency_card = html.Div([
            html.H5("Efficiency Score", className="metric-title"),
            html.H3([
                f"{efficiency_score:.2f}",
                html.Span(f" / 2.00", style={"font-size": "0.7em", "color": "#999"})
            ], className=f"text-{efficiency_color}"),
            html.P(rating, className="metric-subtitle")
        ])
        
        # Waste metric
        waste_card = html.Div([
            html.H5("Waste", className="metric-title"),
            html.H3(f"{waste_percentage:.1f}%", 
                   className="text-danger" if waste_percentage > 20 else "text-warning"),
            html.P(f"Opportunity: ${waste_percentage * total_cost / 100:.2f}", className="metric-subtitle")
        ])
        
        # Sustainability metric
        if sustainability_score < 30:
            sustainability_color = "danger"
            sustainability_rating = "Poor"
        elif sustainability_score < 50:
            sustainability_color = "warning"
            sustainability_rating = "Fair"
        elif sustainability_score < 70:
            sustainability_color = "info"
            sustainability_rating = "Good"
        else:
            sustainability_color = "success"
            sustainability_rating = "Excellent"
            
        sustainability_card = html.Div([
            html.H5("Sustainability", className="metric-title"),
            html.H3(f"{sustainability_score:.0f}/100", className=f"text-{sustainability_color}"),
            html.P(sustainability_rating, className="metric-subtitle")
        ])
        
        return total_cost_card, efficiency_card, waste_card, sustainability_card
    
    @app.callback(
        [Output("utilization-chart", "figure"),
         Output("utilization-distribution", "figure")],
        [Input("date-range", "start_date"),
         Input("date-range", "end_date"),
         Input("provider-filter", "value")]
    )
    def update_utilization_charts(start_date, end_date, providers):
        """Update utilization charts."""
        # Generate sample data for demonstration
        services = ["EC2", "S3", "RDS", "Lambda", "App Service", "Storage", "Databases", 
                    "Compute Engine", "Cloud Storage", "BigQuery"]
        data = []
        
        for service in services:
            utilization = np.random.uniform(0.3, 0.9)
            provider = "AWS" if service in ["EC2", "S3", "RDS", "Lambda"] else \
                      "Azure" if service in ["App Service", "Storage", "Databases"] else "GCP"
                
            if provider in providers:
                data.append({
                    "service": service,
                    "utilization": utilization,
                    "provider": provider,
                    "cost": np.random.uniform(100, 500)
                })
        
        df = pd.DataFrame(data)
        
        # Utilization by service chart
        fig1 = px.bar(
            df.sort_values("utilization"), 
            y="service", 
            x="utilization",
            color="provider",
            labels={"service": "Service", "utilization": "Utilization", "provider": "Cloud Provider"},
            orientation='h',
            text_auto='.0%'
        )
        
        # Add threshold line
        threshold = 0.5
        fig1.add_vline(x=threshold, line_dash="dash", line_color="red", 
                      annotation_text="Threshold (50%)", annotation_position="top right")
        
        fig1.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(tickformat=".0%")
        )
        
        # Distribution chart
        fig2 = px.histogram(
            df, 
            x="utilization",
            color="provider",
            nbins=20,
            labels={"utilization": "Utilization", "count": "Resource Count", "provider": "Cloud Provider"},
            opacity=0.7
        )
        
        # Add threshold line
        fig2.add_vline(x=threshold, line_dash="dash", line_color="red")
        
        # Calculate percentage below threshold
        below_threshold = (df["utilization"] < threshold).mean() * 100
        fig2.add_annotation(
            x=threshold/2,
            y=fig2.layout.yaxis.range[1] * 0.9 if hasattr(fig2.layout.yaxis, 'range') else 10,
            text=f"{below_threshold:.1f}% resources<br>below threshold",
            showarrow=False,
            font=dict(color="red")
        )
        
        fig2.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(tickformat=".0%"),
            bargap=0.1
        )
        
        return fig1, fig2
    
    # Additional callbacks for other tabs would be defined similarly
    
    # Example for idle resources tab
    @app.callback(
        [Output("idle-resources-chart", "figure"),
         Output("inactive-days-distribution", "figure")],
        [Input("date-range", "start_date"),
         Input("date-range", "end_date"),
         Input("provider-filter", "value")]
    )
    def update_idle_resources_charts(start_date, end_date, providers):
        """Update idle resources charts."""
        # Generate sample data
        resource_types = ["VM", "Storage", "Database", "Container", "Network"]
        data = []
        
        for _ in range(40):
            resource_type = np.random.choice(resource_types)
            provider = np.random.choice(providers)
            days_inactive = np.random.randint(0, 30)
            
            data.append({
                "resource_id": f"resource-{_}",
                "resource_type": resource_type,
                "provider": provider,
                "days_inactive": days_inactive,
                "monthly_cost": np.random.uniform(10, 200)
            })
        
        df = pd.DataFrame(data)
        
        # Idle resources by type
        idle_df = df[df["days_inactive"] >= 7]  # Consider resources idle if inactive for 7+ days
        
        if idle_df.empty:
            # Create empty figures with messages if no idle resources
            fig1 = go.Figure()
            fig1.add_annotation(
                text="No idle resources found",
                showarrow=False,
                font=dict(size=16)
            )
            
            fig2 = go.Figure()
            fig2.add_annotation(
                text="No idle resources found",
                showarrow=False,
                font=dict(size=16)
            )
        else:
            # Group by resource type
            idle_by_type = idle_df.groupby("resource_type").agg(
                count=("resource_id", "count"),
                total_cost=("monthly_cost", "sum")
            ).reset_index()
            
            fig1 = px.pie(
                idle_by_type,
                values="total_cost",
                names="resource_type",
                title="Idle Resource Cost by Type",
                hole=0.4,
                labels={"resource_type": "Resource Type", "total_cost": "Monthly Cost ($)"}
            )
            
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            
            # Days inactive distribution
            fig2 = px.box(
                idle_df,
                x="resource_type",
                y="days_inactive",
                color="provider",
                labels={"resource_type": "Resource Type", "days_inactive": "Days Inactive", "provider": "Cloud Provider"},
                points="all"
            )
            
            # Add threshold line
            fig2.add_hline(y=7, line_dash="dash", line_color="red",
                          annotation_text="Idle Threshold (7 days)", annotation_position="right")
            
            fig2.update_layout(
                margin=dict(l=20, r=20, t=20, b=20)
            )
        
        return fig1, fig2 