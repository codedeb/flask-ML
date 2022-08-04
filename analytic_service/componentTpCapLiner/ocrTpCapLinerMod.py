import logging
import cv2
import numpy as np
from wrapper_service.constants import ModelDetails
from .inferenceTpCapLiner import getClassResults
from .modelArtifacts import detector

# import some common detectron2 utilities
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg

import pandas as pd

logger = logging.getLogger(__name__)

def ocr_parser_tp_cap_liner(seg_out, model_params, label_type):
    try:
        ocr_tp_cap_liner_predictor = detector(ModelDetails.tp_cap_liner_ocr_config_path, ModelDetails.tp_cap_liner_ocr_model_path,ModelDetails.tp_cap_liner_ocr_threshold)

        # load class_map
        model_params_ocr = model_params["tp_cap_liner"]["ocr"]
        class_map_tp_cap_liner = {int(k):v for k,v in model_params_ocr["class_map"].items()}

        if label_type == 'label_not_found':
            out_obj = {}
            out_obj["ocrValue"] = ''
            out_obj["confValue"] = 0.0
            out_obj["confBand"] = "LOW"
            return out_obj

        if label_type == 'ln_cp_tp_o_bb':
            im = seg_out["O_BB"]["segment"]
            bboxes_dict = {'o_bb': seg_out["O_BB"]["box"], \
                           'sn':   seg_out["SN"]["box"]}
        
            # handle case when O_BB is found but SN box is not found
            tmp_sn = seg_out["SN"]["box"] 
            if np.all(np.array(tmp_sn) == 0):
                tmp_o_bb = seg_out["O_BB"]["box"] 
                xmin, ymin, xmax, ymax = tmp_o_bb[0], tmp_o_bb[1], tmp_o_bb[2], tmp_o_bb[3]
                bboxes_dict['sn'] = [0, 0, xmax-xmin, ymax-ymin]
                
        # else: # ln_cp_tp_o_bb_sn - use outer bounding box for both o_bb and sn
        if label_type == 'ln_cp_tp_o_bb_sn':
            im = seg_out["O_BB_SN"]["segment"]
            tmp_sn = seg_out["O_BB_SN"]["box"] # use o_bb_sn as sn for this case (for now)
            xmin, ymin, xmax, ymax = tmp_sn[0], tmp_sn[1], tmp_sn[2], tmp_sn[3]
            bboxes_dict = {'o_bb': seg_out["O_BB_SN"]["box"], \
                           'sn':   [0, 0, xmax-xmin, ymax-ymin] }

        ## image pre-processing start
        # noise removal
        im = cv2.GaussianBlur(im,(5,5),0)

        # resize to 500px height
        height, width = im.shape[:2]
        resize_fac = 1.0
        if height != 0:
            resize_fac = 500.0 / height
        im = cv2.resize(im,(int(np.round(resize_fac*width)), int(np.round(resize_fac*height))), interpolation = cv2.INTER_CUBIC)
        
        # adjust sn and seg bboxes after resizing of image
        bboxes_dict['o_bb'] = [int(resize_fac * x) for x in bboxes_dict['o_bb']]
        bboxes_dict['sn'] = [int(resize_fac * x) for x in bboxes_dict['sn']]
        ## image pre-processing end        

        ocr_tp_cap_liner_outputs = ocr_tp_cap_liner_predictor(im)

        logger.info('TP/Cap/Liner OCR Parser successfull!')
    except Exception as e:
        logger.info('TP/Cap/Liner OCR Parser failure!')
        logger.info(e)
    
    try:
        bboxes = [tuple(bboxes_dict["o_bb"]), \
                  tuple(bboxes_dict["sn"])]
        # Extract the strings 
        resultString, confidence, confidence_band = getClassResults(class_map_tp_cap_liner, bboxes, ocr_tp_cap_liner_outputs, label_type)
        out_obj = {}
        out_obj["ocrValue"] = resultString
        out_obj["confValue"] = confidence
        out_obj["confBand"] = "LOW"
        logger.info('TP/Cap/Liner post processing success! %s' % out_obj)
    except Exception as e:
        logger.info('TP/Cap/Liner post processing failure!')
        logger.info(e)

    return out_obj    