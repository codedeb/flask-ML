import json
import logging
from ocr_analytic_service.service.runner import main
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def process_images(input_images):
    # logger.info('data', input_images)
    logger.info('sending images to process')
    output = main(json.loads(input_images))
    return output

