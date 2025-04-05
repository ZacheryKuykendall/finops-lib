import pandas as pd
from azure.identity import AzureCliCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryDefinition, QueryTimePeriod, QueryDataset, QueryAggregation, QueryGrouping
from datetime import datetime, timedelta
import numpy as np
from .base import CloudCostProvider
from .auth_utils import try_azure_auth
import logging
import json
import os

logger = logging.getLogger(__name__)

class AzureCostProvider(CloudCostProvider):
    def __init__(self, subscription_id=None, test_mode=True):
        super().__init__(test_mode=True)  # Force test mode
        self.subscription_id = subscription_id
        self.test_mode = True  # Always use test mode for now
        self.logger = logger
        if not test_mode:
            try:
                if not try_azure_auth():
                    logger.warning("Could not authenticate with Azure, falling back to test mode")
                    self.test_mode = True
                else:
                    self.credential = AzureCliCredential()
                    self.client = CostManagementClient(self.credential, self.subscription_id)
                    self.scope = f"/subscriptions/{subscription_id}"
            except Exception as e:
                logger.warning(f"Azure initialization failed: {e}, falling back to test mode")
                self.test_mode = True

    def _generate_test_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate realistic test data for Azure costs"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        services = ['Virtual Machines', 'Storage', 'SQL Database', 'App Service', 'Kubernetes Service']
        regions = ['eastus', 'westus2', 'centralus']
        resource_groups = ['prod-rg', 'dev-rg', 'staging-rg']
        
        data = []
        for date in dates:
            for service in services:
                # Generate realistic cost data with some randomness
                base_cost = {
                    'Virtual Machines': 100,
                    'Storage': 50,
                    'SQL Database': 200,
                    'App Service': 75,
                    'Kubernetes Service': 150
                }.get(service, 100)
                
                # Add some daily variation
                cost = base_cost * (1 + np.random.uniform(-0.2, 0.2))
                
                data.append({
                    'timestamp': date.strftime('%Y-%m-%d'),
                    'service': service,
                    'cost': round(cost, 2),
                    'currency': 'USD',
                    'region': np.random.choice(regions),
                    'resource_group': np.random.choice(resource_groups),
                    'utilization': round(np.random.uniform(0.6, 0.95), 2),
                    'output': round(np.random.uniform(100, 1000), 2),
                    'discount': round(np.random.uniform(0, 0.25), 2),
                    'tags': {
                        'environment': np.random.choice(['production', 'development', 'staging']),
                        'team': np.random.choice(['platform', 'data', 'web']),
                        'project': f'project-{np.random.randint(1,4)}'
                    }
                })
        
        return pd.DataFrame(data)

    def get_cost_data(self, start_date: str, end_date: str, resource_id: str = None, tags: dict = None) -> pd.DataFrame:
        if self.test_mode:
            logger.info("Using test data for Azure costs")
            return self._generate_test_data(start_date, end_date)
            
        try:
            # Define the query parameters with extended dimensions
            query_definition = QueryDefinition(
                type="ActualCost",
                timeframe="Custom",
                time_period=QueryTimePeriod(
                    from_property=datetime.strptime(start_date, "%Y-%m-%d"),
                    to=datetime.strptime(end_date, "%Y-%m-%d")
                ),
                dataset=QueryDataset(
                    granularity="Daily",
                    aggregation={
                        "totalCost": QueryAggregation(
                            name="Cost",
                            function="Sum"
                        ),
                        "usageQuantity": QueryAggregation(
                            name="UsageQuantity",
                            function="Sum"
                        )
                    },
                    grouping=[
                        QueryGrouping(
                            type="Dimension",
                            name="ServiceName"
                        ),
                        QueryGrouping(
                            type="Dimension",
                            name="ResourceLocation"
                        ),
                        QueryGrouping(
                            type="Dimension",
                            name="ResourceGroup"
                        ),
                        QueryGrouping(
                            type="Dimension",
                            name="MeterCategory"
                        ),
                        QueryGrouping(
                            type="TagKey",
                            name="Environment"
                        )
                    ]
                )
            )

            # Add resource filter if resource_id is provided
            filters = []
            if resource_id:
                filters.append({
                    "dimensions": {
                        "name": "ResourceId",
                        "operator": "In",
                        "values": [resource_id]
                    }
                })

            # Add tag-based filters if tags are provided
            if tags:
                for key, value in tags.items():
                    filters.append({
                        "tags": {
                            "name": key,
                            "operator": "In",
                            "values": [value]
                        }
                    })

            if filters:
                query_definition.dataset.filter = {
                    "and": filters
                }

            # Query cost data
            response = self.client.query.usage(scope=self.scope, parameters=query_definition)

            # Process the response into a DataFrame
            data = []
            for row in response.rows:
                entry = {
                    "timestamp": row[0],          # Date
                    "service": row[2],            # ServiceName
                    "cost": float(row[1]),        # Cost
                    "currency": "USD",            # Currency
                    "region": row[3],             # ResourceLocation
                    "resource_group": row[4],     # ResourceGroup
                    "meter_category": row[5],     # MeterCategory
                    "usage_quantity": float(row[6]), # UsageQuantity
                    "tags": {
                        "environment": row[7]     # Environment tag
                    }
                }
                # Add utilization and discount data from test mode since we can't get real data
                if self.test_mode:
                    entry.update({
                        "utilization": 0.8,
                        "output": float(row[6]),
                        "discount": 0.0
                    })
                else:
                    # In production, these would come from Azure Monitor metrics
                    entry.update({
                        "utilization": 0.8,  # Default utilization
                        "output": float(row[6]),  # Using usage quantity as output
                        "discount": 0.0  # Default discount
                    })
                data.append(entry)

            return pd.DataFrame(data)
        except Exception as e:
            logger.error("Azure cost retrieval failed: %s", e)
            if not self.test_mode:
                raise
            logger.info("Falling back to test data")
            return self._generate_test_data(start_date, end_date)

    def get_budget_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Get budget data for the subscription."""
        if self.test_mode:
            # Generate test budget data
            return pd.DataFrame([
                {
                    'name': 'Engineering Team',
                    'amount': 10000.0,
                    'timeGrain': 'Monthly',
                    'startDate': start_date,
                    'endDate': end_date,
                    'currentSpend': 7500.0,
                    'forecastSpend': 9500.0
                },
                {
                    'name': 'DevOps Team',
                    'amount': 5000.0,
                    'timeGrain': 'Monthly',
                    'startDate': start_date,
                    'endDate': end_date,
                    'currentSpend': 3200.0,
                    'forecastSpend': 4800.0
                }
            ])

        try:
            budgets = self.client.budgets.list(scope=self.scope)
            budget_data = []
            for budget in budgets:
                budget_data.append({
                    "name": budget.name,
                    "amount": budget.amount,
                    "timeGrain": budget.time_grain,
                    "startDate": budget.time_period.start_date,
                    "endDate": budget.time_period.end_date,
                    "currentSpend": budget.current_spend.amount if budget.current_spend else 0,
                    "forecastSpend": budget.forecast_spend.amount if budget.forecast_spend else 0
                })
            return pd.DataFrame(budget_data)
        except Exception as e:
            logger.error(f"Failed to get budget data: {e}")
            return pd.DataFrame()

    def get_resource_data(self, start_date, end_date, include_activity=False):
        """Get resource data including activity metrics.
        
        Args:
            start_date: Start date for cost data
            end_date: End date for cost data
            include_activity: Whether to include activity data
            
        Returns:
            DataFrame containing resource data
        """
        self.logger.info(f"Getting resource data from {start_date} to {end_date}")
        
        if self.test_mode:
            self.logger.info("Using test data for Azure resource data")
            # Generate sample data with resource information
            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta
            
            # Create sample resources
            services = ['Virtual Machines', 'Storage', 'SQL Database', 'App Service', 'Functions']
            regions = ['eastus', 'westus2', 'northeurope', 'southeastasia']
            
            # Generate random number of resources (10-30)
            num_resources = np.random.randint(10, 30)
            
            data = {
                'resource_id': [f'azure-resource-{i}' for i in range(1, num_resources + 1)],
                'resource_type': np.random.choice(services, num_resources),
                'provider': 'Azure',
                'region': np.random.choice(regions, num_resources),
                'monthly_cost': np.round(np.random.uniform(10, 500, num_resources), 2),
            }
            
            if include_activity:
                # Generate last activity dates (some recent, some old)
                current_date = datetime.now()
                data['last_activity_date'] = [
                    (current_date - timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d')
                    for _ in range(num_resources)
                ]
            
            df = pd.DataFrame(data)
            return df
        
        # In real implementation, would call Azure API here
        # Placeholder for real implementation
        self.logger.warning("Real Azure resource data implementation not available")
        return pd.DataFrame()
