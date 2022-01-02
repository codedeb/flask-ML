import boto3
import logging
import json
from ocr_wrapper_service.constants import S3Constants
from ocr_wrapper_service.constants import SQSConstants
from ocr_wrapper_service.constants import LocalDirectoryConstants

logger = logging.getLogger(__name__)

def s3_client():
    try:
        logger.info('Connecting to s3...')
        s3 = boto3.client('s3', region_name=os.getenv('REGION'))
    except:
        logger.error('Connecting with s3 with access credentials...')
        s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), aws_session_token=os.getenv('AWS_SESSION_TOKEN'), region_name=os.getenv('REGION'))
        pass
    return s3

def sqs_client():
    try:
        logger.info('Connecting to SQS consumer...')
        sqs_client = boto3.client('sqs', region_name=os.getenv('REGION'))
    except:
        logger.error('Error while connecting to SQS for consuming msgs!')
        sqs_client = boto3.client('sqs', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                  region_name=os.getenv('REGION'))
        pass
    return sqs_client

def s3_model_download(s3):
    try:
        logger.debug('Listing objects for bucket: %s' % S3Constants.bucket_name)
        # Retrieve the objects deom specific IDM model folder
        logger.info(f"Listing Objects from Bucket : {S3Constants.bucket_name} and Path : {S3Constants.model_path}")
        objects = s3.list_objects(Bucket=S3Constants.bucket_name, MaxKeys=10, Prefix=S3Constants.model_path)
        logger.debug('S3 objects: %s' % objects)

        # Path where model will be downloaded
        base_path = LocalDirectoryConstants.model_path
        model_path = os.path.join(base_path, 'model')
        logger.debug('model_path: %s' %  model_path)

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
        logger.info('Error while loading models from s3! %s' % e)
        logger.debug('Error while loading models from s3! %s' % e)
        return False