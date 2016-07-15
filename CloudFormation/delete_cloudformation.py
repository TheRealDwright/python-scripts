#!/usr/bin/python

import argparse
import boto3
import time


def describe_stack(client, stack_name):
    response = client.describe_stacks(
        StackName=stack_name
    )
    return response['Stacks']


def main(args):
    if args.region:
        if args.verbose:
            print(
                'Creating CloudFormation client in region %s' % args.region
            )
        client = boto3.client('cloudformation', region_name=args.region)
    else:
        if args.verbose:
            print 'Creating CloudFormation client'
        client = boto3.client('cloudformation')
    if args.stack_name:
        if args.verbose:
            print 'Stack Name to delete is %s' % args.stack_name
        stack_name = args.stack_name

    stacks = describe_stack(client, stack_name)

    for stack in stacks:
        stack_id = stack['StackId']
        status = stack["StackStatus"]
        if status in ['CREATE_COMPLETE', 'UPDATE_COMPLETE',
                      'ROLLBACK_COMPLETE', 'CREATE_FAILED']:
            delete_response = client.delete_stack(
                StackName=stack_name
            )
            is_deleted = False
            current_time = 0
            timeout = args.timeout
            sleep_time = 10
            while not is_deleted:
                current_status = describe_stack(
                    client, stack_id
                )[0]["StackStatus"]
                is_deleted = current_status == 'DELETE_COMPLETE'
                if not is_deleted:
                    print(
                        "Stack is currently deleting status is: %s"
                        ". Deletion has been running for %s seconds"
                        % (current_status, current_time)
                    )
                    current_time += sleep_time
                    time.sleep(sleep_time)
        else:
            print("Stack %s is in a state of " + status +
                  " and is not viable for deletion. Script will now exit."
                  ) % stack_name
            exit(1)
    print("Stack: %s has been deleted." % args.stack_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', help='print debug information')
    parser.add_argument(
        '--region', help='use a custom region instead of the cli configuration'
    )
    parser.add_argument('--stack-name', help='enter a stack name for deletion')
    parser.add_argument(
        '--timeout', help='time in seconds before timing out'
    )
    args = parser.parse_args()
    main(args)
