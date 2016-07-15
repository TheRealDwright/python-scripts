import boto3
import re


def describe_log_groups(client, log_prefix):
    response = client.describe_log_groups(
        logGroupNamePrefix=log_prefix
    )
    return response["logGroups"]


def lambda_handler(event, context):

    client = boto3.client("logs")
    log_prefix = "/aws/lambda"
    log_string = ".*lookupStackOutputs.*"

    if log_prefix:
        print(
            "Retrieving log groups that match prefix"
        )
        all_log_groups = describe_log_groups(client, log_prefix)

    log_groups = [log_group["logGroupName"]
                  for log_group in all_log_groups
                  if re.match(log_string, log_group["logGroupName"])]

    print(
        "Deleting matching log groups"
    )
    for log_group in log_groups:
        for log_group in log_groups:
            print("Deleting log group: %s") % log_group
            client.delete_log_group(
                logGroupName=log_group
            )
