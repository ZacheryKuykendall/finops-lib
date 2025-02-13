import pandas as pd
from azure.identity import AzureCliCredential
from azure.mgmt.costmanagement import CostManagementClient
from .base import CloudCostProvider
from .auth_utils import try_azure_auth
import logging

logger = logging.getLogger(__name__)

class AzureCostProvider(CloudCostProvider):
    def __init__(self, subscription_id, test_mode=False):
        super().__init__(test_mode)
        self.subscription_id = subscription_id
        if not test_mode:
            try:
                if not try_azure_auth():
                    logger.warning("Could not authenticate with Azure, falling back to test mode")
                    self.test_mode = True
                else:
                    self.credential = AzureCliCredential()
                    self.client = CostManagementClient(self.credential, self.subscription_id)
            except Exception as e:
                logger.warning(f"Azure initialization failed: {e}, falling back to test mode")
                self.test_mode = True

    def get_cost_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        if self.test_mode:
            logger.info("Using test data for Azure costs")
            return self.get_test_data(start_date, end_date, "Azure")
            
        try:
            # Real Azure cost management API call would go here
            data = [{"timestamp": start_date, "service": "Azure-RealService", 
                    "cost": 200.0, "currency": "USD", "tags": {}}]
            return pd.DataFrame(data)
        except Exception as e:
            logger.error("Azure cost retrieval failed: %s", e)
            if not self.test_mode:
                raise
            logger.info("Falling back to test data")
            return self.get_test_data(start_date, end_date, "Azure")
