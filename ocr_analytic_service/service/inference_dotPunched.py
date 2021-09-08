import logging
from .conf_band import confidence_band

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


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

        return string_ocr, conf, conf_band
