import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.resource('ec2')


def lambda_handler(event, context):
    filters = [{
            'Name': 'tag:AutoOn',
            'Values': ['True']
        },
        {
            'Name': 'instance-state-name',
            'Values': ['stopped']
        }
    ]

    instances = ec2.instances.filter(Filters=filters)

    StoppedInstances = [instance.id for instance in instances]

    if len(RunningInstances) > 0:
        poweringOn = ec2.instances.filter(InstanceIds=StoppedInstances).start()
        print poweringOn
    else:
        print "Nothing to see here, move along please"
