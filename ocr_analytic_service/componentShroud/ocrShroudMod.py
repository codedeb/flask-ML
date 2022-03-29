import logging
from ocr_wrapper_service.constants import ModelDetails
from .inferenceShroud import getClassResults
from .modelArtifacts import detector

# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

import pandas as pd


logger = logging.getLogger(__name__)


class_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10:'A',  11: 'B', 12: 'C', 13: 'D', 14: 'E', 15:'F', 16: 'G', 17: 'H',18:'I',19:'J',  20: 'K', 21:'L',22: 'M', 23: 'N', 24:'O', 25: 'P', 26:'Q',27:'R',28:'S', 29: 'T', 30:'U', 31:'V', 32: 'W',33:'X',34:'Y',35:'Z'}

####Class_map dictionary of classes that are predicted
class_map_shroud = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10:'A',  11: 'B', 12: 'C', 13: 'D', 14: 'E', 15:'F', 16: 'G', 17: 'H',18:'I',19:'J',  20: 'K', 21:'L',22: 'M', 23: 'N', 24:'O', 25: 'P', 26:'Q',27:'R',28:'S', 29: 'T', 30:'U', 31:'V', 32: 'W',33:'X',34:'Y',35:'Z'}

def ocr_parser_shrouds(im, bboxes):
    try:
        ocr_shrouds_predictor = detector(ModelDetails.shroud_ocr_config_path, ModelDetails.shroud_ocr_model_path,ModelDetails.shroud_ocr_threshold)
        ocr_shrouds_outputs= ocr_shrouds_predictor(im)
        # cfg = get_cfg()
        # cfg.merge_from_file(ModelDetails.shroud_ocr_config_path)
        # cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = ModelDetails.shroud_ocr_threshold  # set threshold for this model
        # cfg.MODEL.DEVICE = "cpu"
        # cfg.MODEL.WEIGHTS = ModelDetails.shroud_ocr_model_path

        # predictor = DefaultPredictor(cfg)
        # # cn = list(class_map.values())
        # ocr_shrouds_outputs = predictor(im)  
        logger.info('Shrouds OCR Parser successfull!')
    except Exception as e:
        logger.info('Shrouds OCR Parser failure!')
        logger.info(e)
    
    try:
        #Extract the strings. Right now its 'SN'_'SEG'; it is hard coded into the result extraction
        resultString,confidence = getClassResults(class_map_shroud,bboxes,ocr_shrouds_outputs)
        out_obj = {}
        out_obj["ocrValue"] = resultString
        out_obj["confValue"] = confidence
        out_obj["confBand"] = "LOW"
        logger.info('Shrouds post processing success! %s' % out_obj)
    except Exception as e:
        logger.info('Shrouds post processing failure!')
        logger.info(e)

    return out_obj    