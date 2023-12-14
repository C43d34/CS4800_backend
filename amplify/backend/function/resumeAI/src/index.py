from openai import OpenAI
#import fitz
import boto3
import PyPDF2
import io

def handler(event, context):

    resume_id = event['resume_id']  
    key = f'public/{resume_id}'
    #key = f'{resume_id}.pdf'
    s3 = boto3.client('s3')
    
    a = 0
    try:

        response = s3.get_object(Bucket='userresumes', Key=key)
        a = 1
        resume = response['Body'].read()
        a = 1.1
        resume_file_like = io.BytesIO(resume)
        a= 1.2
        pdf_reader = PyPDF2.PdfReader(resume_file_like)
        a = 1.3
        resume_text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            resume_text += pdf_reader.pages[page_num].extract_text()
        
        a = 2

        client = OpenAI(api_key="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")
        a = 3
        primer = f"""You are Q&A bot. A highly intelligent system that answers
        user questions based on the information provided by the user above
        each question. If the information can not be found in the information
        provided by the user leave the response blank.
        """
        #contexts is a list of context chunks. ie we split the resume into multiple chunks to
        #get chatgpt to answer it better because it tends to use only the beginning and the end
        a = 3.1
        query = resume_text + """give me name, location, job title (ie software engineer), education, ie bachelors of science in Engineering from cal poly pomona.
                    give me total years of experience based on any job dates. give me work experience, ie Systems Analyst - Cisco 2021-2022
                    give me hard skills. list any links the user might have to sites like github, linked in but only if they have the html link. 
                    keywords are a few words that describe the industry/profession. format it like this: 
                    'Name: x
                    Location: x
                    Title: x
                    Education: x
                    Work Experience: x, y, z
                    Years of experience: x
                    Skills: x, y, z
                    Links: x, y
                    Keywords: x, y, z'
                    do not add any explanation at the beginning or end. your entire answer must follow the format in the quotes. 
                    If you cannot find the information leave the space after the format blank."""
        a= 3.2
        #augmented_query = "\n\n---\n\n".join(contexts)+"\n\n-----\n\n"+query
        
        #Ask AI
        a = 3.5
        answer = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": primer},
                {"role": "user", "content": query}
            ]
        )
        #print(answer)
        a = 4

        res = answer.choices[0].message.content
        a = 4.1
        
        a = 4.2
        
        profile_dict = {}

        lines = res.strip().split('\n')

        for line in lines:
            key, value = map(str.strip, line.split(':', 1))
            profile_dict[key] = value

        #print(profile_dict)

        a = 10
        return {
            'statusCode': 200,
            'body': 'Object retrieval successful',
            'profile' : profile_dict,
        }
        
    except Exception as e:
        print('Error:', e)
        return {
            'key' : key,
            'a' : a,
            'statusCode': 500,
            'body': 'Error retrieving object',
        }