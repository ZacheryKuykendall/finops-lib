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

    def get_test_data(self, start_date: str, end_date: str, cloud_name: str, resource_id: str = None) -> pd.DataFrame:
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

        regions = {
            "AWS": ["us-east-1", "us-west-2", "eu-west-1"],
            "Azure": ["East US", "West Europe", "Southeast Asia"],
            "GCP": ["us-central1", "europe-west1", "asia-east1"]
        }

        data = []
        for date in dates:
            # Generate 3-5 service entries per day
            for _ in range(random.randint(3, 5)):
                service = random.choice(services.get(cloud_name, ["Generic"]))
                region = random.choice(regions.get(cloud_name, ["Global"]))
                utilization = random.uniform(0, 1)  # Utilization as a percentage
                output = random.uniform(100, 1000)  # Random output value
                discount = random.uniform(0, 0.2) * 100  # Random discount percentage
                entry = {
                    "timestamp": date,
                    "service": f"{cloud_name}-{service}",
                    "cost": round(random.uniform(10, 1000), 2),
                    "currency": "USD",
                    "tags": {
                        "environment": random.choice(["prod", "dev", "test"]),
                        "team": random.choice(["platform", "data", "web"]),
                        "project": f"project-{random.randint(1,3)}"
                    },
                    "resource_id": f"resource-{random.randint(1, 100)}",
                    "region": region,
                    "utilization": utilization,
                    "output": output,
                    "discount": discount
                }
                data.append(entry)

        # Filter data by resource_id if provided
        if resource_id:
            data = [entry for entry in data if entry.get("resource_id") == resource_id]

        return pd.DataFrame(data)
