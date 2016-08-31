#!/usr/bin/python
import boto3
import json
import decimal

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('SOME-TABLE-NAME')

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):

    try:
        put = table.put_item(
            Item ={
                'id': 'DYNAMODB_POLL',
                'task_id': 'TASK_ID',
                'unix_time': 7,
            }
        )

        print("PutItem succeeded:")
        print(json.dumps(put, indent=4, cls=DecimalEncoder))

        query_table = table.get_item(
            Key={
                'id': 'DYNAMODB_POLL'
            }
        )

        query_table = query_table['Item']
        print("GetItem Table succeeded:")
        print(json.dumps(query_table, indent=4, cls=DecimalEncoder))

        query_index = table.query(
            IndexName='task_id-unix_time-index',
            KeyConditions={
                'task_id': {
                    'AttributeValueList': [
                        'TASK_ID'
                    ],
                    'ComparisonOperator': 'EQ'
                }
            }
        )

        query_index = query_index['Items']
        print("GetItem Index succeeded:")
        print(json.dumps(query_index, indent=4, cls=DecimalEncoder))

        delete = table.delete_item(
            Key={
                'id': 'DYNAMODB_POLL'
            }
        )

        print("DeleteItem succeeded:")
        print(json.dumps(delete, indent=4, cls=DecimalEncoder))
    except Exception as e:
        print(e)
        print('Error performing table operations. Make sure the table exists and is in the same region as this function.')
        raise e
