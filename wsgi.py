import os
import threading
import time
import logging

import requests

from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
import atexit


from ocr_wrapper_service.app import create_app
# from flask_rabmq import RabbitMQ
from ocr_wrapper_service.service.rabbitq_service import process_messages
# ramq = RabbitMQ()

logging.basicConfig(filename="debugLogs.log", filemode='w', level=logging.INFO, format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
app = create_app(os.getenv('APP_SETTING_MODULE'))
# ramq.init_app(app=app)


# @ramq.queue(exchange_name='idm.exchange', routing_key='idm_ocr_input_queue',
#             queue_name='idm_ocr_input_queue', exchange_type='direct')
# def idm_ocr_input_queue(body):
#     print(body)
#     return True

@app.before_first_request
def activate_job():
    def run_job():
        logger.info("Run recurring task")
        process_messages()
    thread = threading.Thread(target=run_job)
    thread.start()

def sqs_scheduler():
    print('Requesting to receive messages')
    process_messages()

scheduler = BackgroundScheduler(timezone=utc,daemon=True)
scheduler.add_job(func=sqs_scheduler, trigger="interval", seconds=30)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            logger.info('In start loop')
            try:
                r = requests.get('http://127.0.0.1:5000/')
                if r.status_code == 200:
                    logger.info('Server started, quiting start_loop')
                    not_started = False
                logger.info(r.status_code)

            except:
                logger.info('Server not yet started')
            time.sleep(2)

    logger.info('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


if __name__  == "__main__":
    # ramq.run_consumer()
    start_runner()
    app.run(host="0.0.0.0", port=5000, debug=False)

# gunicorn run_app:app
# gunicorn -c python:devops.gunicorn_sample_flask_app_config wsgi:app
# python wsgi.py
# curl -i localhost:5000/
# curl -i localhost:5000/get
# curl -X POST localhost:5000/post
# ps -ef | grep python
# chmod 755 python_build.sh