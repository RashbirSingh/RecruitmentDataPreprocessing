import boto3
from boto3.dynamodb.conditions import Key


def get_item():
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.getenv("aws_access_key_id"),
                              aws_secret_access_key=os.getenv("aws_secret_access_key"),
                              region_name=os.getenv("region_name"))

    table = dynamodb.Table('JobDataWrangle')

    resp = table.get_item(
        Key={
            'id': 47,
        }
    )

    if 'Item' in resp:
        print(resp['Item'])