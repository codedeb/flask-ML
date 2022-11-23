from cmath import log
import os
import json
import cv2
import time
from analytic_service.bladePartWrapper import blade_part_analytics
from analytic_service.shroudPartWrapper import shroud_part_analytics
from analytic_service.tpCapLinerPartWrapper import tp_cap_liner_part_analytics
from analytic_service.nozzlesWrapper import nozzles_part_analytics
import logging
import numpy as np

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


    
def blade_operation(img_obj, im):
    logger.info('Calling BLADES flow!')
    return blade_part_analytics(img_obj, im)

def shroud_operation(img_obj, im):
    logger.info('Calling SHROUDS flow!')
    return shroud_part_analytics(img_obj, im)

def trans_cap_liner_operation(img_obj, im):
    logger.info('Calling TPCAPASSY flow!')
    return tp_cap_liner_part_analytics(img_obj, im)

def fuel_nozzles_operation(img_obj, im):
    logger.info('Calling FUELNOZZLES flow!')
    return nozzles_part_analytics(img_obj, im)

def perform_operaions(operation, img_obj, im):
    ops = {
    "BLADES": blade_operation,
    "SHROUDS": shroud_operation,
    "TRANSPIECE": trans_cap_liner_operation,
    "CAPASSY":trans_cap_liner_operation,
    "LINERASSY":trans_cap_liner_operation, 
    "NOZZLES": fuel_nozzles_operation
  }
    chosen_operation_function = ops.get(operation)
    return chosen_operation_function(img_obj, im)

def read_input_and_form_output(s3_resource,input_dict):
    logger.info(f"Analytics Input: {json.dumps(input_dict)}")
    
    out_put_dict = []
    try:
        for img_obj in input_dict:
            img_path = img_obj['imagePath']
            try:
                attempts = 0
                success = False
                while attempts < 3 and not success:
                    try:
                        # Local Testing setup:
                        # success = True
                        # logger.info('Image object input: %s'% img_obj)
                        # # filename = img_obj["imagePath"]
                        # filename = img_path
                        # im = cv2.imread(filename)
                        
                        bucket = s3_resource.Bucket(os.getenv('BUCKET_NAME'))
                        image_folder_path = os.path.join(os.getenv('IMAGE_FOLDER_PATH'), img_path)
                        img = bucket.Object(image_folder_path).get().get('Body')
                        image = np.asarray(bytearray(img.read()), dtype="uint8")
                        im = cv2.imdecode(image, cv2.IMREAD_COLOR)
                        success = True
                    except Exception as e:
                        logger.error('Not able to read image: %s' % e)
                        time.sleep(3)
                        logger.error('Trying to read image after 3 secs')
                        attempts += 1
                        if attempts == 3:
                            break
               
                # calling operations which handles log according to the component type
                output_dict = perform_operaions(img_obj['partType'], img_obj, im)
        
            except Exception as e:
                logger.error('OCR Failed: %s' % e)
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
        logger.info('Analytics Output: %s' % output_dict)
        return out_put_dict
    except Exception as e:
        logger.info('Error while detecting OCR!')
        logger.debug('Error while detecting OCR! %s' % e)

    return output_dict