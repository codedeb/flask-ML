import logging
from pytz import utc
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from wrapper_service.constants import FlaskConstants
from wrapper_service.constants import SchedulerConstants
from wrapper_service.constants import S3Constants
from wrapper_service.utils.base_logger import log_initializer
from wrapper_service.utils.base_logger import SkipScheduleFilter
from wrapper_service.utils.aws_services import s3_client
from wrapper_service.utils.aws_services import sqs_client
from wrapper_service.utils.aws_services import s3_resource
from wrapper_service.utils.image_processor import wrapper_service
from wrapper_service.utils.aws_services import s3_model_download
from wrapper_service.api_1_1.register_blueprint import create_flask_app

# from ocr_analytic_service.input_mod import read_input_and_form_output


"""
logging.basicConfig(filename="debugLogs.log", filemode='w', level=logging.INFO, format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
"""

logger=log_initializer()
my_filter=SkipScheduleFilter()
logging.getLogger("apscheduler.scheduler").addFilter(my_filter)

app = create_flask_app()
global modelLoadStatus
modelLoadStatus = False

s3_client_object=s3_client()
sqs_client_object=sqs_client()
s3_resource_object=s3_resource()

# Local system testing setup
# try:
#     # Folder Path
#     path = "/ocr_data/shroud_models/images/"
#     # iterate through all file
#     for file in os.listdir(path):
#         # Check whether file is in text format or not
#         if file.endswith(".JPG"):
#             file_path = os.path.join(path, file)
#             image_object = [{"imageId":1,"partDataType":"PARTSERIALNUMBER","partType":"BLADES","positionNumber":2,"componentId":9,"componentName":"Comp1","imagePath": file_path}]
#             logger.info('calling read function on image obj: %s' % image_object)
#             # call analytics function
#             read_input_and_form_output(s3_resource_object,image_object)
#         else:
#             logger.info('Image is not JPG! %s' % file)
# except Exception as e:
#     logger.info('Error while starting analytics! %s' % e)

def sqs_scheduler():
    global modelLoadStatus
    if modelLoadStatus:
        logger.info("Inside Scheduler Function")
        wrapper_service(sqs_client_object,s3_resource_object)
    else:
        logger.info("Downloading models from S3")
        modelLoadStatus = s3_model_download(s3_client_object)
        #sleep if models are not available
        if not modelLoadStatus:
            logger.info(f"Models are not available in sleep for : {S3Constants.retry_sleep} seconds")
            sleep(S3Constants.retry_sleep)
    
try:
    scheduler = BackgroundScheduler(timezone=utc,daemon=True)
    scheduler.add_job(func=sqs_scheduler, trigger=SchedulerConstants.trigger, seconds=SchedulerConstants.seconds)
    scheduler.start()
except Exception as e:
    # logger.info('Error while starting scheduler!')
    logger.error('Error while starting scheduler! %s' % e)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    logger.info('Starting Flask Server!')
    app.run(host=FlaskConstants.host, port=FlaskConstants.port, ssl_context=(FlaskConstants.cert_path,FlaskConstants.rsa_private_key_path))
