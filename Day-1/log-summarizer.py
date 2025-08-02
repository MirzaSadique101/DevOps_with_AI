import boto3
import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    
    # Extract bucket and key from S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key    = event['Records'][0]['s3']['object']['key']
    
    # Read log file content
    response = s3.get_object(Bucket=bucket, Key=key)
    log_content = response['Body'].read().decode('utf-8')

    # Truncate for OpenAI input limits
    log_excerpt = log_content[:3000] if len(log_content) > 3000 else log_content
    
    # Call OpenAI to summarize
    prompt = f"Summarize the following log:\n\n{log_excerpt}"
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    summary = completion.choices[0].message.content.strip()
    
    # Save summary to second bucket
    summary_key = key.replace(".log", "_summary.txt")
    s3.put_object(
        Bucket="log-summary-bucket-devops-ai",
        Key=summary_key,
        Body=summary.encode()
    )

    return {
        "statusCode": 200,
        "body": f"Summary created: {summary_key}"
    }
