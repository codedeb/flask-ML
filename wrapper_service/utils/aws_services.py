import boto3
import os
import logging
import json
from wrapper_service.constants import S3Constants
from wrapper_service.constants import SQSConstants
from wrapper_service.constants import LocalDirectoryConstants
import re

logger = logging.getLogger(__name__)

def s3_client():
    try:
        logger.info('Initializing s3 client')
        s3 = boto3.client('s3', region_name=S3Constants.region)
    except Exception as e:
        logger.error(f"error while intializing s3 client : {e}")
        logger.error('Connecting with s3 with access credentials...')
        s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), aws_session_token=os.getenv('AWS_SESSION_TOKEN'), region_name=os.getenv('REGION'))
        pass
    return s3

def s3_resource():
    try:
        logger.info('Initializing s3 resource')
        s3_resource = boto3.resource('s3', region_name=S3Constants.region)
    except Exception as e:
        logger.error(f"error while intializing s3 resource : {e}")
        s3_resource = boto3.resource('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                     AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'),
                                     region_name=os.getenv('REGION'))
        pass

    return s3_resource

def sqs_client():
    try:
        logger.info('initializing sqs client')
        sqs_client = boto3.client('sqs', region_name=SQSConstants.region)
    except Exception as e:
        logger.error(f"error while intializing sqs client : {e}")
        sqs_client = boto3.client('sqs', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                  region_name=os.getenv('REGION'))
        pass
    return sqs_client

def s3_model_download(s3):
    """
    Used for downloading of models from specific S3 location
    :param s3: s3 client for connection
    :return: bool : True or False
    """
    try:
        logger.debug('Listing objects for bucket: %s' % S3Constants.bucket_name)
        # Retrieve the objects deom specific IDM model folder
        logger.info(f"Listing Objects from Bucket : {S3Constants.bucket_name} and Path : {S3Constants.model_path}")
        objects = s3.list_objects(Bucket=S3Constants.bucket_name, MaxKeys=10, Prefix=S3Constants.model_path)
        logger.info('S3 objects: %s' % objects)
        logger.info(objects)

        # Path where model will be downloaded
        #base_path = LocalDirectoryConstants.model_path
        #model_path = os.path.join(base_path, 'model')
        model_path = LocalDirectoryConstants.model_path
        logger.info('model_path: %s' %  model_path)

        #Checking whether all the models are available in S3.
        if objects.get('Contents'):
            models_available=len(objects.get('Contents'))
            if models_available>=S3Constants.model_count:
                logger.info(f"No of available models in S3 : {models_available} , Required no of models : {S3Constants.model_count} ")

            else:
                logger.info(f"No of available models in S3 : {models_available} , Required no of models : {S3Constants.model_count} ")
                return False
        else:
            logger.info("Model files are not available")
            return False

        #Verify whether filename regex matches
        models_available={}
        models_flag = False
        for object in objects['Contents']:
            model_name=object["Key"].split("/")[-1]
            for regex_model_name in S3Constants.model_names:
                regex_result = re.search(regex_model_name, model_name)
                if regex_result:
                    models_available[regex_model_name] = True
                    models_flag = True
                else:
                    if not models_available.get(regex_model_name):
                        models_available[regex_model_name] = False
                        models_flag = False

        if not models_flag:
            logger.info("Models filenames are not matching")
            logger.info(f"Models Flag : {models_flag}")
            logger.info(json.dumps(models_available))
            return False
        else:
            logger.info("Models filenames are matching")
            logger.info(f"Models Flag : {models_flag}")
            logger.info(json.dumps(models_available))

        # downloading files
        for object in objects['Contents']:
            path, filename = os.path.split(object['Key'])
            logger.info('file to be downloaded: %s' %  filename)
            # Create directory if doesnt exist
            os.makedirs(model_path, exist_ok=True)
            modelDownloaded = os.path.join(model_path, filename)
        
            logger.info('file downloaded in container path: %s' %  modelDownloaded)
            # Download file
            s3.download_file(S3Constants.bucket_name, object['Key'], modelDownloaded)
        return True
    except Exception as e:
        logger.error(f"error while downloading models from s3 : {e}")
        return False

def sqs_receive_message(sqs_client,queue_url=SQSConstants.input_queue):
    """

    :param sqs_client:
    :param queue_url:
    :return:
    """
    try:
        logger.info(f"Polling SQS URL: {queue_url}")
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=SQSConstants.max_number_of_messages,
            WaitTimeSeconds=SQSConstants.wait_time_seconds
        )
        # response = 
        logger.info(f"Received Messages : {json.dumps(response)}")
        if "Messages" in response and response['ResponseMetadata']['HTTPStatusCode']==200:
            return True,response
        else:
            return False,response
    except Exception as e:
        logger.error(f"Received Exception in sqs_receive_message {e}")
        return False,False

def sqs_delete_message(sqs_client,queue_url,receipt_handle):
    try:
        logger.info(f"Deleting Message SQS URL: {queue_url} Receipt Handle :{receipt_handle}")
        response=sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        logger.info(json.dumps(response))
        if response['ResponseMetadata']['HTTPStatusCode']==200:
            return True,response
        else:
            logger.info(f"retrying to delete message Receipt Handle : {receipt_handle}")
            for i in range(0,3):
                response = sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
                if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                    return True, response
            return False, response
    except Exception as e:
        logger.error(f"Received Exception in sqs_delete_message {e}")
        return False

def sqs_send_message(sqs_client,queue_url,message):
    try:
        logger.info(f"Sending Message SQS URL: {queue_url}  Message : {json.dumps(message)}")
        response=sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
        logger.info(f"Send Message Response :  {json.dumps(response)}")
        if response['ResponseMetadata']['HTTPStatusCode']==200:
            return True,response
        else:
            return False, response
        return response
    except Exception as e:
        logger.error(f"Received Exception in sqs_send_message {e}")
        return False