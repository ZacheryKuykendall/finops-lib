"""
Azure FinOps CLI - A tool for Azure cloud cost management and optimization
"""

from .azure import AzureCostProvider
from .web import start_web_interface
from .scoring import calculate_composite_score

__version__ = "0.1.0" 