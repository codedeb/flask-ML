import pika
import os
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def rabbitqConnection(queue_connect):
    hostname = os.environ['RABBITMQ_HOST_NAME']
    port = os.environ['RABBITMQ_HOST_PORT']
    username = os.environ['RABBITMQ_USERNAME']
    password = os.environ['RABBITMQ_PASSWORD']
    input_queue = os.environ['RABBITMQ_INPUT_QUEUE']
   
    queue_connect = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port,
                                                                    credentials=pika.credentials.PlainCredentials(
                                                                        username, password)))
    logger.info('Connected to rabbitmq successfully!')                                                                   
    return queue_connect