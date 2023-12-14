
import json
import datetime
import boto3

##Associate User with a JobListing to complete Saved Job Process
    #Expected POST body format
        #"user_id": "str",
        #"job_id": "str"

#CONSTANTS
SEENLISTINGS_TABLE_NAME = "userSeenListings"

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(SEENLISTINGS_TABLE_NAME)


def handler(event, context):
    event = json.loads(event["body"])
    seen_job = formatNewUserSavedListingEntry(event["user_id"], event["job_id"])

   #create new entry
    new_seen_job = table.put_item(
        Item = seen_job
    )

    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        }, 
        'body': f"job listing id: {seen_job['job_id']} saved by user id: {seen_job['user_id']}"
    }
    return response



##DEFAULT USERSAVEDLISTINGS ENTRY FORMAT
    # "user_id": "str, not-null", (partition key)
    # "job_id": "str, not-null", (sort-key)
    # "date_added": "str"

def formatNewUserSavedListingEntry(user_id, job_id):
    seen_job = {}

    seen_job["user_id"] = user_id
    seen_job["job_id"] = job_id
    seen_job["date_added"] = str(datetime.datetime.now())

    return seen_job
