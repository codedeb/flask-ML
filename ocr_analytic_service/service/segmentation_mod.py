import os
from .inference_segmentation import clean_class
from .model_artifacts import detector
from .conf_band import confidence_band
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def img_segmenter(img):
    logger.info('Inside Image segementer')
    class_map = {0: 'ROI', 2: 'PSN', 4: 'PR'}
    logger.info('class map: %s' % class_map)
    dct_out_segs = dict.fromkeys(list(class_map.values()))
    logger.info('dct_out_segs: %s' % dct_out_segs)
    config_path = "ocr_analytic_service/service/configSeg_file.yaml"
    logger.info('config_path: %s' % config_path)
    base_path = os.getenv("NAS_PATH")
    logger.info('Seg model path in plp: %s' % os.path.join(base_path, '/models/model_final_segmentation.pth'))
    model_weight_path = "/opt/shared/data/cpl/idm/models/model_final_segmentation.pth"
    # model_weight_path = r"/shared-volume/model_final_segmentation.pth"
    logger.info('Segmentation model path: %s' % model_weight_path)
    threshold = 0.3

    # Make prediction
    predictor = detector(config_path, model_weight_path, threshold)
    outputs = predictor(img)
    classes = outputs['instances'].pred_classes
    boxes = outputs['instances'].pred_boxes
    scores = outputs['instances'].scores
    classes_list = classes.tolist()
    scores_list = scores.tolist()
    boxes_list = boxes.tensor.tolist()

    # Clean the predictions
    clean_box_list, clean_classes_list, clean_scores_list = clean_class(
        classes_list, scores_list, boxes_list, list(class_map.keys()))
    clean_confband_list = [confidence_band([item], 1)[1] for item in clean_scores_list]

    # Update class map and prepare outputs
    class_map_up = dict(zip(clean_classes_list, [class_map[item] for item in clean_classes_list]))
    dct_clean_box = dict(zip(class_map_up.keys(), clean_box_list))
    dct_clean_class_list = dict(zip(class_map_up.keys(), clean_classes_list))
    dct_out_conf = dict(zip(class_map_up.values(), clean_scores_list))
    dct_out_confband = dict(zip(class_map_up.values(), clean_confband_list))
    for index in dct_clean_box.keys():
        box_list = dct_clean_box[index]
        try:
            width = box_list[0]-box_list[2]
            height = box_list[1]-box_list[3]
        except IndexError as e:
            print('error', e)
        if class_map[index] == 'PSN':
            multwd = 0.1
            multht = 0.1
        else:
            multwd = 0
            multht = 0
        roi_cropped = img[int(box_list[1]+(height*multht)):int(box_list[3]-(height*multht)),
                          int(box_list[0]+(width*multwd)):int(box_list[2]-(width*multwd))]
        dct_out_segs[class_map[int(
            dct_clean_class_list[index])]] = roi_cropped
        
    # Publish output
    dct_out = {}
    for seg in class_map.values():
        if seg in class_map_up.values():
            out_obj = {}
            out_obj['segment'] = dct_out_segs[seg]
            out_obj['confValue'] = dct_out_conf[seg]
            out_obj['confBand'] = dct_out_confband[seg]
            dct_out[seg] = out_obj
        else:
            out_obj = {}
            out_obj['segment'] = img
            out_obj['confValue'] = 0
            out_obj['confBand'] = "LOW"
            dct_out[seg] = out_obj
    return dct_out
