##Get ResumeProfile data entry specified by the primary key (partition key + sort key)
    #Expected POST body payload:
        #"user_id": "str" (partition key)
        #"upload_date": "str" (sort key) (optional)

#Returns Resume Profile entry in json format

import json
import boto3

#CONSTANTS
RESUMEPROFILE_TABLE_NAME = "ResumeProfiles"

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(RESUMEPROFILE_TABLE_NAME)


def handler(event, context):
    event = json.loads(event["body"])

    if ("upload_date" in event):
        query_params = {
            "KeyConditionExpression" : "#user_id = :user_id" + " AND " + "#upload_date = :upload_date",
            # "FilterExpression" :
            "ExpressionAttributeNames": {"#user_id": "user_id", "#upload_date": "upload_date"},
            "ExpressionAttributeValues": {":user_id": event["user_id"], ":upload_date": event["upload_date"]},
        }
    else:
        query_params = {
            "KeyConditionExpression" : "#user_id = :user_id",
            # "FilterExpression" :
            "ExpressionAttributeNames": {"#user_id": "user_id"},
            "ExpressionAttributeValues": {":user_id": event["user_id"]},
        }

    response = table.query(**query_params)
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },        
        "body": json.dumps(response["Items"])
    }