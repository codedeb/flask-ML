import os
from .model_artifacts import detector
from . import inference_prefix
from .conf_band import confidence_band
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def prefix_data_parser(imgobj):
    logger.info('Prefix predictor')

    config_path = "ocr_analytic_service/service/configPrefix_file.yaml"
    base_path = os.getenv('MODEL_PATH')
    model_weight_path = os.path.join(base_path, "model/model_final_prefix.pth")
    logger.info('Prefix model path: %s' % model_weight_path)

    threshold = 0.1
    logger.info('Predicting: ')
    prediction = detector(config_path, model_weight_path, threshold)
    logger.info('Prefix prediction: %s' % prediction)
    inference_prefix.class_names = []
    lbl, scr, lowChar, lowProb, scoreList = inference_prefix.getPrefix(imgobj, prediction)
    logger.info('Prefix scores %s' % lbl)
    conf, conf_band = confidence_band(scoreList, 4)
    logger.info('Prefix conf %s' % conf)
    logger.info('Prefix conf band %s' % conf_band)
    prefix_out = {}
    prefix_out['ocrValue'] = lbl
    prefix_out['confValue'] = conf
    prefix_out['confBand'] = conf_band

    logger.info('Prefix model output: %s' % prefix_out)
    return prefix_out