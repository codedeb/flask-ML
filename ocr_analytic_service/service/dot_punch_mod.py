import os
from logging import exception
import pickle
from .inference_dotPunched import Inference
from .model_artifacts import detector
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def dot_punched_data_parser(imgobj):
    # config_path = "ocr_analytic_service/service/configDotPunch_file.yaml"
    config_path = "ocr_analytic_service/service/configDotPunch_file_psn.yaml"

    base_path = os.getenv("NAS_PATH")
    model_weight_path = os.path.join(base_path, "models/model_final_dotpunch_psn.pth")
    # model_weight_path = "/opt/shared/data/cpl/idm/models/model_final_dotpunch.pth"
    # model_weight_path = r"/shared-volume/model_final_dotpunch.pth"
    logger.info('Dot punch model path: %s' % model_weight_path)

    threshold = 0.8
    file = open('ocr_analytic_service/service/listPickle', 'rb')
    data = pickle.load(file)
    prediction = detector(config_path, model_weight_path, threshold)
    try:
        str_ocr, conf, conf_band = Inference().output(data, prediction, imgobj)
        out_obj = {}
        out_obj['ocrValue'] = str_ocr
        out_obj['confValue'] = conf
        out_obj['confBand'] = conf_band
    except exception as e:
        logger.info('no data found: %s' % e)
    return out_obj
