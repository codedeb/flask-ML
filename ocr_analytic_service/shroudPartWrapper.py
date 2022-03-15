import os
import json
import cv2
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)

####Class_map dictionary of classes that are predicted
class_map_shroud = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10:'A',  11: 'B', 12: 'C', 13: 'D', 14: 'E', 15:'F', 16: 'G', 17: 'H',18:'I',19:'J',  20: 'K', 21:'L',22: 'M', 23: 'N', 24:'O', 25: 'P', 26:'Q',27:'R',28:'S', 29: 'T', 30:'U', 31:'V', 32: 'W',33:'X',34:'Y',35:'Z'}

def shroud_part_analytics(img_obj, im, filename):
    logger.info(f"Analytics Input: \n {img_obj}")
    ####Bounding boxes of the regions within which character strings need to be extracted
    bboxes = []
    if 'SN' in segDict[filename.upper()].keys():
        box1 = segDict[filename.upper()]['SN']['xmin'],segDict[filename.upper()]['SN']['ymin'],\
    segDict[filename.upper()]['SN']['xmax'],segDict[filename.upper()]['SN']['ymax']
    else:
        box1 = 0,0,0,0
    bboxes.append(box1)
    if 'SEG' in segDict[filename.upper()].keys():
        box1 = segDict[filename.upper()]['SEG']['xmin'],segDict[filename.upper()]['SEG']['ymin'],\
    segDict[filename.upper()]['SEG']['xmax'],segDict[filename.upper()]['SEG']['ymax']
    else:
        box1 = 0,0,0,0
    bboxes.append(box1)

    ####Output of the model that has the alphanums
    outputs = predictor(im)


    ###Extract the strings. Right now its 'SN'_'SEG'; it is hard coded into the result extraction
    resultString,confidence = getClassResults(class_map_shroud,bboxes,outputs)