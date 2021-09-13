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
    logger.info('Input dict for ROI Update: %s' % input_dict)
    out_put_dict = []
    try:
        logger.info('Starting for loop')
        # for img_obj in json.loads(input_dict):
        for img_obj in input_dict:
            logger.info('img obj input: %s' % img_obj)
            base_path = os.getenv("NAS_PATH")
            logger.info('Image path in plp: %s' % os.path.join(base_path, img_obj['imagePath']))
            fl_nm = os.path.join(base_path, img_obj['imagePath'])
            # fl_nm = img_obj["imagePath"]
            logger.info('file name: %s' % fl_nm)
            try:
                im = cv2.imread(fl_nm)
                logger.info('Input image: %s' % im)
                if im:
                    try:
                        seg_out = img_segmenter(im)
                        logger.info('Seg out: %s' % seg_out)
                    except:
                        logger.info('exception for seg_out')
                        seg_out = dict.fromkeys(["ROI", "PSN", "PR"])
                        seg_out["ROI"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                        seg_out["PSN"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                        seg_out["PR"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                    try:
                        psn_out = dot_punched_data_parser(seg_out['ROI']['segment'])
                        logger.info('psn out: %s' % psn_out)
                    except:
                        logger.info('exception for psn_out')
                        psn_out = {}
                        psn_out["ocrValue"] = "S_UNKN"
                        psn_out["confValue"] = 0.0
                        psn_out["confBand"] = "LOW"
                    try:
                        prefix_out = prefix_data_parser(im)
                        logger.info('prefix out: %s' % prefix_out)
                    except:
                        logger.info('exception for prefix_out')
                        prefix_out = {}
                        prefix_out["ocrValue"] = "P_UNKN"
                        prefix_out["confValue"] = 0.0
                        prefix_out["confBand"] = "LOW"
                
                    result_out = data_collector(seg_out, psn_out, prefix_out)
                    logger.info('data collector result: %s' % result_out)
                    final_obj = img_obj.copy()
                    final_obj["ocrValue"] = result_out["ocrValue"]
                    final_obj["ocrConfidenceValue"] = result_out["confValue"]
                    final_obj["ocrConfidenceBand"] = result_out["confBand"]
                    final_obj["ocrAdditional"] = ""
                    out_put_dict.append(final_obj)
                else:
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
        logger.info('Output dict: %s' % out_put_dict)
        return out_put_dict
    except:
        logger.info('No item found')

    return out_put_dict


# input_dict = [{"imageId": 1, "imageOcrType": "PARTDRAWINGNUMBER", "imagePath": "./Raw_S1B_297719_dot_punched_IMG_2025.JPG",
#                "positionNumber": 2, "componentId": 1234, "componentName": "S1B"}]
# print(read_input_and_form_output(input_dict))
