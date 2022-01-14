import boto3
import logging
import json
from ocr_wrapper_service.constants import S3Constants
from ocr_wrapper_service.constants import SQSConstants
from ocr_wrapper_service.constants import LocalDirectoryConstants
from ocr_wrapper_service.utils.aws_services import sqs_receive_message
from ocr_wrapper_service.utils.aws_services import sqs_send_message
from ocr_wrapper_service.utils.aws_services import sqs_delete_message
from ocr_analytic_service.service.input_mod import read_input_and_form_output

logger = logging.getLogger(__name__)


def wrapper_service(sqs_client,s3_resource):
    logger.info("Inside Wrapper Function")
    bool_flag,received_messages=sqs_receive_message(sqs_client,SQSConstants.input_queue)
    if not bool_flag:
        return False
    bool_flag=process_messages(sqs_client,s3_resource,received_messages)
    return bool_flag



def process_image(s3_client,input_payload):
    try:
        logger.info("Invoking Analytics Engine")
        output = {'receipt_handle': input_payload['receipt_handle']}
        output_messages = read_input_and_form_output(s3_client,input_payload['body'])
        output['body'] = output_messages
        logger.info("OCR output : ")
        logger.info(json.dumps(output))
        return True,output
    except Exception as e:
        logger.info('Failed processing images!')
        logger.debug('Failed processing images! %s' % e)
        output = {}
        return False,output



def process_messages(sqs_client,s3_client,sqs_response):
    for message in sqs_response.get('Messages'):
        input_payload = {}
        input_payload['receipt_handle'] = message['ReceiptHandle']
        if 'Body' in message:
            body = json.loads(message['Body'])
            input_payload['body'] = body
            bool_flag,result=process_image(s3_client,input_payload)
            bool_flag,response=sqs_send_message(sqs_client,SQSConstants.output_queue,result.get('body'))
            if bool_flag:
                bool_flag,response=sqs_delete_message(sqs_client,SQSConstants.input_queue,input_payload['receipt_handle'])
        else:
            logger.info(f"skipped processing , body not present in the message : receipt_handle :{input_payload['reciept_handle']}")
            bool_flag,response=sqs_delete_message(sqs_client,SQSConstants.input_queue,input_payload['receipt_handle'])

    return True
