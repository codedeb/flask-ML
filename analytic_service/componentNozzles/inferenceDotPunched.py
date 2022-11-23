import logging
from .confBand import confidence_band
from .modelArtifacts import iou_calc, delete_multiple_element
"""
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
"""
logger = logging.getLogger(__name__)

class Inference:
    def output(self, data, predictor, im, psn_box, exp_len):
        outputs = predictor(im)
        classes = outputs["instances"].pred_classes
        boxes = outputs["instances"].pred_boxes
        scores = outputs["instances"].scores
        box_list, serial_number, scores_list, boxes_list = list(), list(), list(), list()
        [box_list.append(box[0].item()) for v, box in enumerate(boxes)]
        boxes_list = boxes.tensor.tolist()
        boxes_centroid_list = [[(item[0]+item[2])/2, (item[1]+item[3])/2] for item in boxes_list]
        boxes_centroid_psn_idx_list = []
        for item in boxes_centroid_list:
            if item[0] > psn_box[0] and item[1] > psn_box[1] and item[0] < psn_box[2] and item[1] < psn_box[3]:
                boxes_centroid_psn_idx_list.append(boxes_centroid_list.index(item))
        boxes_list = [boxes_list[x] for x in boxes_centroid_psn_idx_list]
        box_list = [box_list[x] for x in boxes_centroid_psn_idx_list]
        box_list = [(a, b) for a, b in zip(box_list, boxes_centroid_psn_idx_list)]
        boxes_list.sort()
        sorted_list = sorted(box_list)

        [
            scores_list.append(
                scores[x_left[1]].item()
            )
            for x_left in sorted_list
        ]

        # Find boxes which are intersecting and remove them
        list_rem = iou_calc(boxes_list)
        if list_rem:
            list_idx_rem = []
            for item in list_rem:
                list_idx_rem.append(scores_list.index(min([scores_list[num] for num in item])))
                list_idx_rem = list(set(list_idx_rem))
                boxes_list = delete_multiple_element(boxes_list, list_idx_rem)
                sorted_list = delete_multiple_element(sorted_list, list_idx_rem)
                scores_list = delete_multiple_element(scores_list, list_idx_rem)

        # If there are still more than exp_len number of boxes remaining
        list_keep = sorted(range(len(scores_list)), key=lambda k: scores_list[k], reverse=True)[0:exp_len]
        list_keep.sort()
        boxes_list = [boxes_list[item] for item in list_keep]
        sorted_list = [sorted_list[item] for item in list_keep]
        scores_list = [scores_list[item] for item in list_keep]

        [
            serial_number.append(
                data[classes[x_left[1]].item()]
            )
            for x_left in sorted_list
        ]

        string_ocr = "".join(map(str, serial_number))

        conf, conf_band = confidence_band(scores_list, exp_len)

        '''
        if len(scores_list) > 0:
            logging.info('length of scorelist: %s' %
                         len(scores_list))
            # conf = round(sum(scores_list) / len(scores_list), 3)
            conf = np.prod(scores_list)
            if len(scores_list) != 6:
                logging.warning('length of score list: %s' %
                                len(scores_list))
                conf_band = "LOW"
                conf = 0
            elif conf > 0.95:
                conf_band = "HIGH"
            elif conf >= 0.60 and conf <= 0.95:
                conf_band = "MEDIUM"
            elif conf < 0.60:
                conf_band = "LOW"

        else:
            if len(scores_list) == 0:
                logging.critical('length of score list: %s' % len(scores_list))
                conf = 0
                conf_band = "LOW"

        logging.info('conf_band: %s' % conf_band)
        logging.info('confidence: %s' % conf)
        '''

        return string_ocr, conf, conf_band
