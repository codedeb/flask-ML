
from .conf_band import overall_band


def data_collector(seg_out, psn_out, prefix_out):

    '''SPECIAL CONDITIONS'''
    if '8' in str(psn_out['ocrValue']):
        psn_out['confValue'] = 0.8
        psn_out['confBand'] = 'MEDIUM'
    '''END OF SPECIAL CONDITIONS'''

    list_conf_band = [seg_out['PSN']['confBand'], psn_out['confBand'], prefix_out['confBand']]
    res_conf_band = overall_band(list_conf_band)
    res_conf = seg_out['PSN']['confValue']*psn_out['confValue']*prefix_out['confValue']
    res_ocr = prefix_out['ocrValue']+' '+psn_out['ocrValue']
    out_obj = {}
    out_obj['ocrValue'] = res_ocr
    out_obj['confValue'] = res_conf
    out_obj['confBand'] = res_conf_band
    return out_obj
