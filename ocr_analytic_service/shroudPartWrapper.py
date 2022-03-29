import json
import logging
import json
import numpy as np
import traceback
from .componentShroud.segmentationModShroud import img_segmenter_shrouds
from .componentShroud.ocrShroudMod import ocr_parser_shrouds
logger = logging.getLogger(__name__)


def shroud_part_analytics(img_obj, im, filename):
    logger.info(f"Shrouds Analytics Input: {img_obj}")
    with open('/ocr-wrapper-service/ocr_analytic_service/model_params.json') as file:
        model_params = json.load(file)
    
    try:
        seg_out = img_segmenter_shrouds(im, model_params)
        logger.info('Shroud Segmentation successful! %s' % seg_out)
        logger.debug('Shroud Segmentation successful! %s' % seg_out)
    except Exception as e:
        logger.info('Shroud Segmentation failure!')
        logger.info(e)
        seg_out = dict.fromkeys(["O_BB", "SN", "SEG"])
        seg_out["O_BB"] = {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}
        seg_out["SN"] = {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}
        seg_out["SEG"] =  {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}

    ocr_parser_out = {}
    try:
        bbox = []
        bbox.append( seg_out["SN"]["box"])
        bbox.append( seg_out["SEG"]["box"])
        ###Output of the model that has the alphanums
        ocr_parser_out = ocr_parser_shrouds(seg_out["O_BB"]["segment"], bbox)
        logger.info('Shrouds OCR Flow success! %s' % ocr_parser_out)
    except Exception as e:
        logger.info('Shrouds OCR Flow failure!')
        logger.info(e)
        ocr_parser_out["ocrValue"] = "OCR_UNKN"
        ocr_parser_out["confValue"] = 0.0
        ocr_parser_out["confBand"] = "LOW"
        # logger.info(traceback.format_exc())
