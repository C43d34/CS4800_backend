##Delete user entry from Users dynamodb table
    #Expected POST body payload:
        #"user_id": "str" (partition key)


import json
import boto3

#CONSTANTS
USERS_TABLE_NAME = "Users"

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(USERS_TABLE_NAME)


def handler(event, context):
    event = json.loads(event["body"])
    delete_params = {
        "Key": {"user_id": event["user_id"]}
    }
    user_delete_response = table.delete_item(**delete_params)

    return {
      'statusCode': 200,
      'headers': {
          'Access-Control-Allow-Headers': '*',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
      },
      'body': json.dumps({
            'response': user_delete_response                                            
      })
    }