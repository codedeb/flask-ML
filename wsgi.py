import os
import logging
from pytz import utc
import cProfile
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from ocr_wrapper_service.utils.s3_download_model import load_models
from ocr_wrapper_service.utils.sqs_consumer import receive_messages
from ocr_wrapper_service.app import create_app
from ocr_analytic_service.service.input_mod import read_input_and_form_output
from ocr_wrapper_service.constants import Logger_Constants
from ocr_wrapper_service.constants import Flask_Constants
from ocr_wrapper_service.constants import Scheduler_Constants
from ocr_wrapper_service.utils.base_logger import log_initializer
from ocr_wrapper_service.utils.base_logger import SkipScheduleFilter

"""
logging.basicConfig(filename="debugLogs.log", filemode='w', level=logging.INFO, format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
"""

logger=log_initializer()
my_filter=SkipScheduleFilter()
logging.getLogger("apscheduler.scheduler").addFilter(my_filter)

app = create_app(os.getenv('APP_SETTING_MODULE'))
modelLoadStatus = False

def sqs_scheduler():
    if(modelLoadStatus):
        logger.info('Requesting to receive messages...')
        receive_messages()
    else:
        logger.info('Could not recieve sqs messages until models are loaded!')
    
try:
    scheduler = BackgroundScheduler(timezone=utc,daemon=True)
    scheduler.add_job(func=sqs_scheduler, trigger=Scheduler_Constants.trigger, seconds=Scheduler_Constants.seconds)
    scheduler.start()
except Exception as e:
    logger.info('Error while starting scheduler!')
    logger.debug('Error while starting scheduler! %s' % e)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    # cProfile.run('main()')
    logger.info('Loading Models...')
    modelLoadStatus = load_models()
    logger.info('Starting app server!')
    app.run(host=Flask_Constants.host, port=Flask_Constants.port, ssl_context=(Flask_Constants.cert_path,Flask_Constants.rsa_private_key_path))
    # if(modelLoadStatus):
    #     logger.info('Starting app main!')
    #     app.run(host="0.0.0.0", port=8090, ssl_context=("platform/ssl/server.crt","platform/ssl/server.key"))
    # else:
    #     logger.info('Error while starting app!')

# gunicorn run_app:app
# gunicorn -c python:devops.gunicorn_sample_flask_app_config wsgi:app
# python wsgi.py
