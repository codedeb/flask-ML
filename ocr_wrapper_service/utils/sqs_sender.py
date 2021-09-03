import boto3
import json
from ocr_wrapper_service.utils.sqs_delete import delete_sqs_messages
import os
# sqs_client = boto3.client('sqs', region_name='us-east-1')
try:
    sqs_client = boto3.client('sqs', region_name=os.getenv('REGION'))
except:
    sqs_client = boto3.client('sqs', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                              AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'), region_name=os.getenv('REGION'))
    pass


def send_sqs_messages(output):
    print('in send', output)
    queue_url = "https://{}/{}".format(os.getenv('AWS_ACCOUNT_NUMBER'), os.getenv('OUTPUT_QUEUE'))
    sqs_client.send_message(QueueUrl=queue_url,
                            MessageBody=json.dumps(output['body']))
    delete_sqs_messages(output['receipt_handle'])
    return True
