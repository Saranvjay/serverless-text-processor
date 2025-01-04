import json
import boto3
import os

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']

        # Read file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        content = response['Body'].read().decode('utf-8')
        line_count = len(content.splitlines())

        # Save to DynamoDB
        table.put_item(Item={
            'file_id': file_key,
            'timestamp': record['eventTime'],
            'line_count': line_count
        })

    return {
        'statusCode': 200,
        'body': json.dumps('File processed successfully!')
    }

