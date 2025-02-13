"""Multi-cloud FinOps Python library"""

__version__ = "1.0.0"

from .base import CloudCostProvider
from .aws import AWSCostProvider
from .azure import AzureCostProvider
from .gcp import GCPCostProvider
from .reporting import get_report
from .anomaly import detect_anomalies
from .forecast import forecast_costs
