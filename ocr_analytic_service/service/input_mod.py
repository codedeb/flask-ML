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
import psutil
"""
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


try:
    s3_resource = boto3.resource('s3', region_name=os.getenv('REGION'))
except:
    s3_resource = boto3.resource('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                 AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'),
                                 region_name=os.getenv('REGION'))
    pass
"""
logger = logging.getLogger(__name__)

def read_input_and_form_output(s3_resource,input_dict):
    logger.info(f"Analytics Input: \n {json.dumps(input_dict)}")
    # logger.info('System memory usage in bytes:' % psutil.virtual_memory())
    # logger.info('SYstem CPU utilization in percent:' % psutil.cpu_percent(1))
    out_put_dict = []
    try:
        for img_obj in input_dict:
            try:
                bucket = s3_resource.Bucket(os.getenv('BUCKET_NAME'))
                image_folder_path = os.path.join(os.getenv('IMAGE_FOLDER_PATH'), img_obj['imagePath'])
                img = bucket.Object(image_folder_path).get().get('Body')
                image = np.asarray(bytearray(img.read()), dtype="uint8")
                im = cv2.imdecode(image, cv2.IMREAD_COLOR)
                path, filename = os.path.split(img_obj['imagePath'])
                # cv2.imwrite('/idm/input/abc.jpg',im)
                # im = cv2.imread(fl_nm, cv2.IMREAD_UNCHANGED)
                # logger.info('Image read: %s' % im)
                if im is not None:
                    try:
                        seg_out = img_segmenter(im)
                        logger.info('Segmentation successful!')
                        # Uncomment if need to dump segmented images for debugging
                        # try:
                        #     logger.info('Segmentation result: %s' % seg_out )
                        #     file_seg = 'seg/' + filename
                        #     seg_dump_file_path = os.path.join(os.getenv('DUMP_IMAGES'), file_seg)
                        #     logger.info('Segmented Images will be dumped at: %s' % seg_dump_file_path)
                        #     os.makedirs("IDM/dev/dump_images/seg", exist_ok=True)
                        #     imwriteStatus = cv2.imwrite(seg_dump_file_path, im)
                        #     image_path = 'IDM/dev/dump_images/seg_out' + filename
                        #     s3_resource.meta.client.upload_file(seg_dump_file_path, os.getenv('BUCKET_NAME'), image_path)
                        # except Exception as e:
                        #     logger.info('Dumping Segmented Images failure! %s' % e)
                    except Exception as e:
                        logger.info('Segmentation failure!')
                        logger.info(e)
                        seg_out = dict.fromkeys(["ROI", "PSN", "PR"])
                        seg_out["ROI"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                        seg_out["PSN"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                        seg_out["PR"] = {"confBand": "LOW", "confValue": 0, "segment": im}
                    try:
                        psn_out = dot_punched_data_parser(seg_out['ROI']['segment'], seg_out['PSN']['box'], exp_len=6)
                        logger.info('dotpunch prediction: %s' % psn_out)
                    except Exception as e:
                        logger.info('Dot punch failure!')
                        logger.info(e)
                        psn_out = {}
                        psn_out["ocrValue"] = "S_UNKN"
                        psn_out["confValue"] = 0.0
                        psn_out["confBand"] = "LOW"
                    try:
                        # prefix_out = prefix_data_parser(seg_out['ROI']['segment'], filename)
                        prefix_out = dot_punched_data_parser(seg_out['ROI']['segment'], seg_out['PR']['box'], exp_len=4)
                        logger.info('prefix prediction: %s' % prefix_out)
                    except Exception as e:
                        logger.info('Prefix failure! %s' % e)
                        prefix_out = {}
                        prefix_out["ocrValue"] = "P_UNKN"
                        prefix_out["confValue"] = 0.0
                        prefix_out["confBand"] = "LOW"
                    result_out = data_collector(seg_out, psn_out, prefix_out)
                    final_obj = img_obj.copy()
                    final_obj["ocrValue"] = result_out["ocrValue"]
                    final_obj["ocrConfidenceValue"] = result_out["confValue"]
                    final_obj["ocrConfidenceBand"] = result_out["confBand"]
                    final_obj["ocrPrefixValue"]=prefix_out["ocrValue"]
                    final_obj["ocrPrefixConfidenceBand"]=prefix_out["confBand"]
                    final_obj["ocrPrefixConfidenceValue"]=prefix_out["confValue"]
                    final_obj["ocrNumericValue"] =psn_out["ocrValue"]
                    final_obj["ocrNumericConfidenceBand"]=psn_out["confBand"]
                    final_obj["ocrNumericConfidenceValue"]=psn_out["confValue"]
                    final_obj["ocrAdditional"] = ""
                    out_put_dict.append(final_obj)
                else:
                    final_obj = img_obj.copy()
                    final_obj["ocrValue"] = "FAILED"
                    final_obj["ocrConfidenceValue"] = 0.0
                    final_obj["ocrConfidenceBand"] = "LOW"
                    final_obj["ocrPrefixValue"] = "FAILED"
                    final_obj["ocrPrefixConfidenceBand"] = "LOW"
                    final_obj["ocrPrefixConfidenceValue"] = 0.0
                    final_obj["ocrNumericValue"] = "FAILED"
                    final_obj["ocrNumericConfidenceBand"] = "LOW"
                    final_obj["ocrNumericConfidenceValue"] = 0.0
                    final_obj["ocrAdditional"] = "Failed to read image"
                    out_put_dict.append(final_obj)
            except Exception as e:
                logger.info('OCR Failed: %s' % e)
                final_obj = img_obj.copy()
                final_obj["ocrValue"] = "FAILED"
                final_obj["ocrConfidenceValue"] = 0.0
                final_obj["ocrConfidenceBand"] = "LOW"
                final_obj["ocrPrefixValue"] = "FAILED"
                final_obj["ocrPrefixConfidenceBand"] = "LOW"
                final_obj["ocrPrefixConfidenceValue"] = 0.0
                final_obj["ocrNumericValue"] = "FAILED"
                final_obj["ocrNumericConfidenceBand"] = "LOW"
                final_obj["ocrNumericConfidenceValue"] = 0.0
                final_obj["ocrAdditional"] = "OCR Failed"
                out_put_dict.append(final_obj)
        logger.info('Analytics Output: %s' % out_put_dict)
        return out_put_dict
    except Exception as e:
        logger.info('Error while detecting OCR!')
        logger.debug('Error while detecting OCR! %s' % e)

    return out_put_dict