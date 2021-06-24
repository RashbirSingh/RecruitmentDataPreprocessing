import boto3
from boto3.dynamodb.conditions import Key
import os
from dotenv import dotenv_values


class DatabaseCommands:

    def __init__(self):
        config = dotenv_values(".env")
        os.environ["aws_access_key_id"] = config["aws_access_key_id"]
        os.environ["aws_secret_access_key"] = config["aws_secret_access_key"]
        os.environ["region_name"] = config["region_name"]

        self.dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.getenv("aws_access_key_id"),
                                       aws_secret_access_key=os.getenv("aws_secret_access_key"),
                                       region_name=os.getenv("region_name"))

    def createTable(self, tableName):
        table = self.dynamodb.create_table(
            TableName=tableName,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5000,
                'WriteCapacityUnits': 5000
            }
        )

        # Wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
        return table

    def get_item(self, id, tableName='JobDataWrangle'):
        table = self.dynamodb.Table(tableName)
        resp = table.get_item(
            Key={
                'id': id,
            }
        )
        if 'Item' in resp:
            return (resp['Item'])

    def deleteTable(self, tableName):
        table = self.dynamodb.Table(tableName)
        table.delete()
