import argparse
import boto3
import requests


def describe_stack(client, stack_name):
    response = client.describe_stacks(
        StackName=stack_name
    )
    return response['Stacks']


def get_client(args):
    if args.region:
        if args.verbose:
            print(
                'Creating CloudFormation client in region %s' % args.region
            )
        return boto3.client('cloudformation', region_name=args.region)
    else:
        if args.verbose:
            print 'Creating CloudFormation client using AWS CLI Config'
        return boto3.client('cloudformation')


def get_stack(args):
    if args.stack_name:
        if args.verbose:
            print 'Stack Name to look up is %s' % args.stack_name
        return args.stack_name


def get_protocol(args):
    if args.protocol:
        if args.verbose:
            print (
                'Using %s protocol to construct url' % args.protocol
            )
        return args.protocol
    else:
        return 'http'


def main(args):
    client = get_client(args)
    stack = get_stack(args)
    protocol = get_protocol(args)
    stack = next(iter(describe_stack(client, stack)))
    config_prefix = 'config/dns'

    outputs = dict([(output['OutputKey'], output['OutputValue'])
                    for output in stack['Outputs']
                    if output['OutputKey'] in ['consulUrl', 'dnsAddress']])

    if args.protocol:
        data = (protocol + '://' + outputs['dnsAddress'])
    else:
        data = (outputs['dnsAddress'])
    endpoint = 'http://%s:8500/v1/kv/%s/%s' % (outputs['consulUrl'],
                                               config_prefix, args.service)

    if args.verbose:
        print('Content to post is %s' % data)
        print('Will post to %s' % endpoint)

    requests.put(endpoint, data=data)

    if args.verbose:
        print('Key:Value has been posted')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', help='print debug information')
    parser.add_argument(
        '--region', help='use a custom region instead of the cli configuration'
    )
    parser.add_argument(
        '--protocol', help='select a protocol to use (http or https)'
    )
    parser.add_argument(
        '--service', help='select service where value is required (task etc)'
    )
    parser.add_argument('--stack-name', help='enter a stack name for lookup')
    args = parser.parse_args()
    main(args)
