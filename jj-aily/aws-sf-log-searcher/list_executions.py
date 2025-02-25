#!/usr/bin/env python3
import boto3
import datetime
import argparse
from typing import List, Dict
from datetime import timezone
import json

def get_state_machines(region: str = None) -> List[str]:
    """Get all state machine ARNs in the account"""
    sfn = boto3.client('stepfunctions', region_name=region)
    state_machines = []
    
    paginator = sfn.get_paginator('list_state_machines')
    for page in paginator.paginate():
        for machine in page['stateMachines']:
            state_machines.append(machine['stateMachineArn'])
            
    return state_machines

def get_executions(state_machine_arn: str, hours: int = 24, status: str = 'ALL', 
                   name_filter: str = None, key_filter: str = None, region: str = None) -> List[Dict]:
    """Get executions for a state machine within specified hours"""
    sfn = boto3.client('stepfunctions', region_name=region)
    executions = []
    
    # Calculate start time
    start_time = datetime.datetime.now(timezone.utc) - datetime.timedelta(hours=hours)
    
    paginator = sfn.get_paginator('list_executions')
    paginator_args = {'stateMachineArn': state_machine_arn}
    
    # Only add statusFilter if a specific status is requested
    if status != 'ALL':
        paginator_args['statusFilter'] = status
        
    for page in paginator.paginate(**paginator_args):
        for execution in page['executions']:
            if execution['startDate'] >= start_time:
                # Fetch execution input
                execution_details = sfn.describe_execution(
                    executionArn=execution['executionArn']
                )
                try:
                    input_data = json.loads(execution_details['input'])
                    
                    # Apply filters if specified
                    if name_filter is not None and input_data.get('name') != name_filter:
                        continue
                    if key_filter is not None and key_filter not in input_data.get('key', ''):
                        continue
                        
                    formatted_input = json.dumps(input_data, indent=4)
                except (json.JSONDecodeError, KeyError):
                    formatted_input = execution_details.get('input', 'No input available')
                    # Skip if filters are specified but we couldn't parse the input
                    if name_filter is not None or key_filter is not None:
                        continue

                executions.append({
                    'name': execution['name'],
                    'status': execution['status'],
                    'start_date': execution['startDate'].strftime('%Y-%m-%d %H:%M:%S'),
                    'state_machine_arn': state_machine_arn,
                    'input': formatted_input
                })
            else:
                # Since results are ordered by startDate descending, we can break early
                return executions
                
    return executions

def main():
    VALID_STATUSES = ['ALL', 'SUCCEEDED', 'TIMED_OUT', 'PENDING_REDRIVE', 'ABORTED', 'FAILED', 'RUNNING']
    
    parser = argparse.ArgumentParser(description='List AWS Step Functions executions in the last N hours')
    parser.add_argument('--hours', type=int, default=24, help='Number of hours to look back (default: 24)')
    parser.add_argument('--state-machine', type=str, help='Specific state machine ARN (optional)')
    parser.add_argument('--status', type=str, choices=VALID_STATUSES, default='ALL',
                      help='Filter by execution status (default: ALL)')
    parser.add_argument('--name', type=str, help='Filter by exact match of input name attribute')
    parser.add_argument('--key-contains', type=str, help='Filter by substring in input key attribute')
    parser.add_argument('--region', type=str, help='AWS region to use (defaults to configured region)')
    args = parser.parse_args()

    try:
        if args.state_machine:
            state_machines = [args.state_machine]
        else:
            state_machines = get_state_machines(region=args.region)

        print(f"\nFetching {args.status} executions from the last {args.hours} hours...")
        if args.name:
            print(f"Filtering for name = '{args.name}'")
        if args.key_contains:
            print(f"Filtering for key containing '{args.key_contains}'")
        if args.region:
            print(f"Using AWS region: {args.region}")
        
        for state_machine in state_machines:
            executions = get_executions(
                state_machine, 
                args.hours, 
                args.status,
                name_filter=args.name,
                key_filter=args.key_contains,
                region=args.region
            )
            
            if executions:
                print(f"\nState Machine: {state_machine}")
                print("-" * 80)
                
                for execution in executions:
                    print(f"Name: {execution['name']}")
                    print(f"Status: {execution['status']}")
                    print(f"Start Date: {execution['start_date']}")
                    print("Input:")
                    print(execution['input'])
                    print("-" * 40)

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == '__main__':
    exit(main()) 