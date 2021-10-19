import os
import json
import cv2
from .segmentation_mod import img_segmenter
from .dot_punch_mod import dot_punched_data_parser
from .collector import data_collector
from .prefix_mod import prefix_data_parser
import time
from typing import List
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def read_input_and_form_output(input_dict):
    logger.info('Input for analytics: %s' % input_dict)
    out_put_dict = []
    try:
        # local testing
        # for img_obj in json.loads(input_dict): 
        for img_obj in input_dict:
            base_path = os.getenv("NAS_PATH")
            fl_nm = os.path.join(base_path, img_obj['imagePath'])
            logger.info('File: %s' % fl_nm)
            try:
                im = cv2.imread(fl_nm)
                # logger.info('Input image: %s' % im)
                if im is not None:
                    try:
                        seg_out = img_segmenter(im)
                        logger.info('Segmented successfully!')
                    except:
                        logger.info('Exception occurred while segmentation!')
                        seg_out = dict.fromkeys(["ROI", "PSN", "PR"])
                        seg_out["ROI"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                        seg_out["PSN"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                        seg_out["PR"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                    try:
                        psn_out = dot_punched_data_parser(seg_out['ROI']['segment'])
                        logger.info('psn out: %s' % psn_out)
                    except:
                        logger.info('Exception occurred while parsing PSN!')
                        psn_out = {}
                        psn_out["ocrValue"] = "S_UNKN"
                        psn_out["confValue"] = 0.0
                        psn_out["confBand"] = "LOW"
                    try:
                        prefix_out = prefix_data_parser(seg_out['ROI']['segment'])
                        logger.info('prefix out: %s' % prefix_out)
                    except:
                        logger.info('Exception occurred while parsing prefix!')
                        prefix_out = {}
                        prefix_out["ocrValue"] = "P_UNKN"
                        prefix_out["confValue"] = 0.0
                        prefix_out["confBand"] = "LOW"
                
                    result_out = data_collector(seg_out, psn_out, prefix_out)
                    final_obj = img_obj.copy()
                    final_obj["ocrValue"] = result_out["ocrValue"]
                    final_obj["ocrConfidenceValue"] = result_out["confValue"]
                    final_obj["ocrConfidenceBand"] = result_out["confBand"]
                    final_obj["ocrAdditional"] = ""
                    out_put_dict.append(final_obj)
                else:
                    logger.info('Failed to read image!')
                    final_obj = img_obj.copy()
                    final_obj["ocrValue"] = "IMG_NOT_FOUND"
                    final_obj["ocrConfidenceValue"] = 0.0
                    final_obj["ocrConfidenceBand"] = "LOW"
                    final_obj["ocrAdditional"] = "Failed to read image"
                    out_put_dict.append(final_obj)
            except:
                logger.info('OCR Failed')
                final_obj = img_obj.copy()
                final_obj["ocrValue"] = "FAILED"
                final_obj["ocrConfidenceValue"] = 0.0
                final_obj["ocrConfidenceBand"] = "LOW"
                final_obj["ocrAdditional"] = "OCR Failed"
                out_put_dict.append(final_obj)
        return out_put_dict
    except:
        logger.info('No item found')

    return out_put_dict
