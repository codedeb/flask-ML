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


def read_input_and_form_output(input_dict: list('dict_obj')) -> list('dict_obj'):
    logger.info('Input dict for ROI Update: %s' % input_dict)
    out_put_dict = []
    try:
        for img_obj in json.loads(input_dict):
            logger.info(img_obj)
            #base_path = os.getenv("NAS_PATH")
            # fl_nm = os.path.join(base_path, img_obj['imagePath'])
            fl_nm = img_obj["imagePath"]
            logger.info('file name: %s' % fl_nm)
            try:
                im = cv2.imread(fl_nm, cv2.IMREAD_UNCHANGED)
                seg_out = img_segmenter(im)
                try:
                    psn_out = dot_punched_data_parser(
                        seg_out['ROI']['segment'])
                except:
                    psn_out = {}
                    psn_out['ocr_value'] = None
                    psn_out['conf_value'] = 0
                    psn_out['conf_band'] = 'LOW'
                try:
                    prefix_out = prefix_data_parser(im)
                except:
                    prefix_out = {}
                    prefix_out["ocr_value"] = None
                    prefix_out["conf_value"] = 0
                    prefix_out["conf_band"] = "LOW"
                result_out = data_collector(seg_out, psn_out, prefix_out)
                final_obj = img_obj.copy()
                final_obj['ocr_value'] = result_out['ocrValue']
                final_obj['conf_value'] = result_out['confValue']
                final_obj['conf_band'] = result_out['confBand']
                out_put_dict.append(final_obj)
            except:
                final_obj = img_obj.copy()
                final_obj['ocr_value'] = None
                final_obj['conf_value'] = 0
                final_obj['conf_band'] = 'LOW'
                out_put_dict.append(final_obj)
        return out_put_dict
    except:
        logger.info('No item found')

    return out_put_dict


# input_dict = [{"imageId": 1, "imageOcrType": "PARTDRAWINGNUMBER", "imagePath": "./Raw_S1B_297719_dot_punched_IMG_2025.JPG",
#                "positionNumber": 2, "componentId": 1234, "componentName": "S1B"}]
# print(read_input_and_form_output(input_dict))
