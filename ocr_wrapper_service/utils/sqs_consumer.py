import json
import boto3
import botocore
import logging
import os
from ocr_wrapper_service.service.process_message_service import process_messages
from ocr_wrapper_service.utils.sqs_delete import delete_sqs_messages

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info('Connecting to SQS consumer...')
    sqs_client = boto3.client('sqs', region_name=os.getenv('REGION'))
except:
    logger.error('Error while connecting to SQS for consuming msgs!')
    sqs_client = boto3.client('sqs', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), region_name=os.getenv('REGION'))
    pass


def receive_messages():
    logger.info('Connecting to queue...')
    queue_url = "https://sqs.us-east-1.amazonaws.com/{}/{}".format(os.getenv('ACCOUNT_NUMBER'), os.getenv('INPUT_QUEUE'))
    # sqs_client = boto3.client('sqs', config=Config(proxies={'https': 'cis-americas-pitc-cinciz.proxy.corporate.gtm.ge.com:80'})
    logger.debug('sqs url: %s' % queue_url)
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1
    )
    logger.debug('raw messages %s' % response)
    if 'Messages' in response:
        for message in response['Messages']:
            input = {}
            receipt_handle = message['ReceiptHandle']
            input['receipt_handle'] = receipt_handle
            if 'Body' in message:
                body = json.loads(message['Body'])
                input['body'] = body
                # body['receipt_handle'] = receipt_handle
                process_messages(input)
            else:
                logger.error('No Body present while reading sqs message')
                delete_sqs_messages(receipt_handle)
            # messages_list.append(body)
            # process_sqs_messages(messages_list)
    # if len(messages_list) > 0:
    #     analytic_input_json['input'] = messages_list

    # print('messages', messages_list)

    # local testing:
    # logger.info('Calling analytics for local!')
    # input = {}
    # input_dict = '[{"imageId": 1, "imageOcrType": "PARTDRAWINGNUMBER", "imagePath": "IDM/dev/163/PARTSOUT/1632995892574_Raw_S1B_297719_dot_punched_IMG_2027.JPG", "positionNumber": 2, "componentId": 1234, "componentName": "S1B"}]'
    # input['receipt_handle'] = 'abc'
    # body = json.loads(input_dict)
    # input['body'] = body
    # process_messages(input)
    return True
