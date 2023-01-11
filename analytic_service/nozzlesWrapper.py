from .componentNozzles.segmentationMod import img_segmenter
from .componentNozzles.dotPunchMod import dot_punched_data_parser
from .collector import data_collector
import logging

logger = logging.getLogger(__name__)

def nozzles_part_analytics(img_obj, im):
    logger.info(f"Analytics Input for Nozzles: \n {img_obj}")
    out_put_dict = []
    if im is not None:
        try:
            seg_out = img_segmenter(im)
            logger.info('Segmentation successful!')
        except Exception as e:
            logger.info('Segmentation failure! %s' % e)
            seg_out = dict.fromkeys(["obb_b", "psn", "pr"])
            seg_out["obb_b"] = {"confBand": "LOW", "confValue": 0, "segment": im}
            seg_out["psn"] = {"confBand": "LOW", "confValue": 0, "segment": im}
            seg_out["pr"] = {"confBand": "LOW", "confValue": 0, "segment": im}
        try:
            psn_out = dot_punched_data_parser(seg_out['obb_b']['segment'], seg_out['psn']['box'], exp_len=5)
            logger.info('psn successful! %s' % psn_out)
        except Exception as e:
            logger.info('psn failure! %s' % e)
            psn_out = {}
            psn_out["ocrValue"] = "S_UNKN"
            psn_out["confValue"] = 0.0
            psn_out["confBand"] = "LOW"
        try:
            prefix_out = dot_punched_data_parser(seg_out['obb_b']['segment'], seg_out['pr']['box'], exp_len=4)
            logger.info('Prefix successful! %s' % prefix_out)
        except Exception as e:
            logger.info('Prefix failure! %s' % e)
            prefix_out = {}
            prefix_out["ocrValue"] = "P_UNKN"
            prefix_out["confValue"] = 0.0
            prefix_out["confBand"] = "LOW"
            
        # try SNB out
        try:
            snb_out = dot_punched_data_parser(seg_out['obb_b']['segment'], seg_out['snb']['box'], exp_len=9)
            logger.info('snb successful! %s' % snb_out)
        except Exception as e:
            logger.info('snb failure! %s' % e)
            snb_out = {}
            snb_out["ocrValue"] = "P_UNKN"
            snb_out["confValue"] = 0.0
            snb_out["confBand"] = "LOW"
            
        result_out = data_collector(seg_out, psn_out, prefix_out, snb_out)
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

    return out_put_dict