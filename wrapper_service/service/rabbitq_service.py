import json
import os

import pika
import logging
from wrapper_service.service.analytic_service import process_images as process
"""
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
"""
logger = logging.getLogger(__name__)


def send_messages(output):
    try:
        logger.info('Sending output to queue!')
        hostname = os.environ['RABBITMQ_HOST_NAME']
        port = os.environ['RABBITMQ_HOST_PORT']
        username = os.environ['RABBITMQ_USERNAME']
        password = os.environ['RABBITMQ_PASSWORD']
        output_queue = os.environ['RABBITMQ_OUTPUT_QUEUE']
        exchange = os.environ['RABBITMQ_EXCHANGE']
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port,
                                                                    credentials=pika.credentials.PlainCredentials(
                                                                        username, password)))
        channel = connection.channel()

        channel.queue_declare(queue=output_queue, durable=True)
        logger.info("Ouptut: %s" % output)

        channel.basic_publish(exchange=exchange, routing_key=output_queue, body=json.dumps(output),
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # make message persistent
                            ))
        logger.info(" [x] Sent Output to Queue")
        connection.close()
    except Exception as e:
        logger.info("Exceptions for output queue: %s" % e)
        connection.close()
        pass
    return True                                           
            
def process_messages():
    hostname = os.environ['RABBITMQ_HOST_NAME']
    port = os.environ['RABBITMQ_HOST_PORT']
    username = os.environ['RABBITMQ_USERNAME']
    password = os.environ['RABBITMQ_PASSWORD']
    input_queue = os.environ['RABBITMQ_INPUT_QUEUE']
    try:
        logger.info("Checking Connection:")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port,
                                                                        credentials=pika.credentials.PlainCredentials(
                                                                            username, password)))
        logger.info('Connected to rabbitmq successfully!') 
        channel = connection.channel() 

    except pika.exceptions.AMQPHeartbeatTimeout:
        logger.info("Connection dropped!")

    except Exception as e:
        logger.info("Connection not present!")

    channel.queue_declare(queue=input_queue, durable=True)
    logger.info(' [*] Waiting for messages.')

    def callback(ch, method, properties, body):
        logger.info(" [x] Received %r" % body)
        input_messages = body.decode('utf8')
        output_messages = process(input_messages)
        # if len(output_messages) > 0:
        #     logger.info('length > 0')
        send_messages(output_messages)
        connection.close()

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=input_queue, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    

