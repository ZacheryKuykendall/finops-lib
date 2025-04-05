"""
Command-line interface for Azure FinOps CLI
"""

import argparse
from datetime import datetime, timedelta
import json
import os
from .web import start_web_interface, load_config
from .azure import AzureCostProvider
from .scoring import calculate_composite_score

def main():
    parser = argparse.ArgumentParser(description='Azure FinOps CLI - Cloud cost management tool')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Web interface command
    web_parser = subparsers.add_parser('web', help='Start the web interface')
    web_parser.add_argument('--port', type=int, default=5000, help='Port to run the web server on')

    # List subscriptions command
    list_subs_parser = subparsers.add_parser('list-subscriptions', help='List configured Azure subscriptions')

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate a cost report')
    report_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    report_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    report_parser.add_argument('--output', type=str, choices=['json', 'csv'], default='json',
                             help='Output format')
    report_parser.add_argument('--subscription-id', help='Filter by subscription ID')

    # Score command
    score_parser = subparsers.add_parser('score', help='Calculate efficiency score')
    score_parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    score_parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')
    score_parser.add_argument('--subscription-id', help='Filter by subscription ID')

    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Get optimization recommendations')
    optimize_parser.add_argument('--subscription-id', help='Filter by subscription ID')

    args = parser.parse_args()

    if args.command == 'web':
        config = load_config()
        if not config['azure_subscriptions']:
            print("Error: No Azure subscriptions configured. Please add subscriptions to config.json")
            return
        start_web_interface(port=args.port)

    elif args.command == 'list-subscriptions':
        config = load_config()
        if not config['azure_subscriptions']:
            print("No Azure subscriptions configured")
            return
        print("\nConfigured Azure Subscriptions:")
        print("-" * 50)
        for sub in config['azure_subscriptions']:
            print(f"Name: {sub['name']}")
            print(f"ID:   {sub['id']}")
            print("-" * 50)

    elif args.command == 'report':
        config = load_config()
        start_date = args.start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = args.end_date or datetime.now().strftime('%Y-%m-%d')
        
        # Get subscription IDs
        if args.subscription_id:
            subscription_ids = [args.subscription_id]
        else:
            subscription_ids = [sub['id'] for sub in config['azure_subscriptions']]
        
        if not subscription_ids:
            print("Error: No Azure subscriptions configured or specified")
            return
            
        provider = AzureCostProvider(subscription_ids=subscription_ids)
        costs = provider.get_cost_data(start_date, end_date)
        
        # Group by subscription
        costs_by_sub = costs.groupby(['subscription_name', 'service'])['cost'].sum().reset_index()
        
        if args.output == 'json':
            print(costs_by_sub.to_json(orient='records'))
        else:
            print(costs_by_sub.to_csv(index=False))

    elif args.command == 'score':
        config = load_config()
        start_date = args.start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = args.end_date or datetime.now().strftime('%Y-%m-%d')
        
        # Get subscription IDs
        if args.subscription_id:
            subscription_ids = [args.subscription_id]
        else:
            subscription_ids = [sub['id'] for sub in config['azure_subscriptions']]
        
        if not subscription_ids:
            print("Error: No Azure subscriptions configured or specified")
            return
            
        provider = AzureCostProvider(subscription_ids=subscription_ids)
        costs = provider.get_cost_data(start_date, end_date)
        
        # Calculate scores per subscription
        print("\nEfficiency Scores:")
        print("-" * 50)
        for sub_name in costs['subscription_name'].unique():
            sub_data = costs[costs['subscription_name'] == sub_name]
            score = calculate_composite_score(sub_data)
            print(f"\nSubscription: {sub_name}")
            print(f"Score: {score:.2f}")
        
        # Calculate overall score
        overall_score = calculate_composite_score(costs)
        print("\nOverall Score:", f"{overall_score:.2f}")

    elif args.command == 'optimize':
        config = load_config()
        
        # Get subscription IDs
        if args.subscription_id:
            subscription_ids = [args.subscription_id]
        else:
            subscription_ids = [sub['id'] for sub in config['azure_subscriptions']]
        
        if not subscription_ids:
            print("Error: No Azure subscriptions configured or specified")
            return
            
        provider = AzureCostProvider(subscription_ids=subscription_ids)
        recommendations = provider.get_optimization_recommendations()
        
        print("\nOptimization Recommendations:")
        print("-" * 50)
        for rec in recommendations:
            print(f"- {rec}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 