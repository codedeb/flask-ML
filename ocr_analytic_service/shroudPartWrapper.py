import json
import logging
import json
import numpy as np
import traceback
import matplotlib.pyplot as plt
from .componentShroud.segmentationModShroud import img_segmenter_shrouds
from .componentShroud.ocrShroudMod import ocr_parser_shrouds
logger = logging.getLogger(__name__)


def shroud_part_analytics(img_obj, im, filename):
    logger.info(f"Shrouds Analytics Input: {img_obj}")
    out_put_dict = []
    if im is not None:
        with open('/ocr-wrapper-service/ocr_analytic_service/model_params.json') as file:
            model_params = json.load(file)
    
        try:
            seg_out = img_segmenter_shrouds(im, model_params)
            logger.info('Shroud Segmentation successful! %s' % seg_out)
            logger.debug('Shroud Segmentation successful! %s' % seg_out)
        except Exception as e:
            logger.info('Shroud Segmentation failure!')
            logger.info(e)
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
            logger.info('Shrouds OCR Flow failure!')
            logger.info(e)
            ocr_parser_out["ocrValue"] = "OCR_UNKN"
            ocr_parser_out["confValue"] = 0.0
            ocr_parser_out["confBand"] = "LOW"
            # logger.info(traceback.format_exc())

        # Plot image and segment output for demo
        try:
            logger.info('Plotting Shroud Segmentation...')
            plt.subplot(2,2,1)
            plt.imshow(im[...,::-1])
            plt.title('input image')
            plt.subplot(2,2,2)
            plt.imshow(seg_out["O_BB"]["segment"][...,::-1])
            bbox = seg_out["SN"]["box"]
            xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
            plt.plot([xmin, xmin, xmax, xmax, xmin], [ymin, ymax, ymax, ymin, ymin], 'r-')
            plt.text(xmax, ymax, 'SN')
            bbox = seg_out["SEG"]["box"]
            xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
            plt.plot([xmin, xmin, xmax, xmax, xmin], [ymin, ymax, ymax, ymin, ymin], 'r-')
            plt.text(xmax, ymax, 'SEG')
            plt.title('O_BB')
            plt.subplot(2,2,3)
            plt.imshow(seg_out["SN"]["segment"][...,::-1])
            plt.title('SN')
            plt.subplot(2,2,4)
            plt.imshow(seg_out["SEG"]["segment"][...,::-1])
            plt.title('SEG')
            
            # ax = plt.subplot(2,2,5)
            # ax.text(3, 4, ocr_parser_out["ocrValue"] , fontsize=15,  color='red')
            # ax.text(60, 4.1, ocr_parser_out["confValue"] , fontsize=15,  color='red')
            # plt.title('OCR')

            # plt.show()
            plt.suptitle(filename)
            plt.savefig(img_obj["imagePath"]+'_seg_output.png')
            logger.info('Plotting Shroud Segmentations successful!')
        except Exception as e:
            logger.info('Shroud Segmentation output plot failure!')
            logger.info(e)

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
