import json
import logging
from analytic_service.input_mod import read_input_and_form_output
from wrapper_service.utils.sqs_sender import send_sqs_messages
"""
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
"""
logger = logging.getLogger(__name__)


def process_images(input):
    # logger.info('data', input_images)
    try:
        logger.info('Processing Images for analytics!')
        output = {'receipt_handle': input['receipt_handle']}
        output_messages = read_input_and_form_output(input['body'])
        output['body'] = output_messages
        logger.info('OCR output: %s' % output)
    except Exception as e:
        logger.info('Failed processing images!')
        logger.debug('Failed processing images! %s' % e)
    send_sqs_messages(output)
    return output

