import boto3
import os
from jobPostFilter import jobAddFilter
from paragraphFilters import paragraphFilters
from bulletFilter import bulletFilter
import pandas as pd
import logging
from dotenv import dotenv_values
import sys
from datetime import datetime


# nltk.download('punkt')
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

def truncateTable(tableName):
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.getenv("aws_access_key_id"),
                              aws_secret_access_key=os.getenv("aws_secret_access_key"),
                              region_name=os.getenv("region_name"))
    table = dynamodb.Table(tableName)

    # get the table keys
    tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

    # Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ", ".join('#' + key for key in tableKeyNames)
    expressionAttrNames = {'#' + key: key for key in tableKeyNames}

    counter = 0
    page = table.scan(ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames)
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            counter += page["Count"]
            # Delete items in batches
            for itemKeys in page["Items"]:
                batch.delete_item(Key=itemKeys)
            # Fetch the next page
            if 'LastEvaluatedKey' in page:
                page = table.scan(
                    ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames,
                    ExclusiveStartKey=page['LastEvaluatedKey'])
            else:
                break
    print(f"Deleted {counter}")


def scrape(tableName):
    # Track the start time
    startTime = datetime.now()


    dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.getenv("aws_access_key_id"),
                              aws_secret_access_key=os.getenv("aws_secret_access_key"),
                              region_name=os.getenv("region_name"))
    table = dynamodb.Table(tableName)
    response = table.scan()
    result = response['Items']
    # TODO: Push the data to AWS DynamoDB
    batchKeeper= 0
    finaldata = pd.DataFrame()

    while 'LastEvaluatedKey' in response:
        logging.info('-------------Next Batch--------------')
        batchKeeper = batchKeeper + 1

        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        resultToProcess = response['Items']
        for eachDataPoint in resultToProcess:
            paragraphinformationText = ""
            logging.info('-------------Processing Data Point--------------')


            if (JobAddFilter.NumberChar(eachDataPoint['JobAdText'])) & \
                    (JobAddFilter.HasKeywords(eachDataPoint['JobAdText'])) & \
                    (True in [True if len(value) > 1 else False for key, value in JobAddFilter.detectBullets(eachDataPoint['JobAdText']).items()]):

                if (JobAddFilter.NumberChar(eachDataPoint['JobAdText'], 3000, 4000)):
                    eachDataPoint['JobAdText'] = JobAddFilter.removeIntroduction(eachDataPoint['JobAdText'])

                paragraphinformation = ParagraphFilters.countParagraph(eachDataPoint['JobAdText'])
                if (paragraphinformation[0] >= 2) & (paragraphinformation[0] <= 4):
                    paragraphinformationText = ParagraphFilters.ParagraphCharCountFilter(paragraphinformation[1])
                    paragraphinformationText = ParagraphFilters.ParagraphSentCountFilter(paragraphinformationText)
                    paragraphinformationText = ParagraphFilters.ParagraphEntityRecognister(paragraphinformationText)
                    paragraphinformationText = ParagraphFilters.phoneNumberDetection(paragraphinformationText)
                    paragraphinformationText = ParagraphFilters.emailDetection(paragraphinformationText)

                sectionalDic = JobAddFilter.detectBullets(eachDataPoint['JobAdText'])
                # sectionalDic = BulletFilter.recordCharCounter(sectionalDic)
                # sectionalDic = BulletFilter.bulletEntityRecognister(sectionalDic)
                # sectionalDic = BulletFilter.removeDot(sectionalDic)
                # sectionalDic = BulletFilter.bulletDropEmailAndWebsite(sectionalDic)

                eachDataPoint["paragraphinformation"] = paragraphinformationText
                for key, val in sectionalDic.items():
                    for eachValCount in range(len(val)):
                        category = JobAddFilter.categoryChecker(val[eachValCount], key, "keywords.csv")
                        eachDataPoint[key+"_"+str(eachValCount)+"_"+category] = val[eachValCount]

                logging.info('--------- PUSHING DATA ---------------' + str(eachDataPoint['Id']))

                finaldata = finaldata.append(eachDataPoint, ignore_index=True)
                finaldata = finaldata.reindex(sorted(finaldata.columns), axis=1)
                finaldata.to_csv("ProcessedData_Batch.csv")

                # finaldata.to_csv("ProcessedData_Batch-" + str(batchKeeper) + ".csv")

            result.extend(eachDataPoint['JobAdText'])
    datetime.now() - startTime



def scrapeAcceptReject(tableName, counterLimit):
    # Track the start time
    startTime = datetime.now()


    dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.getenv("aws_access_key_id"),
                              aws_secret_access_key=os.getenv("aws_secret_access_key"),
                              region_name=os.getenv("region_name"))
    table = dynamodb.Table(tableName)
    response = table.scan()
    result = response['Items']
    # TODO: Push the data to AWS DynamoDB
    batchKeeper= 0
    counter = 0
    finaldata = pd.DataFrame()

    while 'LastEvaluatedKey' in response:
        logging.info('-------------Next Batch--------------')
        batchKeeper = batchKeeper + 1


        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        resultToProcess = response['Items']
        for eachDataPoint in resultToProcess:

            ############################## Limiting the processing #############################
            print(counter)
            if counter == counterLimit: #Processing the top 50000+1 values
                print("DONE PROCESSING")
                sys.exit()
            #####################################################################################


            paragraphinformationText = ""
            logging.info('-------------Processing Data Point--------------')


            if (JobAddFilter.NumberChar(eachDataPoint['JobAdText'])) & \
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
                # print(sectionalDic.keys())
                for key, val in sectionalDic.items():
                    eachDataPoint[key] = val

                if ("Job Responsibilities" in eachDataPoint.keys()) and ("Skills & Experience" in eachDataPoint.keys()):
                    if (len(eachDataPoint["Job Responsibilities"]) > 0) or (len(eachDataPoint["Skills & Experience"]) > 0):
                        eachDataPoint["Decision"] = "Accepted"
                        for key, val in sectionalDic.items():
                            for eachValCount in range(len(val)):
                                category = JobAddFilter.categoryChecker(val[eachValCount], key)
                                eachDataPoint[key + "_" + str(eachValCount+1) + "_" + category] = val[eachValCount]
                                # eachDataPoint[key + "_" + str(eachValCount)] = val[eachValCount]
                    else:
                        eachDataPoint["Decision"] = "Rejected Because of Bullet business rules"
                elif ("Job Responsibilities" not in eachDataPoint.keys()):
                    eachDataPoint["Decision"] = "Rejected because unable to identify Job Responsibilities"

                elif ("Skills & Experience" not in eachDataPoint.keys()):
                    eachDataPoint["Decision"] = "Rejected because unable to identify Skills & Experience"

                else:
                    eachDataPoint["Decision"] = "Rejected because unable to identify Job Responsibilities and Skills & Experience"

                logging.info('--------- PUSHING DATA ---------------' + str(eachDataPoint['Id']))

                finaldata = finaldata.append(eachDataPoint, ignore_index=True)
                finaldata = finaldata.reindex(sorted(finaldata.columns), axis=1)
                finaldata.to_csv("ProcessedData_Batch.csv")

            else:
                eachDataPoint["Decision"] = "Rejected"
                finaldata = finaldata.append(eachDataPoint, ignore_index=True)
                finaldata = finaldata.reindex(sorted(finaldata.columns), axis=1)
                finaldata.to_csv("ProcessedData_Batch.csv")

                # finaldata.to_csv("ProcessedData_Batch-" + str(batchKeeper) + ".csv")

            counter = counter + 1 ## Updating the limit counter

            result.extend(eachDataPoint['JobAdText'])
    datetime.now() - startTime


if __name__ == '__main__':
    if str(sys.argv):
        limit = int(str(sys.argv[-1]))
    else:
        limit = 10000
    scrapeAcceptReject('JobDataWrangle', limit)
    # scrape('JobDataWrangle')
