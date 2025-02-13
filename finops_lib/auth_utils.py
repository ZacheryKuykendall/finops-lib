import subprocess
import logging
import json
import os
import click

logger = logging.getLogger(__name__)

def prompt_cloud_selection():
    """Prompt user to select which cloud to authenticate with"""
    click.echo("\nSelect cloud provider to authenticate:")
    click.echo("1) Azure")
    click.echo("2) AWS")
    click.echo("3) GCP")
    
    choice = click.prompt("Enter your choice (1-3)", type=click.Choice(['1', '2', '3']))
    
    if choice == '1':
        return try_azure_auth()
    elif choice == '2':
        return try_aws_auth()
    elif choice == '3':
        return try_gcp_auth()

def try_aws_auth():
    """Try to ensure AWS credentials are available"""
    try:
        import boto3
        boto3.client('sts').get_caller_identity()
        return True
    except Exception:
        click.echo("No AWS credentials found. Would you like to configure AWS CLI?")
        if click.confirm('Proceed with AWS configuration?'):
            try:
                subprocess.run(['aws', 'configure'], check=True)
                return True
            except subprocess.CalledProcessError:
                logger.warning("AWS CLI login failed")
                return False
        return False

def try_azure_auth():
    """Try to ensure Azure credentials are available"""
    try:
        from azure.identity import AzureCliCredential
        credential = AzureCliCredential()
        credential.get_token("https://management.azure.com/.default")
        return True
    except Exception:
        click.echo("No Azure credentials found. Would you like to login to Azure?")
        if click.confirm('Proceed with Azure login?'):
            try:
                subprocess.run(['az', 'login'], check=True)
                return True
            except subprocess.CalledProcessError:
                logger.warning("Azure CLI login failed")
                return False
        return False

def try_gcp_auth():
    """Try to ensure GCP credentials are available"""
    try:
        from google.oauth2 import service_account
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            service_account.Credentials.from_service_account_file(
                os.environ['GOOGLE_APPLICATION_CREDENTIALS']
            )
            return True
    except Exception:
        click.echo("No GCP credentials found. Would you like to login to GCP?")
        if click.confirm('Proceed with GCP login?'):
            try:
                subprocess.run(['gcloud', 'auth', 'application-default', 'login'], check=True)
                return True
            except subprocess.CalledProcessError:
                logger.warning("GCP CLI login failed")
                return False
        return False
