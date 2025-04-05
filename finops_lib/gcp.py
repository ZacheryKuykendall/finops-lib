import pandas as pd
from google.cloud import bigquery
from .base import CloudCostProvider
from .auth_utils import try_gcp_auth
import logging
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GCPCostProvider(CloudCostProvider):
    def __init__(self, project_id, test_mode=False):
        super().__init__(test_mode)
        self.project_id = project_id
        self.logger = logger
        if not test_mode:
            try:
                if not try_gcp_auth():
                    logger.warning("Could not authenticate with GCP, falling back to test mode")
                    self.test_mode = True
                else:
                    self.client = bigquery.Client(project=project_id)
            except Exception as e:
                logger.warning(f"GCP initialization failed: {e}, falling back to test mode")
                self.test_mode = True

    def get_cost_data(self, start_date: str, end_date: str, resource_id: str = None) -> pd.DataFrame:
        if self.test_mode:
            logger.info("Using test data for GCP costs")
            return self.get_test_data(start_date, end_date, "GCP", resource_id)
            
        try:
            # Add resource filter if resource_id is provided
            query = f"""
            SELECT * FROM `project.dataset.table`
            WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
            """
            if resource_id:
                query += f" AND resource_id = '{resource_id}'"

            # Real BigQuery cost data query would go here
            data = [{"timestamp": start_date, "service": "GCP-RealService", 
                    "cost": 150.0, "currency": "USD", "tags": {}}]
            return pd.DataFrame(data)
        except Exception as e:
            logger.error("GCP cost retrieval failed: %s", e)
            if not self.test_mode:
                raise
            logger.info("Falling back to test data")
            return self.get_test_data(start_date, end_date, "GCP", resource_id)

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
            self.logger.info("Using test data for GCP resource data")
            # Generate sample data with resource information
            # Create sample resources
            services = ['Compute Engine', 'Cloud Storage', 'Cloud SQL', 'BigQuery', 'Cloud Functions']
            regions = ['us-central1', 'us-east1', 'europe-west1', 'asia-east1']
            
            # Generate random number of resources (10-30)
            num_resources = np.random.randint(10, 30)
            
            data = {
                'resource_id': [f'gcp-resource-{i}' for i in range(1, num_resources + 1)],
                'resource_type': np.random.choice(services, num_resources),
                'provider': 'GCP',
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
        
        # In real implementation, would call GCP API here
        # Placeholder for real implementation
        self.logger.warning("Real GCP resource data implementation not available")
        return pd.DataFrame()
