import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from click.testing import CliRunner
from finops_lib.cli import (
    sustainability_report,
    resource_utilization,
    idle_resources,
    cost_efficiency_score
)

class TestNewCommands(unittest.TestCase):
    """Test cases for the newly added FinOps CLI commands."""

    def setUp(self):
        self.runner = CliRunner()
        # Test date range
        self.start_date = "2023-01-01"
        self.end_date = "2023-01-31"
        
        # Sample DataFrame for cost data
        self.sample_df = pd.DataFrame({
            'timestamp': pd.date_range(start=self.start_date, end=self.end_date, freq='D'),
            'service': ['EC2', 'S3', 'RDS'] * 10 + ['CloudSQL'],
            'cost': np.random.uniform(10, 200, 31),
            'utilization': np.random.uniform(0.3, 0.9, 31),
            'region': ['us-east-1', 'us-west-2'] * 15 + ['eu-west-1'],
            'provider': ['AWS'] * 20 + ['GCP'] * 11
        })

    @patch('finops_lib.cli.AWSCostProvider')
    @patch('finops_lib.cli.AzureCostProvider')
    @patch('finops_lib.cli.GCPCostProvider')
    @patch('finops_lib.cli.generate_sustainability_report')
    def test_sustainability_report(self, mock_gen_report, mock_gcp, mock_azure, mock_aws):
        """Test the sustainability_report command."""
        # Set up mock returns
        mock_aws_instance = mock_aws.return_value
        mock_azure_instance = mock_azure.return_value
        mock_gcp_instance = mock_gcp.return_value
        
        mock_aws_instance.get_cost_data.return_value = self.sample_df.copy()
        mock_azure_instance.get_cost_data.return_value = self.sample_df.copy()
        mock_gcp_instance.get_cost_data.return_value = self.sample_df.copy()
        
        # Mock sustainability report 
        mock_gen_report.return_value = {
            "summary": {
                "sustainability_score": 75,
                "rating": "Good", 
                "estimated_carbon_emissions_kg": 5000,
                "estimated_power_usage_kwh": 15000
            },
            "recommendations": [
                {"priority": "High", "recommendation": "Test recommendation", "estimated_impact": "Medium"}
            ],
            "sustainable_regions": [
                {"provider": "AWS", "region": "us-west-2", "carbon_intensity": 0.1, "sustainability_rating": "High"}
            ],
            "details": {
                "carbon_intensity_by_region": {
                    "us-east-1": {"carbon_intensity": 0.2, "cost_percentage": 35}
                }
            }
        }
        
        # Run the command
        result = self.runner.invoke(sustainability_report, [
            '--start-date', self.start_date,
            '--end-date', self.end_date,
            '--test'
        ])
        
        # Assert command execution was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Generating sustainability report", result.output)
        self.assertIn("Sustainability Score:", result.output)
        
        # Assert mocks were called correctly
        mock_aws.assert_called_once_with(test_mode=True)
        mock_azure.assert_called_once_with(subscription_id="test", test_mode=True)
        mock_gcp.assert_called_once_with(project_id="test", test_mode=True)
        mock_aws_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
        mock_azure_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
        mock_gcp_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
        mock_gen_report.assert_called_once()
    
    @patch('finops_lib.cli.AWSCostProvider')
    @patch('finops_lib.cli.AzureCostProvider')
    @patch('finops_lib.cli.GCPCostProvider')
    def test_resource_utilization(self, mock_gcp, mock_azure, mock_aws):
        """Test the resource_utilization command."""
        # Set up mock returns
        mock_aws_instance = mock_aws.return_value
        mock_azure_instance = mock_azure.return_value
        mock_gcp_instance = mock_gcp.return_value
        
        df = self.sample_df.copy()
        mock_aws_instance.get_cost_data.return_value = df
        mock_azure_instance.get_cost_data.return_value = df
        mock_gcp_instance.get_cost_data.return_value = df
        
        # Run the command
        result = self.runner.invoke(resource_utilization, [
            '--start-date', self.start_date,
            '--end-date', self.end_date,
            '--test',
            '--threshold', '0.5'
        ])
        
        # Assert command execution was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Analyzing resource utilization", result.output)
        self.assertIn("Resource Utilization Summary", result.output)
        
        # Assert mocks were called correctly
        mock_aws.assert_called_once_with(test_mode=True)
        mock_azure.assert_called_once_with(subscription_id="test", test_mode=True)
        mock_gcp.assert_called_once_with(project_id="test", test_mode=True)
        mock_aws_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
        mock_azure_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
        mock_gcp_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
    
    @patch('finops_lib.cli.AWSCostProvider')
    @patch('finops_lib.cli.AzureCostProvider')
    @patch('finops_lib.cli.GCPCostProvider')
    def test_idle_resources(self, mock_gcp, mock_azure, mock_aws):
        """Test the idle_resources command."""
        # Set up mock returns
        mock_aws_instance = mock_aws.return_value
        mock_azure_instance = mock_azure.return_value
        mock_gcp_instance = mock_gcp.return_value
        
        # Create sample resource data
        resource_data = pd.DataFrame({
            'resource_id': [f'resource-{i}' for i in range(1, 21)],
            'resource_type': np.random.choice(['VM', 'Storage', 'Database'], 20),
            'provider': np.random.choice(['AWS', 'Azure', 'GCP'], 20),
            'region': np.random.choice(['us-east-1', 'us-west-2'], 20),
            'monthly_cost': np.random.uniform(10, 500, 20),
            'last_activity_date': [(pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 30)))
                                   for _ in range(20)]
        })
        
        mock_aws_instance.get_resource_data.return_value = resource_data[resource_data['provider'] == 'AWS']
        mock_azure_instance.get_resource_data.return_value = resource_data[resource_data['provider'] == 'Azure']
        mock_gcp_instance.get_resource_data.return_value = resource_data[resource_data['provider'] == 'GCP']
        
        # Run the command
        result = self.runner.invoke(idle_resources, [
            '--start-date', self.start_date,
            '--end-date', self.end_date,
            '--test',
            '--inactive-threshold', '7'
        ])
        
        # Assert command execution was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Detecting idle resources", result.output)
        
        # Assert mocks were called correctly
        mock_aws.assert_called_once_with(test_mode=True)
        mock_azure.assert_called_once_with(subscription_id="test", test_mode=True)
        mock_gcp.assert_called_once_with(project_id="test", test_mode=True)
        mock_aws_instance.get_resource_data.assert_called_once_with(self.start_date, self.end_date, include_activity=True)
        mock_azure_instance.get_resource_data.assert_called_once_with(self.start_date, self.end_date, include_activity=True)
        mock_gcp_instance.get_resource_data.assert_called_once_with(self.start_date, self.end_date, include_activity=True)
    
    @patch('finops_lib.cli.AWSCostProvider')
    @patch('finops_lib.cli.AzureCostProvider')
    @patch('finops_lib.cli.GCPCostProvider')
    @patch('finops_lib.scoring.calculate_resource_utilization_score')
    @patch('finops_lib.scoring.calculate_waste_percentage_score')
    @patch('finops_lib.scoring.calculate_discount_coverage_score')
    @patch('finops_lib.scoring.calculate_cost_allocation_score')
    @patch('finops_lib.scoring.calculate_forecast_accuracy_score')
    @patch('finops_lib.scoring.calculate_composite_score')
    def test_cost_efficiency_score(self, mock_composite, mock_forecast, mock_allocation, 
                                 mock_discount, mock_waste, mock_utilization,
                                 mock_gcp, mock_azure, mock_aws):
        """Test the cost_efficiency_score command."""
        # Set up mock returns
        mock_aws_instance = mock_aws.return_value
        mock_azure_instance = mock_azure.return_value
        mock_gcp_instance = mock_gcp.return_value
        
        mock_aws_instance.get_cost_data.return_value = self.sample_df.copy()
        mock_azure_instance.get_cost_data.return_value = self.sample_df.copy()
        mock_gcp_instance.get_cost_data.return_value = self.sample_df.copy()
        
        # Mock scoring functions
        mock_utilization.return_value = 1.5
        mock_waste.return_value = 1.2
        mock_discount.return_value = 1.4
        mock_allocation.return_value = 1.3
        mock_forecast.return_value = 1.6
        mock_composite.return_value = 1.4
        
        # Run the command
        result = self.runner.invoke(cost_efficiency_score, [
            '--start-date', self.start_date,
            '--end-date', self.end_date,
            '--test'
        ])
        
        # Assert command execution was successful
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Generating comprehensive cost efficiency score", result.output)
        self.assertIn("Cost Efficiency Score Report", result.output)
        
        # Assert mocks were called correctly
        mock_aws.assert_called_once_with(test_mode=True)
        mock_azure.assert_called_once_with(subscription_id="test", test_mode=True)
        mock_gcp.assert_called_once_with(project_id="test", test_mode=True)
        mock_aws_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
        mock_azure_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
        mock_gcp_instance.get_cost_data.assert_called_once_with(self.start_date, self.end_date)
        mock_composite.assert_called_once()

if __name__ == '__main__':
    unittest.main() 