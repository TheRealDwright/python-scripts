import collections
import datetime
import boto3

ec = boto3.client('ec2')


def lambda_handler(event, context):

    reservations = ec.describe_instances(
        Filters=[
            {'Name': 'tag:AutoBackup', 'Values': ['True']},
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])
    print "Found %d instances that need backing up" % len(instances)

    for instance in instances:
        try:
            retentionDurationDays = [
                int(t.get('Value')) for t in instance['Tags']
                if t['Key'] == 'retentionDurationDays'][0]
        except IndexError:
            retentionDurationDays = 3

        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs') is None:
                # skip anything that does not have EBS volumes
                continue
            vol_id = dev['Ebs']['VolumeId']
            print "Found EBS volume %s on instance %s" % (
                vol_id, instance['InstanceId'])
            ec.create_snapshot(
                VolumeId=vol_id,
            )

            to_tag[retentionDurationDays].append(snap['SnapshotId'])

            print
            "Retaining snapshot %s of volume %s from instance %s for %d days" %
            (
                snap['SnapshotId'], vol_id,
                instance['InstanceId'], retentionDurationDays_days,
            )
        for retentionDurationDays in to_tag.keys():
            delete_date = datetime.date.today()
            + datetime.timedelta(days=retentionDurationDays)
            delete_fmt = delete_date.strftime('%Y-%m-%d')
            print "Will delete %d snapshots on %s" %
            (len(to_tag[retentionDurationDays]), delete_fmt)
            ec.create_tags(
                Resources=to_tag[retentionDurationDays],
                Tags=[
                    {'Key': 'deleteOnDate', 'Value': delete_fmt},
                ]
            )
