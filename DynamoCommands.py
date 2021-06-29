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

    def createTable(self, tableName, primarykeyName = "id"):
        """
        Create Table in the aws server DynamoDB
        ...

        Parameters
        ----------
        tableName : str
            Name of the table to be created in the AWS
        primarykeyName : str
            Name of the primary key for the table

        Returns
        -------
        table
            DynamoDb table object after creation
        """

        table = self.dynamodb.create_table(
            TableName=tableName,
            KeySchema=[
                {
                    'AttributeName': primarykeyName,
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': primarykeyName,
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

    #TODO: Not currently is use see if can be used
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
        """
        Delete Table in the aws server DynamoDB
        ...

        Parameters
        ----------
        tableName : str
            Name of the table to be deleted in the AWS

        Returns
        -------
        NA
        """
        table = self.dynamodb.Table(tableName)
        table.delete()

    def tableExist(self, tableName):
        """
        Check if the Table exist in the aws server DynamoDB
        ...

        Parameters
        ----------
        tableName : str
            Name of the table search in the AWS

        Returns
        -------
        Bool
            True: if table exist
            False: if table does not exist
        """
        existingTable = [table.name for table in self.dynamodb.tables.all()]

        if tableName in existingTable:
            return True
        else:
            return False

    def put_data(self, tableName, tableData):
        """
        Push the data in the aws server DynamoDB
        ...

        Parameters
        ----------
        tableName : str
            Name of the table where the need to be pushed
        tableData : dict
            Dict data to be pushed into the table columns.
            Following fields are required:
                1. AdvertiserId
                2. AdvertiserName
                3. Benefits
                4. ClassificationId
                5. ClassificationName
                6. Counter
                7. CountryId
                8. GeodataId
                9. Id
                10. Job Responsibilities
                11. JobAdText
                12. JobLocation
                13. LeadSource
                14. ListingDate
                15. MaxSalary
                16. MinSalary
                17. OriginalJobTitle
                18. RoleId
                19. SalaryRange
                20. Skills & Experience
                21. SourceJobId
                22. SubclassificationId
                23. SubclassificationName
                24. paragraphinformation

        Returns
        -------
        Bool
            True: If execution done without error
            False: If execution has some error
        """
        try:
            table = self.dynamodb.Table(tableName)
            table.put_item(
                Item={
                    'AdvertiserId': tableData['AdvertiserId'],
                    'AdvertiserName': tableData['AdvertiserName'],
                    'Benefits': tableData['Benefits'],
                    'ClassificationId': tableData['ClassificationId'],
                    'ClassificationName': tableData['ClassificationName'],
                    'Counter': tableData['Counter'],
                    'CountryId': tableData['CountryId'],
                    "GeodataId": tableData['GeodataId'],
                    "Id": tableData['Id'],
                    "Job Responsibilities": tableData['Job Responsibilities'],
                    "JobAdText": tableData['JobAdText'],
                    "JobLocation": tableData['JobLocation'],
                    "LeadSource": tableData['LeadSource'],
                    "ListingDate": tableData['ListingDate'],
                    "MaxSalary": tableData['MaxSalary'],
                    "MinSalary": tableData['MinSalary'],
                    'OriginalJobTitle': tableData['OriginalJobTitle'],
                    'RoleId': tableData['RoleId'],
                    'SalaryRange': tableData['SalaryRange'],
                    'Skills & Experience': tableData['Skills & Experience'],
                    'SourceJobId': tableData['SourceJobId'],
                    'SubclassificationId': tableData['SubclassificationId'],
                    'SubclassificationName': tableData['SubclassificationName'],
                    'paragraphinformation': tableData['paragraphinformation'],
                }
            )

            return True
        except:
            return False