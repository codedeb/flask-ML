import json
import boto3
import logging
import os
from ocr_wrapper_service.service.process_message_service import process_messages
from ocr_wrapper_service.utils.sqs_delete import delete_sqs_messages

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

print('in consumer')
try:
    sqs_client = boto3.client('sqs', region_name=os.getenv('REGION'))
except:
    logging.error('not able to connect ot sqs')
    # sqs_client = boto3.client('sqs', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    #                           AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'), region_name=os.getenv('REGION'))
    pass


def receive_messages():
    queue_url = "https://sqs.us-east-1.amazonaws.com/{}/{}".format(os.getenv('ACCOUNT_NUMBER'), os.getenv('INPUT_QUEUE'))
    # sqs_client = boto3.client('sqs', config=Config(proxies={'https': 'cis-americas-pitc-cinciz.proxy.corporate.gtm.ge.com:80'})
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1
    )
    print('raw messages', response)
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
    return True
