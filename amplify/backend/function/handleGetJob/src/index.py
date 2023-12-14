##Acquire detailed job listing data from dynamodb
    #Expected POST body Payload:
        #"job_id": "str" (partition key)
#Returns singular JobListing object

import boto3
import json
from dynamodb_json import json_util as ddb_json

#CONSTANTS
JOBLISTINGS_TABLE_NAME = "JobListings"

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
job_listings_table = dynamodb.Table(JOBLISTINGS_TABLE_NAME)


def handler(event, context):
    event = json.loads(event["body"])

#Use "job_id" keys to get listing details from table JobListings
    job_id = event["job_id"]
    job_listing = job_listings_table.get_item(
        Key = {"job_id": job_id}
    )
    print(job_listing)
    #parse "Decimal" type data which is annoying and cant be json seralized
    parsed_job_listing = ddb_json.loads(job_listing["Item"])


    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },   
        "body": json.dumps(parsed_job_listing)         
    }
