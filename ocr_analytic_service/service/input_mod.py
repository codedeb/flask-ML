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
import boto3
import numpy as np

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    s3_resource = boto3.resource('s3', region_name=os.getenv('REGION'))
except:
    s3_resource = boto3.resource('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                              AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'), region_name=os.getenv('REGION'))
    pass

def read_input_and_form_output(input_dict):
    logger.info('Input dict for ROI Update: %s' % input_dict)
    out_put_dict = []
    try:
        logger.info('Starting try loop 1')
        try:
            logger.info('Starting try and for loop')
            for img_obj in input_dict:
                logger.info('Starting for loop')
                logger.info('image input without json load: %s' % img_obj)
        except:
            logger.info('execption within try and for loop without json load for input')

        logger.info('Starting try loop 2')
        # input_arr = json.loads(input_dict)
        input_arr = input_dict
        logger.info('image input arr: %s' % input_arr)
        logger.info('Starting for loop')
        for img_obj in input_arr:
            logger.info('img obj input: %s' % img_obj)
            # base_path = os.getenv("NAS_PATH")
            # logger.info('Base path: %s' % base_path)
            # fl_nm = os.path.join(base_path, img_obj['imagePath'])
            # fl_nm = img_obj["imagePath"]
            # logger.info('file name: %s' % fl_nm)
            try:
                bucket = s3_resource.Bucket(os.getenv('BUCKET_NAME'))
                img = bucket.Object(img_obj['imagePath']).get().get('Body')
                image = np.asarray(bytearray(img.read()), dtype="uint8")
                im = cv2.imdecode(image, cv2.IMREAD_COLOR)
                # cv2.imwrite('/idm/input/abc.jpg',im)
                # im = cv2.imread(fl_nm, cv2.IMREAD_UNCHANGED)
                logger.info('Image read: %s' % im)
                seg_out = img_segmenter(im)
                logger.info('Seg out: %s' % seg_out)
                try:
                    psn_out = dot_punched_data_parser(
                        seg_out['ROI']['segment'])
                    logger.info('psn out: %s' % psn_out)
                except:
                    logger.info('exception for psn_out')
                    psn_out = {'ocr_value': None, 'conf_value': 0, 'conf_band': 'LOW'}
                try:
                    prefix_out = prefix_data_parser(im)
                    logger.info('prefix out: %s' % prefix_out)
                except:
                    logger.info('exception for prefix_out')
                    prefix_out = {"ocr_value": None, "conf_value": 0, "conf_band": "LOW"}
                result_out = data_collector(seg_out, psn_out, prefix_out)
                logger.info('data collector result: %s' % result_out)
                final_obj = img_obj.copy()
                final_obj['ocr_value'] = result_out['ocrValue']
                final_obj['conf_value'] = result_out['confValue']
                final_obj['conf_band'] = result_out['confBand']
                out_put_dict.append(final_obj)
            except Exception as e:
                logger.info('exception for seg_out', e)
                final_obj = img_obj.copy()
                final_obj['ocr_value'] = None
                final_obj['conf_value'] = 0
                final_obj['conf_band'] = 'LOW'
                out_put_dict.append(final_obj)
        logger.info('Output dict: %s' % out_put_dict)
        return out_put_dict
    except:
        logger.info('No item found')

    return out_put_dict


# input_dict = [{"imageId": 1, "imageOcrType": "PARTDRAWINGNUMBER", "imagePath": "./Raw_S1B_297719_dot_punched_IMG_2025.JPG",
#                "positionNumber": 2, "componentId": 1234, "componentName": "S1B"}]
# print(read_input_and_form_output(input_dict))
