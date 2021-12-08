import boto3
import json
import logging
from ocr_wrapper_service.utils.sqs_delete import delete_sqs_messages
import os

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info('Connecting to SQS sender...')
    sqs_client = boto3.client('sqs', region_name=os.getenv('REGION'))
except:
    logger.error('Error while connecting to SQS for sending msgs!')
    sqs_client = boto3.client('sqs', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                              AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'), region_name=os.getenv('REGION'))
    pass


def send_sqs_messages(output):
    logger.debug('Send ouput to sqs: %s' % output)
    queue_url = "https://sqs.us-east-1.amazonaws.com/{}/{}".format(os.getenv('ACCOUNT_NUMBER'), os.getenv('OUTPUT_QUEUE'))
    sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(output['body']))
    delete_sqs_messages(output['receipt_handle'])
    return True
