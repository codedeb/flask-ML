# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 12:05:36 2021

@author: 302016159
"""

import json
import os
import ocr_analytic_service.service.one_mask as one_mask
import ocr_analytic_service.service.two_transform as two_transform
import ocr_analytic_service.service.three_tesseract as three_tesseract
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def main(inp_json):
    '''
    # Read input json
    with open("input.json") as f:
        inp_json = json.load(f)
    '''

    out_json = []
    logger.info('in main of runner')
    for img_obj in inp_json:
        try:
            # Read input image path
            base_path = os.environ['NAS_PATH']
            fl_nm = os.path.join(base_path, img_obj['imagePath'])
            logger.info('fl_nm : %s' % fl_nm)
            # Get masked image output
            mask_img = one_mask.main(fl_nm)
            logger.info('after one : %s' % fl_nm)
            # Get transformed image output
            pre_img = two_transform.main(mask_img)
            logger.info('after two : %s' % pre_img)
            # Get Tesseract output
            list_res, conf = three_tesseract.main(pre_img)
            str_ocr = ''.join(list_res)
            # Create output json objects
            out_obj = img_obj.copy()
            if str_ocr == '':
                out_obj['ocrValue'] = 'NOT DETECTED'
            else:
                out_obj['ocrValue'] = str_ocr
            out_obj['ocrConfidenceValue'] = conf
            if int(conf) > 75:
                out_obj['ocrConfidenceBand'] = 'HIGH'
            elif int(conf) < 75 & int(conf) > 60:
                out_obj['ocrConfidenceBand'] = 'MEDIUM'
            else:
                out_obj['ocrConfidenceBand'] = 'LOW'
            out_obj['ocrAdditional'] = ''
        except Exception as e:
            logger.error('Exception occurred processing :%s' % img_obj)
            out_obj = img_obj.copy()
            out_obj['ocrValue'] = 'FAILED'
            out_obj['ocrConfidenceValue'] = 0
            out_obj['ocrConfidenceBand'] = 'LOW'
            out_obj['ocrAdditional'] = ''
        out_json.append(out_obj)
        logger.info('out_json : %s' % out_json)
    '''
    with open('output.json', 'w') as f:
        json.dump(out_json, f)
    '''
    return out_json
