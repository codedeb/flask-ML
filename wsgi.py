import os
import logging
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from ocr_wrapper_service.utils.s3_download_model import load_models
from ocr_wrapper_service.utils.sqs_consumer import receive_messages
from ocr_wrapper_service.app import create_app
from ocr_analytic_service.service.input_mod import read_input_and_form_output

logging.basicConfig(filename="debugLogs.log", filemode='w', level=logging.INFO, format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

app = create_app(os.getenv('APP_SETTING_MODULE'))
modelLoadStatus = False

def sqs_scheduler():
    if(modelLoadStatus):
        logger.info('Requesting to receive messages...')
        receive_messages()
    else:
        logger.info('Could not recieve sqs messages until models are loaded!')
    

scheduler = BackgroundScheduler(timezone=utc,daemon=True)
scheduler.add_job(func=sqs_scheduler, trigger="interval", seconds=60)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    logger.info('Loading Models...')
    modelLoadStatus = load_models()
    if(modelLoadStatus):
        logger.info('Starting app main!')
        app.run(host="0.0.0.0", port=5000, debug=False)
    else:
        logger.info('Error while starting app!')
    
    

# gunicorn run_app:app
# gunicorn -c python:devops.gunicorn_sample_flask_app_config wsgi:app
# python wsgi.py
