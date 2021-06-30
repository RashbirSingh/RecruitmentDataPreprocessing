import pyodbc
import boto3
import os
import sys

os.environ["aws_access_key_id"] = "AKIA6I4GCS6TF2GSHNUJ"
os.environ["aws_secret_access_key"] = "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"
os.environ["region_name"] = 'ap-southeast-1'

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=ARES66;'
                      'Database=JobAdDataWrangling;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()
cursor.execute('SELECT * FROM JobAdDataWrangling.dbo.Query')

dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.getenv("aws_access_key_id"),
                          aws_secret_access_key=os.getenv ("aws_secret_access_key"),
                          region_name =os.getenv("region_name"))

def pushScript(limit):
    count = 0
    table = dynamodb.Table("JobDataWrangle")
    for row in cursor:


        count = count + 1
        print(count)
        if count < limit :
            continue
        else:
            table.put_item( Item = {'Id': row[0],
                                    'ListingDate': row[1],
                                    'AdvertiserId': row[2],
                                    'AdvertiserName': row[3],
                                    'LeadSource': row[4],
                                    'SourceJobId': row[5],
                                    'GeodataId': row[6],
                                    'JobLocation': row[7],
                                    'CountryId': row[8],
                                    'ClassificationId': row[9],
                                    'ClassificationName': row[10],
                                    'SubclassificationId': row[11],
                                    'SubclassificationName': row[12],
                                    'RoleId': row[13],
                                    'OriginalJobTitle': row[14],
                                    'SalaryRange': row[15],
                                    'MinSalary': row[16],
                                    'MaxSalary': row[17],
                                    'JobAdText': row[18],
                                    })

if __name__ == '__main__':
    if len(sys.argv) > 1:
        limit = int(str(sys.argv[-1]))
    else:
        limit = -1

    pushScript(limit)