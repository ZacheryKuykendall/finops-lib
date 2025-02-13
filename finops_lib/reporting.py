import pandas as pd
from .aws import AWSCostProvider
from .azure import AzureCostProvider
from .gcp import GCPCostProvider
import logging
from .auth_utils import prompt_cloud_selection
import click

logger = logging.getLogger(__name__)

def get_report(start_date: str, end_date: str, output_format="markdown", test_mode=False) -> str:
    """
    Retrieve cost data from all providers and output an aggregated report.
    In test_mode=True, uses dummy data when credentials aren't available.
    """
    try:
        # Handle authentication when not in test mode
        if not test_mode:
            click.echo("Checking cloud authentication...")
            auth_attempted = prompt_cloud_selection()
            if not auth_attempted:
                click.echo("No cloud credentials available. Would you like to:")
                choice = click.prompt(
                    "1) Try authentication again\n2) Continue in test mode",
                    type=click.Choice(['1', '2'])
                )
                if choice == '1':
                    auth_attempted = prompt_cloud_selection()
                if not auth_attempted:
                    logger.warning("No cloud authentication available, falling back to test mode")
                    test_mode = True

        # Initialize providers
        aws = AWSCostProvider(test_mode=test_mode)
        azure = AzureCostProvider(subscription_id="test", test_mode=test_mode)
        gcp = GCPCostProvider(project_id="test", test_mode=test_mode)

        # Collect data from each provider
        df_list = []
        for provider, name in [(aws, "AWS"), (azure, "Azure"), (gcp, "GCP")]:
            try:
                df = provider.get_cost_data(start_date, end_date)
                df_list.append(df)
            except Exception as e:
                logger.warning(f"Failed to get data from {name}: {e}")
                if test_mode:
                    df_list.append(provider.get_test_data(start_date, end_date, name))

        if not df_list:
            raise Exception("No data available from any provider")

        # Combine and format results
        df = pd.concat(df_list)
        if output_format == "csv":
            return df.to_csv(index=False)
        elif output_format == "json":
            return df.to_json(orient="records")
        else:
            return df.to_markdown(index=False)
    except Exception as e:
        logger.error("Failed to generate report: %s", e)
        raise
