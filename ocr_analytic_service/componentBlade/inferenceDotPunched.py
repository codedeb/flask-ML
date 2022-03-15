import logging
from componentBlade.confBand import confidence_band
"""
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
"""
logger = logging.getLogger(__name__)

class Inference:
    def output(self, data, predictor, im):
        outputs = predictor(im)
        classes = outputs["instances"].pred_classes
        boxes = outputs["instances"].pred_boxes
        scores = outputs["instances"].scores
        box_list, serial_number, scores_list = list(), list(), list()
        [box_list.append(box[0].item()) for v, box in enumerate(boxes)]
        sorted_list = sorted(box_list)

        [
            serial_number.append(
                data[0].thing_classes[classes[box_list.index(x_left)].item()]
            )
            for x_left in sorted_list
        ]

        [scores_list.append(scores[number[0]].item()) for number in enumerate(scores)
         ]
        string_ocr = "".join(map(str, serial_number))

        conf, conf_band = confidence_band(scores_list, 6)

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
