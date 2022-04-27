import os
import json
import cv2
from ocr_analytic_service.bladePartWrapper import blade_part_analytics
from ocr_analytic_service.shroudPartWrapper import shroud_part_analytics
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

# def read_input_and_form_output(s3_resource,input_dict):
def read_input_and_form_output(input_dict):
    logger.info(f"Analytics Input: \n {json.dumps(input_dict)}")
    # logger.info('System memory usage in bytes:' % psutil.virtual_memory())
    # logger.info('SYstem CPU utilization in percent:' % psutil.cpu_percent(1))
    out_put_dict = []
    try:
        for img_obj in input_dict:
            try:
                # logger.info('Image object input: %s'% img_obj)
                # filename = img_obj["imagePath"]
                # im = cv2.imread(filename)
                bucket = s3_resource.Bucket(os.getenv('BUCKET_NAME'))
                image_folder_path = os.path.join(os.getenv('IMAGE_FOLDER_PATH'), img_obj['imagePath'])
                img = bucket.Object(image_folder_path).get().get('Body')
                image = np.asarray(bytearray(img.read()), dtype="uint8")
                im = cv2.imdecode(image, cv2.IMREAD_COLOR)
                path, filename = os.path.split(img_obj['imagePath'])
                # Add logic to check compon based on 'componentId' and read image once and pass it across
                if img_obj["partType"] == 'BLADES':
                    out_put_dict = blade_part_analytics(img_obj, im, filename)
                elif img_obj["partType"] == 'SHROUDS':
                    out_put_dict = shroud_part_analytics(img_obj, im, filename)
                    
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