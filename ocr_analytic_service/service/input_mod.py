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
                                 AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'),
                                 region_name=os.getenv('REGION'))
    pass


def read_input_and_form_output(input_dict):
    logger.info('Analytics Input: %s' % input_dict)
    out_put_dict = []
    try:
        for img_obj in input_dict:
            try:
                bucket = s3_resource.Bucket(os.getenv('BUCKET_NAME'))
                image_folder_path = os.path.join(os.getenv('IMAGE_FOLDER_PATH'), img_obj['imagePath'])
                img = bucket.Object(image_folder_path).get().get('Body')
                image = np.asarray(bytearray(img.read()), dtype="uint8")
                im = cv2.imdecode(image, cv2.IMREAD_COLOR)
                # cv2.imwrite('/idm/input/abc.jpg',im)
                # im = cv2.imread(fl_nm, cv2.IMREAD_UNCHANGED)
                # logger.info('Image read: %s' % im)
                if im is not None:
                    try:
                        seg_out = img_segmenter(im)
                        logger.info('Segmentation successful!')
                        # logger.info('Segmentation result: %s' % seg_out )
                        # seg_dump_file_path = os.path.join(os.getenv('DUMP_IMAGES'), img_obj['imagePath'])
                        # logger.info('seg_dump_file_path %s' % seg_dump_file_path)
                        # os.makedirs("IDM/dev/dump_images/242/PARTSOUT", exist_ok=True)
                        # imwriteStatus = cv2.imwrite(seg_dump_file_path, seg_out['ROI']['segment'])
                        # logger.info('imwriteStatus %s' % imwriteStatus)
                        # s3_resource.meta.client.upload_file(seg_dump_file_path, os.getenv('BUCKET_NAME'), 'testImage.jpg')
                    except Exception as e:
                        logger.info('Segmentation failure! %s' % e)
                        seg_out = dict.fromkeys(["ROI", "PSN", "PR"])
                        seg_out["ROI"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                        seg_out["PSN"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                        seg_out["PR"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                    try:
                        psn_out = dot_punched_data_parser(seg_out['ROI']['segment'])
                        logger.info('dotpunch prediction: %s' % psn_out)
                    except:
                        logger.info('Dot punch failure!')
                        psn_out = {}
                        psn_out["ocrValue"] = "S_UNKN"
                        psn_out["confValue"] = 0.0
                        psn_out["confBand"] = "LOW"
                    try:
                        # prefix_out = prefix_data_parser(im)
                        prefix_out = prefix_data_parser(seg_out['ROI']['segment'])
                        logger.info('prefix prediction: %s' % prefix_out)
                    except:
                        logger.info('Prefix failure!')
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
                    final_obj = img_obj.copy()
                    final_obj["ocrValue"] = "FAILED"
                    final_obj["ocrConfidenceValue"] = 0.0
                    final_obj["ocrConfidenceBand"] = "LOW"
                    final_obj["ocrAdditional"] = "Failed to read image"
                    out_put_dict.append(final_obj)
            except Exception as e:
                logger.info('OCR Failed: %s' % e)
                final_obj = img_obj.copy()
                final_obj["ocrValue"] = "FAILED"
                final_obj["ocrConfidenceValue"] = 0.0
                final_obj["ocrConfidenceBand"] = "LOW"
                final_obj["ocrAdditional"] = "OCR Failed"
                out_put_dict.append(final_obj)
        logger.info('Analytics Output: %s' % out_put_dict)
        return out_put_dict
    except Exception as e:
        logger.info('Error while detecting OCR: %s' % e)

    return out_put_dict