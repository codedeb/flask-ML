import json
import logging
import json
from .componentShroud.segmentationModShroud import img_segmenter_shrouds
from .componentShroud.ocrShroudMod import ocr_parser_shrouds

logger = logging.getLogger(__name__)

def tp_cap_liner_part_analytics(img_obj, im):
    logger.info(f"TP Cap Liner Analytics Input: {img_obj}")
    out_put_dict = []
    if im is not None:
        with open('/ocr-wrapper-service/analytic_service/model_params.json') as file:
            model_params = json.load(file)

        final_obj = img_obj.copy()
        final_obj["ocrValue"] = ""
        final_obj["ocrConfidenceValue"] = 0.0
        final_obj["ocrConfidenceBand"] = ""
        final_obj["ocrPrefixValue"] = ""
        final_obj["ocrPrefixConfidenceBand"] = ""
        final_obj["ocrPrefixConfidenceValue"] = ""
        final_obj["ocrNumericValue"] = ""
        final_obj["ocrNumericConfidenceBand"] = ""
        final_obj["ocrNumericConfidenceValue"] = ""
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
