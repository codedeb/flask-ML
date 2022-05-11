import logging
from pytz import utc
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

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
from ocr_wrapper_service.api_1_1.register_blueprint import create_flask_app


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
    logger.info('Error while starting scheduler!')
    logger.debug('Error while starting scheduler! %s' % e)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    logger.info('Starting Flask Server!')
    app.run(host=FlaskConstants.host, port=FlaskConstants.port, ssl_context=(FlaskConstants.cert_path,FlaskConstants.rsa_private_key_path))
