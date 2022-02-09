import os
from logging import exception
import pickle
from .inference_dotPunched import Inference
from .model_artifacts import detector
import logging
from ocr_wrapper_service.constants import ModelDetails


global dot_punch_predictor
global dot_punch_predictor_available
dot_punch_predictor_available=False

"""
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
"""
logger = logging.getLogger(__name__)



def dot_punched_data_parser(imgobj):
    #global dot_punch_predictor
    #global dot_punch_predictor_available
    # config_path = "ocr_analytic_service/service/configDotPunch_file.yaml"
    config_path = "ocr_analytic_service/service/configDotPunch_file_psn.yaml"

    base_path = os.getenv('MODEL_PATH')
    model_weight_path = os.path.join(base_path, "model/model_dotpunch_v1.1.0.pth")
    # model_weight_path = r"/shared-volume/model_final_dotpunch.pth"

    threshold = 0.8
    file = open('ocr_analytic_service/service/listPickle', 'rb')
    data = pickle.load(file)
    #prediction = detector(config_path, model_weight_path, threshold)
    # uncomment if condition and enable global variables when model needs to be initialized only once
    if not dot_punch_predictor_available:
        logger.info("Initializing Dot Punch Predictor")
        dot_punch_predictor = detector(ModelDetails.dot_punch_config_path, ModelDetails.dot_punch_model_path,ModelDetails.dot_punch_threshold)
        dot_punch_predictor_available=True
    try:
        str_ocr, conf, conf_band = Inference().output(data, dot_punch_predictor, imgobj)
        out_obj = {}
        out_obj['ocrValue'] = str_ocr
        out_obj['confValue'] = conf
        out_obj['confBand'] = conf_band
    except Exception as e:
        logger.info('no data found: %s' % e)
    return out_obj