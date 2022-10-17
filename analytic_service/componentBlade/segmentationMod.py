import cv2
from .inferenceSegmentation import clean_class
from .modelArtifacts import detector
from .confBand import confidence_band
import logging
from wrapper_service.constants import ModelDetails


global segmentation_predictor
global segmentation_predictor_available
segmentation_predictor_available=False

"""
logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
"""
logger = logging.getLogger(__name__)

def img_segmenter(img):
    global segmentation_predictor
    global segmentation_predictor_available
    img_ht = img.shape[0]
    img_wd = img.shape[1]
    class_map = {0: 'pr', 1: 'psn', 2: 'obb_b', 3: 'snb',4:'sn'}
    dct_out_segs = dict.fromkeys(list(class_map.values()))
    dct_out_box = dict.fromkeys(list(class_map.values()))
  
    # Make prediction
    #uncomment if condition and enable global variables when model needs to be initialized only once
    if not segmentation_predictor_available:
        logger.info("Initializing Segmentation Predictor")
        segmentation_predictor = detector(ModelDetails.segmentation_config_path, ModelDetails.segmentation_model_path,ModelDetails.segmentation_threshold)
        segmentation_predictor_available=True
    outputs = segmentation_predictor(img)
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
            logger.info('error', e)
        if class_map[index] == 'psn':
            multwdst = 0
            multhtst = 0
            multwded = 0
            multhted = 0
        elif class_map[index] == 'obb_b':
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
        
    # Create boxes relative to ROI
    list_ROI_box = dct_out_box['obb_b'].copy()
    list_ROI_box = [list_ROI_box[0], list_ROI_box[1], list_ROI_box[0], list_ROI_box[1]]
    for seg in class_map_up.values():
        dct_out_box[seg] = list(a-b for (a, b) in zip(dct_out_box[seg], list_ROI_box))

    # Scale output images and boxes to a certain size
    roi_out_ht = 1000
    rat = roi_out_ht/dct_out_segs['obb_b'].shape[0] # Set this variable to 1 if scaling shouldn't be applied

    for seg in class_map_up.values():
        im_seg = dct_out_segs[seg].copy()
        im_resize = cv2.resize(im_seg, (int(im_seg.shape[1]*rat), int(im_seg.shape[0]*rat)), interpolation = cv2.INTER_AREA)
        dct_out_segs[seg] = im_resize
        box_seg = dct_out_box[seg].copy()
        box_seg = [int(item*rat) for item in box_seg]
        dct_out_box[seg] = box_seg

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
            out_obj['confBand'] = "LOW"
            out_obj['box'] = [0, 0, 0, 0]
            dct_out[seg] = out_obj
    return dct_out