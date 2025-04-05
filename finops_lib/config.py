"""Configuration management module"""

import os
import json
import logging

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'azure_subscription_id': None,
            'aws_account_id': None,
            'gcp_project_id': None,
            'budgets': []
        } 