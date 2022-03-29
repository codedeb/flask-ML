import os
import json
import cv2
import time
import logging
import json
import numpy as np
import matplotlib.pyplot as plt

from .componentShroud.segmentationModShroud import img_segmenter_shrouds
from .componentShroud.inferenceShroudOcr import getShroudOcr

logger = logging.getLogger(__name__)


def shroud_part_analytics(img_obj, im, filename):
    logger.info(f"Analytics Input: \n {img_obj}")
    with open('/ocr-wrapper-service/ocr_analytic_service/model_params.json') as file:
        model_params = json.load(file)
    
    try:
        logger.info("Input image: %s " % im)
        seg_out = img_segmenter_shrouds(im, model_params)
        logger.info("Segment output: %s" % seg_out)
        logger.info('Shroud Segmentation successful!')
    except Exception as e:
        logger.info('Shroud Segmentation failure!')
        logger.info(e)
        seg_out = dict.fromkeys(["o_bb", "seg", "sn"])
        # seg_out["SEG"] = {"confBand": "LOW", "confValue": 0, "segment": im}
        # seg_out["PSN"] = {"confBand": "LOW", "confValue": 0, "segment": im}
        # seg_out["SN"] = {"confBand": "LOW", "confValue": 0, "segment": im}

    try:
        bbox = []
        bbox.append( seg_out["SN"]["box"])
        bbox.append( seg_out["SEG"]["box"])
        ###Output of the model that has the alphanums
        outputs = getShroudOcr(seg_out["O_BB"]["segment"], bbox)
        # outputs = getShroudOcr(im, bboxes)
        logger.info('Shrouds OCR Flow success! %s' % outputs)
    except Exception as e:
        logger.info('Shrouds OCR Flow failure!')
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
