import json
import logging
import json
from .componentTpCapLiner.segmentationModTpCapLiner import img_segmenter_tp_cap_liner
from .componentTpCapLiner.ocrTpCapLinerMod import ocr_parser_tp_cap_liner

logger = logging.getLogger(__name__)

def tp_cap_liner_part_analytics(img_obj, im):
    logger.info(f"TP Cap Liner Analytics Input: {img_obj}")
    out_put_dict = []
    if im is not None:
        with open('analytic_service/model_params.json') as file:
            model_params = json.load(file)
        try:
            seg_out, label_type = img_segmenter_tp_cap_liner(im, model_params)
            logger.info(f"label type : {label_type}")
            logger.info('Tp Cap Liner Segmentation successful!')
            # logger.debug('Shroud Segmentation successful! %s' % seg_out)
        except Exception as e:
            logger.info('Tp Cap Liner Segmentation failure! %s' % e)
            seg_out = dict.fromkeys(["O_BB", "SN", "O_BB_SN"])
            seg_out["O_BB"] = {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}
            seg_out["SN"] = {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}
            seg_out["O_BB_SN"] =  {"segment": im, "box": [0,0,0,0], "confValue": None, "confBand": None}

        ocr_parser_out = {}
        try:
            ###Output of the model that has the alphanums
            ocr_parser_out = ocr_parser_tp_cap_liner(seg_out, model_params, label_type)
            logger.info('TP/Cap/Liner OCR Flow success! %s' % ocr_parser_out)
        except Exception as e:
            logger.info('TP/Cap/Liner OCR Flow failure! %s' % e)
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
