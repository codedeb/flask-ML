import logging
from .confBand import confidence_band
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
            serial_number.append(
                data[classes[x_left[1]].item()]
            )
            for x_left in sorted_list
        ]

        [
            scores_list.append(
                scores[x_left[1]].item()
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
