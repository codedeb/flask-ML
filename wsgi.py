import os
import logging
from pytz import utc
import cProfile
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
#from ocr_wrapper_service.utils.s3_download_model import load_models
#from ocr_wrapper_service.utils.sqs_consumer import receive_messages
#from ocr_wrapper_service.app import create_app
from ocr_analytic_service.input_mod import read_input_and_form_output
from ocr_wrapper_service.constants import LoggerConstants
from ocr_wrapper_service.constants import FlaskConstants
from ocr_wrapper_service.constants import SchedulerConstants
from ocr_wrapper_service.constants import S3Constants
from ocr_wrapper_service.utils.base_logger import log_initializer
from ocr_wrapper_service.utils.base_logger import SkipScheduleFilter
from ocr_wrapper_service.utils.aws_services import s3_client
from ocr_wrapper_service.utils.aws_services import sqs_client
from ocr_wrapper_service.utils.aws_services import s3_resource
from ocr_wrapper_service.utils.image_processor import wrapper_service
from ocr_wrapper_service.utils.aws_services import s3_model_download
# from ocr_wrapper_service.utils.s3_download_model import s3_model_download
from ocr_wrapper_service.utils.image_processor import load_predictors
from time import sleep
from ocr_wrapper_service.api_1_1.register_blueprint import create_flask_app


"""
logging.basicConfig(filename="debugLogs.log", filemode='w', level=logging.INFO, format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
"""

logger=log_initializer()
my_filter=SkipScheduleFilter()
logging.getLogger("apscheduler.scheduler").addFilter(my_filter)

#app = create_app(os.getenv('APP_SETTING_MODULE'))
app = create_flask_app()
global modelLoadStatus
modelLoadStatus = False

s3_client_object=s3_client()
sqs_client_object=sqs_client()
s3_resource_object=s3_resource()

# Local system testing setup
try:
    # Folder Path
    path = "/shared-volume/ocr_data/images/"
    # iterate through all file
    for file in os.listdir(path):
        # Check whether file is in text format or not
        if file.endswith(".JPG"):
            file_path = os.path.join(path, file)
            image_object = [{"imageId":1,"partDataType":"PARTSERIALNUMBER","partType":"BLADES","positionNumber":2,"componentId":9,"componentName":"Comp1","imagePath": file_path}]
            logger.info('calling read function on image obj: %s' % image_object)
            # call analytics function
            read_input_and_form_output(s3_resource_object,image_object)
        else:
            logger.info('Image is not JPG! %s' % file)
except Exception as e:
    logger.info('Error while starting analytics! %s' % e)

# def sqs_scheduler():
#     global modelLoadStatus
#     if modelLoadStatus:
#         #logger.info('Requesting to receive messages...')
#         #receive_messages()
#         logger.info("Inside Scheduler Function")
#         wrapper_service(sqs_client_object,s3_resource_object)
#     else:
#         logger.info("Downloading models from S3")
#         modelLoadStatus = s3_model_download(s3_client_object)
#         #sleep if models are not available
#         if not modelLoadStatus:
#             logger.info(f"Models are not available in sleep for : {S3Constants.retry_sleep} seconds")
#             sleep(S3Constants.retry_sleep)
    
# try:
#     scheduler = BackgroundScheduler(timezone=utc,daemon=True)
#     scheduler.add_job(func=sqs_scheduler, trigger=SchedulerConstants.trigger, seconds=SchedulerConstants.seconds)
#     scheduler.start()
# except Exception as e:
#     logger.info('Error while starting scheduler!')
#     logger.debug('Error while starting scheduler! %s' % e)

# Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    # cProfile.run('main()')
    #logger.info('Loading Models...')
    #modelLoadStatus = load_models()
    logger.info('Starting Flask Server!')
    app.run(host=FlaskConstants.host, port=FlaskConstants.port, ssl_context=(FlaskConstants.cert_path,FlaskConstants.rsa_private_key_path))
    # if(modelLoadStatus):
    #     logger.info('Starting app main!')
    #     app.run(host="0.0.0.0", port=8090, ssl_context=("platform/ssl/server.crt","platform/ssl/server.key"))
    # else:
    #     logger.info('Error while starting app!')

# gunicorn run_app:app
# gunicorn -c python:devops.gunicorn_sample_flask_app_config wsgi:app
# python wsgi.py
