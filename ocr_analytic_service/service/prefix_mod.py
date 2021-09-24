import os
from .model_artifacts import detector
from .inference_prefix import getPrefix
from .conf_band import confidence_band

import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)



def prefix_data_parser(imgobj):
    logger.info('Prefix predictor')

    config_path = "ocr_analytic_service/service/configPrefix_file.yaml"
    base_path = os.getenv("NAS_PATH")
    model_weight_path = os.path.join(base_path, "models/model_final_prefix.pth")
    # model_weight_path = "/opt/shared/data/cpl/idm/models/model_final_prefix.pth"
    # model_weight_path = r"/shared-volume/model_final_prefix.pth"
    logger.info('Prefix model path: %s' % model_weight_path)

    threshold = 0.1
    prediction = detector(config_path, model_weight_path, threshold)
    lbl, scr, lowChar, lowProb, scoreList = getPrefix(imgobj, prediction)
    conf, conf_band = confidence_band(scoreList, 4)
    prefix_out = {}
    prefix_out['ocrValue'] = lbl
    prefix_out['confValue'] = conf
    prefix_out['confBand'] = conf_band

    logger.info('Prefix model output: %s' % prefix_out)
    return prefix_out