import os
from .model_artifacts import detector
# from .inference_prefix import getPrefix
from . import inference_prefix
from .conf_band import confidence_band
from . import recoverPrefix

import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)



def prefix_data_parser(imgobj):
    config_path = "ocr_analytic_service/service/configPrefix_file.yaml"
    base_path = os.getenv("NAS_PATH")
    model_weight_path = os.path.join(base_path, "models/model_final_prefix.pth")
    # model_weight_path = "/opt/shared/data/cpl/idm/models/model_final_prefix.pth"
    # model_weight_path = r"/shared-volume/model_final_prefix.pth"
    logger.info('Prefix model path: %s' % model_weight_path)

    threshold = 0.1
    try:
        prediction = detector(config_path, model_weight_path, threshold)
        inference_prefix.class_names = []
        lbl, scr, lowChar, lowProb, scoreList = inference_prefix.getPrefix(imgobj, prediction)
        logger.info('Prefix Initial output %s' % lbl)
        conf, conf_band = confidence_band(scoreList, 4)
        if lbl == None:
            logger.info('Prefix region not found!')
        else:
            correctPrefix, probDist = recoverPrefix.getCorrectPrfix(lbl)
            logger.info('Prefix Correct output: %s' % correctPrefix)
        prefix_out = {}
        prefix_out['ocrValue'] = lbl
        prefix_out['confValue'] = conf
        prefix_out['confBand'] = conf_band

        logger.info('Prefix model output: %s' % prefix_out)
    except Exception as e:
        logger.info('Prefix model exception: %s' % e)
    return prefix_out