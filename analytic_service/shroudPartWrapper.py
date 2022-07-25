import json
import logging
import json
from .componentShroud.segmentationModShroud import img_segmenter_shrouds
from .componentShroud.ocrTpCapLinerMod import ocr_parser_shrouds

logger = logging.getLogger(__name__)

def shroud_part_analytics(img_obj, im):
    logger.info(f"Shrouds Analytics Input: {img_obj}")
    out_put_dict = []
    if im is not None:
        with open('/ocr-wrapper-service/analytic_service/model_params.json') as file:
            model_params = json.load(file)
        try:
            seg_out = img_segmenter_shrouds(im, model_params)
            logger.info('Shroud Segmentation successful!')
            # logger.debug('Shroud Segmentation successful! %s' % seg_out)
        except Exception as e:
            logger.info('Shroud Segmentation failure! %s' % e)
            seg_out = dict.fromkeys(["O_BB", "SN", "SEG"])
            seg_out["O_BB"] = {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}
            seg_out["SN"] = {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}
            seg_out["SEG"] =  {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}

        ocr_parser_out = {}
        try:
            bbox = []
            bbox.append(seg_out["SN"]["box"])
            bbox.append(seg_out["SEG"]["box"])
            ###Output of the model that has the alphanums
            ocr_parser_out = ocr_parser_shrouds(seg_out["O_BB"]["segment"], bbox)
            logger.info('Shrouds OCR Flow success! %s' % ocr_parser_out)
        except Exception as e:
            logger.info('Shrouds OCR Flow failure! %s' % e)
            ocr_parser_out["ocrValue"] = "OCR_UNKN"
            ocr_parser_out["confValue"] = 0.0
            ocr_parser_out["confBand"] = "LOW"
            # logger.info(traceback.format_exc())

        final_obj = img_obj.copy()
        final_obj["ocrValue"] = ocr_parser_out["ocrValue"]
        final_obj["ocrConfidenceValue"] = ocr_parser_out["confValue"]
        final_obj["ocrConfidenceBand"] = ocr_parser_out["confBand"]
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
