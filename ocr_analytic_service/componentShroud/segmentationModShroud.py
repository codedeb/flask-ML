import logging
from .inferenceSegmentation import clean_class
from .modelArtifacts import detector
from .confBand import confidence_band
from ocr_wrapper_service.constants import ModelDetails

logger = logging.getLogger(__name__)

def img_segmenter(img):
    logger.info("Segment Input: %s" % img)
    img_ht = img.shape[0]
    img_wd = img.shape[1]
    class_map = {0: 'o_bb',1: 'sn', 2: 'bl', 3: 'seg'}
    dct_out_segs = dict.fromkeys(list(class_map.values()))
    dct_out_box = dict.fromkeys(list(class_map.values()))
    # config_path = "config_shroud_segmentation_v2.yaml"
    # # config_path = "configSeg_file.yaml"
    # model_weight_path = r"model_shroud_segmentation_v2.pth"
    # print(config_path)
    # print(model_weight_path)
    threshold = 0.3

    # Make prediction
    predictor = detector(ModelDetails.shroud_seg_config_path, ModelDetails.shroud_seg_model_path,ModelDetails.shroud_segmentation_threshold)
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
            width = box_list[2]-box_list[0]
            height = box_list[3]-box_list[1]
        except IndexError as e:
            print('error', e)
        if class_map[index] == 'PSN':
            multwdst = 0.1
            multhtst = 0.1
            multwded = 0.1
            multhted = 0.1
        elif class_map[index] == 'ROI':
            multwdst = 0.2
            multhtst = 0.3
            multwded = 0.2
            multhted = 0.3
        else:
            multwdst = 0
            multhtst = 0
            multwded = 0
            multhted = 0

        roi_cropped = img[max(1, int(box_list[1]-(height*multhtst))):min(int(img_ht-1), int(box_list[3]+(height*multhted))), max(1, int(box_list[0]-(width*multwdst))):min(int(img_wd-1), int(box_list[2]+(width*multwded)))]
        dct_out_segs[class_map[int(dct_clean_class_list[index])]] = roi_cropped
        dct_out_box[class_map[int(dct_clean_class_list[index])]] = [max(1, int(box_list[0]-(width*multwdst))), max(1, int(box_list[1]-(height*multhtst))), min(int(img_wd-1), int(box_list[2]+(width*multwded))), min(int(img_ht-1), int(box_list[3]+(height*multhted)))]

    # Publish output
    dct_out = {}
    for seg in class_map.values():
        if seg in class_map_up.values():
            out_obj = {}
            out_obj['segment'] = dct_out_segs[seg]
            out_obj['confValue'] = dct_out_conf[seg]
            out_obj['confBand'] = dct_out_confband[seg]
            out_obj['box'] = dct_out_box[seg]
            dct_out[seg] = out_obj
        else:
            out_obj = {}
            out_obj['segment'] = img
            out_obj['confValue'] = 0
            out_obj['confBand'] = 'LOW'
            out_obj['box'] = None
            dct_out[seg] = out_obj
    return dct_out
