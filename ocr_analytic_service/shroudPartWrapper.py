import os
import json
import cv2
import time
import logging
import numpy as np
import matplotlib.pyplot as plt

from .componentShroud.segmentationModShroud import img_segmenter
from .componentShroud.inferenceShroudOcr import getShroudOcr
from .componentShroud.inferenceShroud import getClassResults

logger = logging.getLogger(__name__)

####Class_map dictionary of classes that are predicted
class_map_shroud = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10:'A',  11: 'B', 12: 'C', 13: 'D', 14: 'E', 15:'F', 16: 'G', 17: 'H',18:'I',19:'J',  20: 'K', 21:'L',22: 'M', 23: 'N', 24:'O', 25: 'P', 26:'Q',27:'R',28:'S', 29: 'T', 30:'U', 31:'V', 32: 'W',33:'X',34:'Y',35:'Z'}

def shroud_part_analytics(img_obj, im, filename):
    logger.info(f"Analytics Input: \n {img_obj}")
    
    try:
        logger.info("Input image: %s " % im)
        seg_out = img_segmenter(im)
        logger.info("Segment output: %s" % seg_out)
        
        logger.info('Shroud Segmentation successful!')
    except Exception as e:
        logger.info('Shroud Segmentation failure!')
        logger.info(e)
        seg_out = dict.fromkeys(["o_bb", "bl", "seg", "sn"])
        # seg_out["SEG"] = {"confBand": "LOW", "confValue": 0, "segment": im}
        # seg_out["PSN"] = {"confBand": "LOW", "confValue": 0, "segment": im}
        # seg_out["SN"] = {"confBand": "LOW", "confValue": 0, "segment": im}

    try:
        ###Output of the model that has the alphanums
        outputs = getShroudOcr(im)
        logger.info('Shrouds OCR Flow success! %s' % outputs)
    except Exception as e:
        logger.info('Shrouds OCR Flow failure!')
        logger.info(e)

    try:
        bboxes = []
        box1 = seg_out["sn"]["box"]
        bboxes.append(box1)
        box2 = seg_out["seg"]["box"]
        bboxes.append(box2)
        #Extract the strings. Right now its 'SN'_'SEG'; it is hard coded into the result extraction
        resultString,confidence = getClassResults(class_map_shroud,bboxes,outputs)
        logger.info('Shrouds post processing success! %s' % resultString)
    except Exception as e:
        logger.info('Shrouds post processing failure!')
        logger.info(e)


    
    # try:
        # ###Bounding boxes of the regions within which character strings need to be extracted
        # bboxes = []
        # if 'SN' in segDict[filename.upper()].keys():
        #     box1 = seg_out["SN"]['xmin'],seg_out["SN"]['ymin'],seg_out["SN"]['xmax'],seg_out["SN"]['SN']['ymax']
        # else:
        #     box1 = 0,0,0,0
        # bboxes.append(box1)
        # if 'SEG' in segDict[filename.upper()].keys():
        #     box1 = seg_out["SEG"]['xmin'],seg_out["SEG"]['ymin'],seg_out["SEG"]['xmax'],seg_out["SEG"]['ymax']
        # else:
        #     box1 = 0,0,0,0
        # bboxes.append(box1)

        # ###Output of the model that has the alphanums
        # outputs = predictor(im)

        # #Extract the strings. Right now its 'SN'_'SEG'; it is hard coded into the result extraction
        # resultString,confidence = getClassResults(class_map_shroud,bboxes,outputs)
        # logger.info("Shrouds output: %s" % resultString)
        # logger.info('Shrouds Flow successful!')
    # except Exception as e:
    #     logger.info('Shrouds Flow failure!')
    #     logger.info(e)
