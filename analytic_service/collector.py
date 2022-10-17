from .componentBlade.confBand import overall_band
import numpy as np
import logging

logger = logging.getLogger(__name__)

def data_collector(seg_out, psn_out, prefix_out, snb_out):

    '''SPECIAL CONDITIONS'''
    if '8' in str(psn_out['ocrValue']):
        psn_out['confValue'] = 0.8
        psn_out['confBand'] = 'MEDIUM'
    '''END OF SPECIAL CONDITIONS'''

    list_conf_band = [seg_out['obb_b']['confBand'], psn_out['confBand'], prefix_out['confBand'], snb_out['confBand']]
    res_conf_band = overall_band(list_conf_band)
    res_conf = seg_out['obb_b']['confValue']*psn_out['confValue']*prefix_out['confValue']*snb_out['confValue']
    
    # put the logic here
    if len(psn_out['ocrValue'])==6 and len(prefix_out['ocrValue'])==4:
        res_conf = np.round(res_conf,2)
        res_ocr = prefix_out['ocrValue']+psn_out['ocrValue']
        
    elif len(prefix_out['ocrValue']) == 0 and len(psn_out['ocrValue'])== 0 :
        res_conf = np.round(res_conf,2)
        res_ocr= snb_out['ocrValue']
        
    else:
        res_ocr= prefix_out['ocrValue']+psn_out['ocrValue']
        
        
    logger.info(f"prefix_out : {prefix_out}")
    logger.info(f"psn_out : {psn_out}")
    logger.info(f"snb_out : {snb_out}")

    out_obj = {}
    out_obj['ocrValue'] = res_ocr
    out_obj['confValue'] = res_conf
    out_obj['confBand'] = res_conf_band
    return out_obj
