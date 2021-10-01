import os
import logging
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from ocr_wrapper_service.utils.sqs_consumer import receive_messages
from ocr_wrapper_service.app import create_app

logging.basicConfig(filename="debugLogs.log", filemode='w', level=logging.INFO, format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)
app = create_app(os.getenv('APP_SETTING_MODULE'))

for k, v in sorted(os.environ.items()):
    print(k+':', v)

def sqs_scheduler():
    logger.info('Requesting to receive messages...')
    receive_messages()


scheduler = BackgroundScheduler(timezone=utc,daemon=True)
scheduler.add_job(func=sqs_scheduler, trigger="interval", seconds=30)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    logger.info('Starting app main...')
    app.run(host="0.0.0.0", port=8090, ssl_context=("platform/ssl/server.crt","platform/ssl/server.key"))

# gunicorn run_app:app
# gunicorn -c python:devops.gunicorn_sample_flask_app_config wsgi:app
# python wsgi.py
