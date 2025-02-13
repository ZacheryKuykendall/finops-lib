import pandas as pd
from google.cloud import bigquery
from .base import CloudCostProvider
from .auth_utils import try_gcp_auth
import logging

logger = logging.getLogger(__name__)

class GCPCostProvider(CloudCostProvider):
    def __init__(self, project_id, test_mode=False):
        super().__init__(test_mode)
        self.project_id = project_id
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
