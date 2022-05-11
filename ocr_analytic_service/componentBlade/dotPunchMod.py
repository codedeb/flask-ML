import os
from logging import exception
import pickle
from .inferenceDotPunched import Inference
from .modelArtifacts import detector
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



def dot_punched_data_parser(imgobj, psn_box, exp_len=6, mdl_opt=1):
    global dot_punch_predictor
    global dot_punch_predictor_available
    
    if mdl_opt == 2:
        config_path = ModelDetails.dot_punch_config_path_alt
        model_weight_path = ModelDetails.dot_punch_model_path_alt
    else:
        config_path = ModelDetails.dot_punch_config_path_main
        model_weight_path = ModelDetails.dot_punch_model_path_main
    
    # file = open('ocr_analytic_service/service/listPickle', 'rb')
    # data = pickle.load(file)
    data = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C',
            'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    #prediction = detector(config_path, model_weight_path, threshold)
    # uncomment if condition and enable global variables when model needs to be initialized only once
    if not dot_punch_predictor_available:
        logger.info("Initializing Dot Punch Predictor")
        dot_punch_predictor = detector(config_path, model_weight_path, ModelDetails.dot_punch_threshold)
        dot_punch_predictor_available=True
    try:
        str_ocr, conf, conf_band = Inference().output(data, dot_punch_predictor, imgobj, psn_box, exp_len)
        out_obj = {}
        out_obj['ocrValue'] = str_ocr
        out_obj['confValue'] = conf
        out_obj['confBand'] = conf_band
    except Exception as e:
        logger.info('no data found: %s' % e)
    return out_obj