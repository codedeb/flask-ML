import boto3
import logging
import json
from wrapper_service.constants import SQSConstants
from wrapper_service.utils.aws_services import sqs_receive_message
from wrapper_service.utils.aws_services import sqs_send_message
from wrapper_service.utils.aws_services import sqs_delete_message
from analytic_service.input_mod import read_input_and_form_output
from analytic_service.componentBlade.modelArtifacts import detector
from wrapper_service.constants import ModelDetails
import time
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
        logger.info(f"OCR output :  {json.dumps(output)}")
        return True,output
    except Exception as e:
        #logger.info('Failed processing images!')
        logger.error(f"Failed processing images! {e}")
        output = {}
        return False,output



def process_messages(sqs_client,s3_client,sqs_response):
    for message in sqs_response.get('Messages'):
        start = time.time()
        logger.info("Timer Initialization")
        input_payload = {}
        input_payload['receipt_handle'] = message['ReceiptHandle']
        logger.info(f"Message :  {json.dumps(message)}")
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
        end=time.time()
        elapsed =end-start
        logger.info(f"Elapsed time is {elapsed} seconds.")
    return True


def load_predictors():
    logger.info("Initializing Predictor Objects")
    segmentation_predictor=detector(ModelDetails.segmentation_config_path,ModelDetails.segmentation_model_path,ModelDetails.segmentation_threshold)
    dot_punch_predictor=detector(ModelDetails.dot_punch_config_path,ModelDetails.dot_punch_model_path,ModelDetails.dot_punch_threshold)
    return segmentation_predictor,dot_punch_predictor

