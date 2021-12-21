import json
import boto3
import logging
import os

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info('Connecting to s3...')
    s3 = boto3.client('s3', region_name=os.getenv('REGION'))
except:
    logger.error('Connecting with s3 with access credentials...')
    s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), aws_session_token=os.getenv('AWS_SESSION_TOKEN'), region_name=os.getenv('REGION'))
    pass

def load_models():
    try:
        logger.info('Connecting to s3...')
        logger.debug('Listing objects for bucket: %s' % os.getenv('BUCKET_NAME'))
        # Retrieve the objects deom specific IDM model folder
        objects = s3.list_objects(Bucket=os.getenv('BUCKET_NAME'), MaxKeys=10, Prefix='IDM/model/ocr_model_psn_v1.0.0/model')
        logger.debug('S3 objects: %s' % objects)

        # Path where model will be downloaded
        base_path = os.getenv('MODEL_PATH')
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
            s3.download_file(os.getenv('BUCKET_NAME'), object['Key'], modelDownloaded)
        return True
    except Exception as e:
        logger.info('Error while loading models from s3!')
        logger.debug('Error while loading models from s3! %s' % e)
        return False
