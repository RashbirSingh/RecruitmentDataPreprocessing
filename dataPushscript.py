import boto3
import os
from jobPostFilter import jobAddFilter
from paragraphFilters import paragraphFilters
from bulletFilter import bulletFilter
import logging
from dotenv import dotenv_values
import sys
from DynamoCommands import DatabaseCommands
from bs4 import BeautifulSoup

config = dotenv_values(".env")
os.environ["aws_access_key_id"] = config["aws_access_key_id"]
os.environ["aws_secret_access_key"] = config["aws_secret_access_key"]
os.environ["region_name"] = config["region_name"]

logging.basicConfig(filename='app.log',
                    level=logging.INFO,
                    filemode='w',
                    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
JobAddFilter = jobAddFilter()
ParagraphFilters = paragraphFilters()
BulletFilter = bulletFilter()
dbc = DatabaseCommands()
acceptedTable = "AcceptedDataJobDataWrangle"
RejectedTable = "RejectedDataJobDataWrangle"
htmlTable = "HTMLDataJobDataWrangle"

def createTableInAWS(acceptedTable = "AcceptedDataJobDataWrangle",
                     RejectedTable = "RejectedDataJobDataWrangle",
                     htmlTable = "HTMLDataJobDataWrangle"):

    if dbc.tableExist(acceptedTable):
        logging.info(acceptedTable + " Table exist")
    else:
        logging.info(acceptedTable + " Does not exist, Creating Tables into AWS")
        dbc.createTable(acceptedTable, "Counter")

    if dbc.tableExist(RejectedTable):
        logging.info(RejectedTable + " Table exist")
    else:
        logging.info(RejectedTable + " Does not exist, Creating Tables into AWS")
        dbc.createTable(RejectedTable, "Counter")

    if dbc.tableExist(htmlTable):
        logging.info(htmlTable + " Table exist")
    else:
        logging.info(htmlTable + " Does not exist, Creating Tables into AWS")
        dbc.createTable(htmlTable, "Counter")



def scrapeAcceptReject(tableName, counterStart=-1):

    dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.getenv("aws_access_key_id"),
                              aws_secret_access_key=os.getenv("aws_secret_access_key"),
                              region_name=os.getenv("region_name"))

    table = dynamodb.Table(tableName)
    response = table.scan()
    result = response['Items']
    batchKeeper= 0
    counter = 0

    while 'LastEvaluatedKey' in response:
        logging.info('-------------Next Batch--------------')
        batchKeeper = batchKeeper + 1

        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        resultToProcess = response['Items']
        for eachDataPoint in resultToProcess:
            print(counter)
            logging.info(counter)

            eachDataPoint['Counter'] = counter
            eachDataPoint["Benefits"] = []
            eachDataPoint["Job Responsibilities"] = []
            eachDataPoint["Skills & Experience"] = []
            eachDataPoint["paragraphinformation"] = []

            if counter <= counterStart:
                counter = counter + 1
                continue

            paragraphinformationText = []


            if bool(BeautifulSoup(eachDataPoint['JobAdText'], "html.parser").find()) == True:
                logging.info('Encountered HTML Text, Pushing data to '+htmlTable)
                dbc.put_data(htmlTable, eachDataPoint)

            elif (JobAddFilter.NumberChar(eachDataPoint['JobAdText'])) & \
                    (JobAddFilter.HasKeywords(eachDataPoint['JobAdText'])) & \
                    (True in [True if len(value) > 1 else False for key, value in JobAddFilter.detectBullets(eachDataPoint['JobAdText']).items()]):

                if (JobAddFilter.NumberChar(eachDataPoint['JobAdText'], 4000, 5000)):
                    eachDataPoint['JobAdText'] = JobAddFilter.removeIntroduction(eachDataPoint['JobAdText'])
                    eachDataPoint['JobAdText'] = str(eachDataPoint['JobAdText'])


                paragraphinformation = ParagraphFilters.countParagraph(eachDataPoint['JobAdText'])
                if (paragraphinformation[0] >= 2) & (paragraphinformation[0] <= 4):
                    paragraphinformationText = ParagraphFilters.ParagraphCharCountFilter(paragraphinformation[1])
                    paragraphinformationText = ParagraphFilters.ParagraphSentCountFilter(paragraphinformationText)
                    paragraphinformationText = ParagraphFilters.ParagraphEntityRecognister(paragraphinformationText)
                    paragraphinformationText = ParagraphFilters.phoneNumberDetection(paragraphinformationText)
                    paragraphinformationText = ParagraphFilters.emailDetection(paragraphinformationText)

                sectionalDic = JobAddFilter.detectBullets(eachDataPoint['JobAdText'])
                sectionalDic = BulletFilter.recordCharCounter(sectionalDic)
                sectionalDic = BulletFilter.bulletEntityRecognister(sectionalDic)
                sectionalDic = BulletFilter.removeDot(sectionalDic)
                sectionalDic = BulletFilter.bulletDropEmailAndWebsite(sectionalDic)
                sectionalDic = BulletFilter.removeSpecialChar(sectionalDic)
                sectionalDic = BulletFilter.isQuestion(sectionalDic)
                sectionalDic = BulletFilter.hasPhoneNumber(sectionalDic)
                sectionalDic = BulletFilter.otherCleaning(sectionalDic)

                eachDataPoint["paragraphinformation"] = paragraphinformationText

                for key, val in sectionalDic.items():
                    eachDataPoint[key] = val

                if ("Job Responsibilities" in eachDataPoint.keys()) and ("Skills & Experience" in eachDataPoint.keys()):
                    if (len(eachDataPoint["Job Responsibilities"]) > 0) or (len(eachDataPoint["Skills & Experience"]) > 0):
                        eachDataPoint["Decision"] = "Accepted"

                        dbc.put_data(acceptedTable, eachDataPoint)

                    else:
                        eachDataPoint["Decision"] = "Rejected Because of Bullet business rules"
                        dbc.put_data(RejectedTable, eachDataPoint)

                elif ("Job Responsibilities" not in eachDataPoint.keys()):
                    eachDataPoint["Decision"] = "Rejected because unable to identify Job Responsibilities"
                    dbc.put_data(RejectedTable, eachDataPoint)

                elif ("Skills & Experience" not in eachDataPoint.keys()):
                    eachDataPoint["Decision"] = "Rejected because unable to identify Skills & Experience"
                    dbc.put_data(RejectedTable, eachDataPoint)

                else:
                    eachDataPoint["Decision"] = "Rejected because unable to identify Job Responsibilities and Skills & Experience"
                    dbc.put_data(RejectedTable, eachDataPoint)

                dbc.put_data(RejectedTable, eachDataPoint)

            else:
                eachDataPoint["Decision"] = "Rejected"
                dbc.put_data(RejectedTable, eachDataPoint)


            counter = counter + 1

            result.extend(eachDataPoint['JobAdText'])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        counterStart = int(str(sys.argv[-1]))
    else:
        counterStart = -1

    createTableInAWS()
    scrapeAcceptReject('JobDataWrangle', counterStart)
