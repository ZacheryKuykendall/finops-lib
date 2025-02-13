import abc
import pandas as pd
from datetime import datetime, timedelta
import random

class CloudCostProvider(abc.ABC):
    """Abstract base class for cloud cost providers."""
    
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
    
    @abc.abstractmethod
    def get_cost_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch cost data between start and end dates"""
        pass

    def get_test_data(self, start_date: str, end_date: str, cloud_name: str) -> pd.DataFrame:
        """Generate realistic test data when credentials aren't available"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        dates = [(start + timedelta(days=x)).strftime("%Y-%m-%d") 
                for x in range((end-start).days + 1)]
        
        services = {
            "AWS": ["EC2", "S3", "RDS", "Lambda", "DynamoDB"],
            "Azure": ["VirtualMachines", "Storage", "SQLDatabase", "Functions", "CosmosDB"],
            "GCP": ["ComputeEngine", "Storage", "CloudSQL", "CloudFunctions", "BigQuery"]
        }

        data = []
        for date in dates:
            # Generate 3-5 service entries per day
            for _ in range(random.randint(3, 5)):
                service = random.choice(services.get(cloud_name, ["Generic"]))
                data.append({
                    "timestamp": date,
                    "service": f"{cloud_name}-{service}",
                    "cost": round(random.uniform(10, 1000), 2),
                    "currency": "USD",
                    "tags": {
                        "environment": random.choice(["prod", "dev", "test"]),
                        "team": random.choice(["platform", "data", "web"]),
                        "project": f"project-{random.randint(1,3)}"
                    }
                })
        
        return pd.DataFrame(data)
