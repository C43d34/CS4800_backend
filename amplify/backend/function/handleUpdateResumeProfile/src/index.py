##Update attributes of resume profile
    #Expected POST body payload:
        #"user_id": "str" (partition key)
        #"upload_date": "str" (sort key)
        #"resume_id": "str" (optional (MUTUALLY EXCLUSIVE WITH: UPLOAD DATE))
        #"update_attributes": {dict} (key-val of attributes to modify)

#Returns Resume Profile entry in json format after update effects

import json
import boto3

#CONSTANTS
RESUMEPROFILE_TABLE_NAME = "ResumeProfiles"

# create a DynamoDB object using the AWS SDK
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(RESUMEPROFILE_TABLE_NAME)


def handler(event, context):
    event = json.loads(event["body"])
#Ensure format of updated attributes are correct before sending to DB table
    updated_attributes_dict = formatExistingResProfile(event["update_attributes"])
    update_expr_substr_list = []
    expr_attr_names = {}
    expr_attr_vals = {}
    for attr_key in updated_attributes_dict:
        update_expr_substr_list.append(f"#{attr_key} = :{attr_key}")
        expr_attr_names[f"#{attr_key}"] = attr_key
        expr_attr_vals[f":{attr_key}"] = updated_attributes_dict[attr_key]

    #If upload_date specified
    if ("upload_date" in event):
            update_params = {
                "Key": {"user_id": event["user_id"], "upload_date": event["upload_date"]},
                "UpdateExpression": "SET " + ", ".join(update_expr_substr_list), #setting attributes to new values
                "ExpressionAttributeNames": expr_attr_names,
                "ExpressionAttributeValues": expr_attr_vals,
                "ReturnValues": "ALL_NEW"
            }
            updated_resume_prof_response = table.update_item(**update_params)

    #If resume_id specified
    #Query and Filter for profile(s) that belong to said resume_id (standard attribute) within user_id (partition)
    elif ("resume_id" in event):
        query_params = {
            "KeyConditionExpression" : "#user_id = :user_id",
            "FilterExpression" : "#resume_id = :resume_id",
            "ExpressionAttributeNames": {"#user_id": "user_id", "#resume_id": "resume_id"},
            "ExpressionAttributeValues": {":user_id": event["user_id"], ":resume_id": event["resume_id"]},
        }
        query_response = table.query(**query_params)

        #use primary keys in response and update items directly
        for item in query_response["Items"]:

            
            update_params = {
                "Key": {"user_id": item["user_id"], "upload_date": item["upload_date"]},
                "UpdateExpression": "SET " + ", ".join(update_expr_substr_list), #setting attributes to new values
                "ExpressionAttributeNames": expr_attr_names,
                "ExpressionAttributeValues": expr_attr_vals,
                "ReturnValues": "ALL_NEW"
            }
            updated_resume_prof_response = table.update_item(**update_params)

            

    #TODO: if neither above specified, two possibilities
        #return error, bad input
        #delete all resumeprofiles belonging to user_id
    else:
         print()
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },  
        "body": json.dumps({
            'updated_item': updated_resume_prof_response["Attributes"]
            #Note: possibility of multiple items updated.
                #when returning response to endpoint, only going to send most recently update - assume every resume profile belongs to only 1 resume_id
        })        
    }
    
    
    
##Handle input data and assign required/default keys to dictionary
    #With respect to ResumeProfile table in DynamoDB
#Returns a formatted dictionary object


#DEFAULT RESUMEPROFILE ENTRY STRUCTURE
# {
#     "user_id" : "str, not_null", (partition key)
#     "upload_date": "str, not_null", (sort key)
#     "":""
# }


def formatExistingResProfile(dictionary_input_data):
    formatted_resprofile_entry = {}
    
    #Partition Key: user_id
        #do not allow changing of user_id
    if ("user_id" in dictionary_input_data):
        ##TODO Raise invalid input error
        del(dictionary_input_data["user_id"])
    
    #Sort Key: upload_date
        #do not allow changing of upload date
    if ("upload_date" in dictionary_input_data):
        ##TODO Raise invalid input error
        del(dictionary_input_data["upload_date"])


    formatted_resprofile_entry = dictionary_input_data
    return formatted_resprofile_entry
