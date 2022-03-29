import logging
from .inferenceSegmentation import clean_class
from .modelArtifacts import detector
from .confBand import confidence_band
from ocr_wrapper_service.constants import ModelDetails

logger = logging.getLogger(__name__)

def img_segmenter_shrouds(img, model_params):
    logger.info("Segment Input: %s" % img)

    model_params_seg = model_params["shroud"]["segmentation"]
    img_ht = img.shape[0]
    img_wd = img.shape[1]
    class_map = {int(k):v for k,v in model_params_seg["class_map"].items()}

    dct_out_segs = dict.fromkeys(list(class_map.values()))
    dct_out_box = dict.fromkeys(list(class_map.values()))
    # json line for model from Box: "model_dir": "C:\\Users\\212070706\\Box\\Capital Parts Lifing\\Intelligent Data Management\\Analytics\\IDM SNO OCR\\Shroud_Models\\Segmentation\\Version3",
    # config_path       = os.path.join(model_params_seg["model_dir"], model_params_seg["model_config"])
    # model_weight_path = os.path.join(model_params_seg["model_dir"], model_params_seg["model_file"])
    # threshold = float(model_params_seg["threshold"])

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
        if class_map[index] == 'sn':
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
    
    #            
    # clean raw dict and form output
    #
    seg_out = {"O_BB": {"segment": img, "box": [0,0,0,0], "confValue": None, "confBand": None},
               "SN":   {"segment": img, "box": [0,0,0,0], "confValue": None, "confBand": None},
               "SEG":  {"segment": img, "box": [0,0,0,0], "confValue": None, "confBand": None}}
    
    # check which type of shroud layout was discovered
    if dct_out["o_bb"]["confValue"] > dct_out["o_bb_t2"]["confValue"]:
        bbox = dct_out["o_bb"]["box"]
        xmin0, ymin0 = bbox[0], bbox[1]

        if dct_out["o_bb"]["confValue"] > 0:
            seg_out["O_BB"]["segment"] = dct_out["o_bb"]["segment"]
            seg_out["O_BB"]["box"] = [0,0,0,0]
            seg_out["O_BB"]["confValue"] = dct_out["o_bb"]["confValue"]
            seg_out["O_BB"]["confBand"] = dct_out["o_bb"]["confBand"]
        if dct_out["bl"]["confValue"] > 0:
            seg_out["SN"]["segment"] = dct_out["bl"]["segment"]
            seg_out["SN"]["box"] = [x-y for x,y in zip(dct_out["bl"]["box"],[xmin0, ymin0, xmin0, ymin0])]
            seg_out["SN"]["confValue"] = dct_out["bl"]["confValue"]
            seg_out["SN"]["confBand"] = dct_out["bl"]["confBand"]
        if dct_out["seg"]["confValue"] > 0:
            seg_out["SEG"]["segment"] = dct_out["seg"]["segment"]
            seg_out["SEG"]["box"] = [x-y for x,y in zip(dct_out["seg"]["box"],[xmin0, ymin0, xmin0, ymin0])]
            seg_out["SEG"]["confValue"] = dct_out["seg"]["confBand"]
            seg_out["SEG"]["confBand"] = dct_out["seg"]["confValue"]
    else:
        bbox = dct_out["o_bb_t2"]["box"]
        xmin0, ymin0 = bbox[0], bbox[1]

        if dct_out["o_bb_t2"]["confValue"] > 0:
            seg_out["O_BB"]["segment"] = dct_out["o_bb_t2"]["segment"]
            seg_out["O_BB"]["box"] = [0,0,0,0]
            seg_out["O_BB"]["confValue"] = dct_out["o_bb_t2"]["confValue"]
            seg_out["O_BB"]["confBand"] = dct_out["o_bb_t2"]["confBand"]
        if dct_out["sn_t2"]["confValue"] > 0:
            seg_out["SN"]["segment"] = dct_out["sn_t2"]["segment"]
            seg_out["SN"]["box"] = [x-y for x,y in zip(dct_out["sn_t2"]["box"],[xmin0, ymin0, xmin0, ymin0])]
            seg_out["SN"]["confValue"] = dct_out["sn_t2"]["confValue"]
            seg_out["SN"]["confBand"] = dct_out["sn_t2"]["confBand"]
        if dct_out["dn_t2"]["confValue"] > 0:
            seg_out["SEG"]["segment"] = dct_out["dn_t2"]["segment"]
            seg_out["SEG"]["box"] = [x-y for x,y in zip(dct_out["dn_t2"]["box"],[xmin0, ymin0, xmin0, ymin0])]
            seg_out["SEG"]["confValue"] = dct_out["dn_t2"]["confValue"]
            seg_out["SEG"]["confBand"] = dct_out["dn_t2"]["confBand"]
                   

    return seg_out

