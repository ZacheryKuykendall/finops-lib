"""
Azure Cost Management provider implementation
"""

import pandas as pd
import numpy as np
from azure.identity import AzureCliCredential, DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryDefinition, QueryTimePeriod, QueryDataset, QueryAggregation, QueryGrouping, QueryFilter, QueryResult
from datetime import datetime, timedelta
import logging
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class AzureCostProvider:
    """Azure Cost Management provider for retrieving and analyzing cost data."""
    
    def __init__(self, subscription_ids=None, test_mode=True):
        self.test_mode = test_mode
        self.subscription_ids = subscription_ids if isinstance(subscription_ids, list) else [subscription_ids] if subscription_ids else []
        self.clients = {}
        
        if not test_mode and self.subscription_ids:
            try:
                # Try Azure CLI credential first, then fall back to default credential chain
                try:
                    self.credential = AzureCliCredential()
                except Exception as e:
                    logger.warning(f"Failed to get CLI credential: {e}, trying default credential")
                    self.credential = DefaultAzureCredential()

                # Initialize clients for each subscription
                for sub_id in self.subscription_ids:
                    if sub_id:  # Skip empty/None subscription IDs
                        try:
                            client = CostManagementClient(self.credential, sub_id)
                            scope = f"/subscriptions/{sub_id}"
                            
                            # Test the connection
                            client.query.usage(
                                scope=scope,
                                parameters=QueryDefinition(
                                    type="ActualCost",
                                    timeframe="TheLastMonth",
                                    dataset=QueryDataset(granularity="None")
                                )
                            )
                            self.clients[sub_id] = {"client": client, "scope": scope}
                            logger.info(f"Successfully connected to Azure Cost Management API for subscription {sub_id}")
                        except Exception as e:
                            logger.warning(f"Failed to initialize client for subscription {sub_id}: {e}")
                
                if not self.clients:
                    logger.warning("No valid subscription clients initialized, falling back to test mode")
                    self.test_mode = True
                    
            except Exception as e:
                logger.warning(f"Azure initialization failed: {e}, using test mode")
                self.test_mode = True
        else:
            logger.info("Using test mode for Azure Cost Management")
            self.test_mode = True

        self._load_test_data()

    def _load_test_data(self):
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        
        # Load cost management data
        with open(os.path.join(test_data_dir, 'cost_management_sample.json'), 'r') as f:
            self.cost_data = json.load(f)
        
        # Load budget data
        with open(os.path.join(test_data_dir, 'budget_sample.json'), 'r') as f:
            self.budget_data = json.load(f)

    def get_cost_data(self, start_date=None, end_date=None):
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # Convert test data to DataFrame
        columns = [col['name'] for col in self.cost_data['properties']['columns']]
        df = pd.DataFrame(self.cost_data['properties']['rows'], columns=columns)
        
        # Filter by date range
        df['UsageDateTime'] = pd.to_datetime(df['UsageDateTime'])
        df = df[(df['UsageDateTime'] >= start_date) & (df['UsageDateTime'] <= end_date)]
        
        # Filter by subscriptions
        df = df[df['ResourceId'].str.contains('|'.join(self.subscription_ids))]
        
        return df

    def get_budgets(self):
        return self.budget_data['value']

    def get_optimization_recommendations(self) -> list:
        """Get cost optimization recommendations."""
        if self.test_mode:
            return [
                "Consider purchasing reserved instances for consistently running VMs",
                "Right-size underutilized virtual machines",
                "Delete unattached disks and unused resources",
                "Implement auto-shutdown for non-production resources"
            ]

        try:
            # In a real implementation, this would use the Azure Advisor API
            # For now, return static recommendations
            return [
                "Consider purchasing reserved instances for consistently running VMs",
                "Right-size underutilized virtual machines",
                "Delete unattached disks and unused resources",
                "Implement auto-shutdown for non-production resources"
            ]
        except Exception as e:
            logger.error(f"Failed to get optimization recommendations: {e}")
            return []

    def _get_test_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate test data for development and testing."""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        services = ['Virtual Machines', 'Storage', 'App Service', 'SQL Database', 'Cosmos DB']
        regions = ['East US', 'West Europe', 'Southeast Asia']
        resource_groups = ['prod-rg', 'dev-rg', 'test-rg']
        subscriptions = [
            {'id': 'sub-1', 'name': 'Production'},
            {'id': 'sub-2', 'name': 'Development'}
        ]
        
        data = []
        for date in dates:
            for service in services:
                for sub in subscriptions:
                    data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'service': service,
                        'cost': round(float(np.random.uniform(100, 1000)), 2),
                        'region': np.random.choice(regions),
                        'resource_group': np.random.choice(resource_groups),
                        'usage_quantity': round(float(np.random.uniform(1, 100)), 2),
                        'utilization': round(float(np.random.uniform(0.5, 0.95)), 2),
                        'is_reserved_instance': np.random.choice([True, False], p=[0.3, 0.7]),
                        'subscription_id': sub['id'],
                        'subscription_name': sub['name']
                    })
        
        return pd.DataFrame(data) 