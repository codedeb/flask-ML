from ocr_wrapper_service.constants import ModelDetails
from .inferenceShroud import getClassResults
import traceback

# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

import cv2
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

modelToUse = ModelDetails.shroud_model_path
configToUse = ModelDetails.shroud_config_path

class_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10:'A',  11: 'B', 12: 'C', 13: 'D', 14: 'E', 15:'F', 16: 'G', 17: 'H',18:'I',19:'J',  20: 'K', 21:'L',22: 'M', 23: 'N', 24:'O', 25: 'P', 26:'Q',27:'R',28:'S', 29: 'T', 30:'U', 31:'V', 32: 'W',33:'X',34:'Y',35:'Z'}

####Class_map dictionary of classes that are predicted
class_map_shroud = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10:'A',  11: 'B', 12: 'C', 13: 'D', 14: 'E', 15:'F', 16: 'G', 17: 'H',18:'I',19:'J',  20: 'K', 21:'L',22: 'M', 23: 'N', 24:'O', 25: 'P', 26:'Q',27:'R',28:'S', 29: 'T', 30:'U', 31:'V', 32: 'W',33:'X',34:'Y',35:'Z'}

def getShroudOcr(im, bboxes):
    # Create config
    cfg = get_cfg()
    cfg.merge_from_file(configToUse)

    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.1  # set threshold for this model
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.WEIGHTS = modelToUse

    predictor = DefaultPredictor(cfg)
   
    cn = list(class_map.values())

    outputs = predictor(im)
    
    try:
        #Extract the strings. Right now its 'SN'_'SEG'; it is hard coded into the result extraction
        resultString,confidence = getClassResults(class_map_shroud,bboxes,outputs)
        logger.info('Shrouds post processing success resultString! %s' % resultString)
        logger.info('Shrouds post processing success confidence! %s' % confidence)
    except Exception as e:
        logger.info('Shrouds post processing failure!')
        logger.info(traceback.format_exc())
        logger.info(e)

    return outputs    