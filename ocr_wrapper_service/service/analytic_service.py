import json
import logging
from ocr_analytic_service.service.input_mod import read_input_and_form_output
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def process_images(input_images):
    try:
        logger.info('Processing Images for analytics')
        output = read_input_and_form_output(json.loads(input_images))
        logger.info('Analytic output: %s' % output)
    except Exception as e:
        logger.error('Failed while process images : %s' % e)
    return output