import boto3
import os
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.debug('Connecting to SQS for deleting msgs...')
    sqs_client = boto3.client('sqs', region_name=os.getenv('REGION'))
except:
    logging.error('Error while connecting to SQS for deleting msgs!')
    sqs_client = boto3.client('sqs', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                              AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'), region_name=os.getenv('REGION'))
    pass

def delete_sqs_messages(receipt_handle):
    try:
        logger.debug('Deleting message from SQS: %s' % receipt_handle)
        queue_url = "https://sqs.us-east-1.amazonaws.com/{}/{}".format(os.getenv('ACCOUNT_NUMBER'), os.getenv('INPUT_QUEUE'))
        sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        return True
    except Exception as e:
        logger.info('Error while deleting message from SQS!')
        logger.debug('Error while deleting message from SQS! %s' % e)
        return False
