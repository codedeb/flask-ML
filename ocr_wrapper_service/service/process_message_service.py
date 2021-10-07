from ocr_wrapper_service.service.analytic_service import process_images
from ocr_wrapper_service.utils.sqs_sender import send_sqs_messages

import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def process_messages(input_dct):
    output = process_images(input_dct)
    # logger.info('Local testing ouput: %s' % output)
    send_sqs_messages(output)
    return output




