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
    # s3 = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), aws_session_token=os.getenv('AWS_SESSION_TOKEN'), region_name=os.getenv('REGION'))
    pass

def load_models():
    try:
        logger.info('Connecting to s3...')
        
        logger.info('Listing objects for bucket: %s' % os.getenv('BUCKET_NAME'))
        # Retrieve the objects deom specific IDM model folder
        objects = s3.list_objects(Bucket=os.getenv('BUCKET_NAME'), MaxKeys=10, Prefix='IDM/model/model')
        logger.info('S3 objects: %s' % objects)

        # Path where model will be downloaded
        base_path = os.getenv('MODEL_PATH')
        model_path = os.path.join(base_path, 'model')
        logger.info('model_path: %s' %  model_path)

        # downloading files 
        for object in objects['Contents']:
            logger.info('s3 object: %s' %  object)
            path, filename = os.path.split(object['Key'])
            logger.info('file to be downloaded: %s' %  filename)
            # Create directory if doesnt exist
            os.makedirs(model_path, exist_ok=True)
            modelDownloaded = os.path.join(model_path, filename)
            logger.info('file to be donloaded as: %s' %  modelDownloaded)
            # Download file
            s3.download_file(os.getenv('BUCKET_NAME'), object['Key'], modelDownloaded)
        return True
    except:
        logger.error('Error while loading models from s3!')
        return False