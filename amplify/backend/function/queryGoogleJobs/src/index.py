##Returns a list of jobs most closely matched with input keyword string
    #Expected POST request body in JSON format:
        #[{},{},{}...] list of dictionary objects which represent an individual job query
        #Contains the following key:value pair for each object
            #"query" : "some string of keywords or other search parameters" 

#May return 0 results

#TODO: Add optional googlejobs query parameters:
    #jobCategories
    #locationFilters

import os
import json
import boto3
import random

from googleapiclient.discovery import build
from googleapiclient.errors import Error

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "igneous-tracer-401703-f52a40df0c10.json"
os.environ["GOOGLE_CLOUD_PROJECT"] = "igneous-tracer-401703"

client_service = build("jobs", "v3")


seen_job_ids = []
def handler(event, context):
    event_body = json.loads(event["body"])
    print(event_body)

    parent = "projects/" + os.environ["GOOGLE_CLOUD_PROJECT"]

    #optional metadata specific to current user...
        #NOT CURRENTLY USED
    request_metadata = { 
        "user_id": "HashedUserId",
        "session_id": "HashedSessionId",
        "domain": "www.google.com",
    }

    user_id_key = 'user_id'
    user_id_value = event_body['user_id']

    # Create a DynamoDB resource
    dynamodb = boto3.resource('dynamodb')

    # Access the DynamoDB table
    table = dynamodb.Table('userSeenListings')

    try:
        # Query the DynamoDB table for items with the specified user_id
        response = table.query(
            KeyConditionExpression=f"{user_id_key} = :value",
            ExpressionAttributeValues={
                ":value": user_id_value
            }
        )
        items = response.get('Items', [])

        seen_job_ids = [item["job_id"] for item in items]

        """        #debugging
        return {
            'statusCode': 200,
            'body': f'Retrieved {len(items)} items with user_id {user_id_value}',
            'items': items
        }"""

    except Exception as e:
        seen_job_ids = []
    
    already_acquired_job_ids = []
    list_of_jobs = []
    for query_dict in event_body["queries"]:
        print(query_dict)
        print(len(list_of_jobs))
        keywords = query_dict["query"]
        print(f"KEYWORDS: {keywords}")
        if not keywords:
            continue
        

        #queries = [item["query"] for item in event_body]
        #print(f"QUERIES:{queries}")
        #query_string = event_body[0]["query"]
        
         
        skills = [part.strip() for part in keywords.split(',')]
        #print(f"SKILLS: {skills}")
        #random_elements = random.sample(skills, 2)
        for skill in skills:
            
            job_query = {"query": skill}
            
            # company_name = "projects/igneous-tracer-401703/companies/88a5289e-1c35-478a-93c4-a83eee16140e"
            company_name = None #option to specify jobs within a specific company
            if company_name is not None:
                job_query.update({"company_names": [company_name]})

            """        if location is not None:
                job_query.update({"company_names": [company_name]})"""

            #print(f"JOB QUERY:{job_query}")
            request = {
                "search_mode": "JOB_SEARCH",
                "request_metadata": request_metadata,
                "job_query": job_query,
            }
            response = (
                client_service.projects().jobs().search(parent=parent, body=request).execute()
            )

            if ('matchingJobs' in response):
                #check for duplicate jobs already acquired
                for job in response['matchingJobs']:
                    job_id = job["job"]["requisitionId"]
                    if job_id not in already_acquired_job_ids and job_id not in seen_job_ids:
                        list_of_jobs.append(job["job"])
                        already_acquired_job_ids.append(job_id)

    #print(f"SEEN JOBS:{seen_job_ids}")
    #print(f"ALREADY AQUIRED JOB IDS: {already_acquired_job_ids}")
    
    # print(f"Search params: {keywords}")
    # if ('matchingJobs' in response):
    #     print(f"List of Jobs Matched {[match['job']['companyDisplayName'] for match in response['matchingJobs']]}")
    # else:
    #     print("No Matches")
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({
            'search_query': keywords,
            # 'length': len(response["matchingJobs"]) if 'matchingJobs' in response else 0,
            # 'matches': [match['job'] for match in response['matchingJobs']] if 'matchingJobs' in response else "No Matches",
            'length': len(list_of_jobs),
            'matches': list_of_jobs,
        
        })
    }