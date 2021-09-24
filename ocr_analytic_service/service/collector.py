
from .conf_band import overall_band
import numpy as np


def data_collector(seg_out, psn_out, prefix_out):

    '''SPECIAL CONDITIONS'''
    if '8' in str(psn_out['ocrValue']):
        psn_out['confValue'] = 0.8
        psn_out['confBand'] = 'MEDIUM'
    '''END OF SPECIAL CONDITIONS'''

    list_conf_band = [seg_out['ROI']['confBand'], psn_out['confBand'], prefix_out['confBand']]
    res_conf_band = overall_band(list_conf_band)
    res_conf = seg_out['ROI']['confValue']*psn_out['confValue']*prefix_out['confValue']
    res_conf = np.round(res_conf,2)
    res_ocr = prefix_out['ocrValue']+psn_out['ocrValue']
    out_obj = {}
    out_obj['ocrValue'] = res_ocr
    out_obj['confValue'] = res_conf
    out_obj['confBand'] = res_conf_band
    return out_obj
