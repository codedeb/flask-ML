import boto3
import os
# sqs_client = boto3.client('sqs', region_name='us-east-1')
try:
    sqs_client = boto3.client('sqs', region_name=os.getenv('REGION'))
except:
    sqs_client = boto3.client('sqs', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                              AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'), region_name=os.getenv('REGION'))
    pass

def delete_sqs_messages(receipt_handle):
    queue_url = "https://{}/{}".format(os.getenv('AWS_ACCOUNT_NUMBER'), os.getenv('INPUT_QUEUE'))
    sqs_client.delete_message(QueueUrl=queue_url,
                              ReceiptHandle=receipt_handle)
    return True
