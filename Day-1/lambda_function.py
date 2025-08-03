import boto3
import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    bucket = event['Records'][0]['s3']['bucket']['name']
    key    = event['Records'][0]['s3']['object']['key']

    response = s3.get_object(Bucket=bucket, Key=key)
    log_data = response['Body'].read().decode('utf-8')

    log_excerpt = log_data[:3000]  # OpenAI token limit

    prompt = f"Summarize the following server log:\n\n{log_excerpt}"

    summary_response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    summary = summary_response.choices[0].message.content.strip()

    summary_key = key.replace(".log", "_summary.txt")
    s3.put_object(
        Bucket=os.environ['SUMMARY_BUCKET'],
        Key=summary_key,
        Body=summary.encode()
    )

    return {
        "statusCode": 200,
        "body": f"Summary written to {summary_key}"
    }
