import logging
from .inferenceSegmentation import clean_class
from .modelArtifacts import detector
from .confBand import confidence_band
from wrapper_service.constants import ModelDetails

logger = logging.getLogger(__name__)

def check_bbox1_overlap_bbox2(bbox1, bbox2):
    if bbox1 is None or bbox2 is None:
        return False
    # atleast one corner of bbox1 should be inside bbox2
    res = check_pt_in_bbox([bbox1[0],bbox1[1]], bbox2) or \
          check_pt_in_bbox([bbox1[0],bbox1[3]], bbox2) or \
          check_pt_in_bbox([bbox1[2],bbox1[1]], bbox2) or \
          check_pt_in_bbox([bbox1[2],bbox1[3]], bbox2)
    return res

def check_pt_in_bbox(pt, bbox):
    x, y = pt[0], pt[1]
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
    return (x > xmin) and (y > ymin) and (x < xmax) and (y < ymax)
    
def check_bbox1_inside_bbox2(bbox1, bbox2, use_centroid=True):
    xmin1, ymin1, xmax1, ymax1 = bbox1[0], bbox1[1], bbox1[2], bbox1[3]
    xmin2, ymin2, xmax2, ymax2 = bbox2[0], bbox2[1], bbox2[2], bbox2[3]
    if use_centroid:
        centx1 = 0.5 * (xmin1 + xmax1)
        centy1 = 0.5 * (ymin1 + ymax1)
        return (centx1 > xmin2) and (centy1 > ymin2) and (centx1 < xmax2) and (centy1 < ymax2)
    else:
        return (xmin1 > xmin2) and (ymin1 > ymin2) and (xmax1 < xmax2) and (ymax1 < ymax2)

def compute_shroud_type(dct_out):

    result = "invalid" # must be one of: "o_bb_not_detected", "o_bb", "o_bb_t2"
    
    if dct_out["o_bb"]["box"] is None and dct_out["o_bb_t2"]["box"] is None:
        result = "o_bb_not_detected"
    else:
        if dct_out["o_bb"]["box"] is None:
            result = "o_bb_t2"
        else:
            if dct_out["o_bb_t2"]["box"] is None:
                result = "o_bb"
            else:    
                # now both boxes are not None
                if dct_out["o_bb"]["confValue"] > dct_out["o_bb_t2"]["confValue"]:
                    result = "o_bb"
                else:
                    result = "o_bb_t2"
    return result

def img_segmenter_shrouds(img, model_params):
    logger.info("Running image segmenter for shrouds...")

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
    predictor = detector(ModelDetails.shroud_seg_config_path, ModelDetails.shroud_seg_model_path,ModelDetails.shroud_seg_threshold)
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
            multhtst = 0.2
            multwded = 0.1
            multhted = 0.2
        elif class_map[index] == 'seg':
            multwdst = 0.1
            multhtst = 0.1
            multwded = 0.1
            multhted = 0.1
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
    # expand outer bounding box to include all boxes inside it
    #
    if True:
        shroud_type = compute_shroud_type(dct_out)
    
        if shroud_type == 'o_bb_not_detected':
            logger.info('o_bb and o_bb_t2 not detected')
        else:
            if shroud_type == 'o_bb':
    
                # if non o_bb boxes do not overlap with outer bounding box then do not use them
                #  to expand the o_bb ; we have to drop the concerned non o_bb box completely
                tmp_class_list = []
                for cc in ["sn", "seg", "tl", "bl", "dn"]:
                    if check_bbox1_overlap_bbox2(dct_out[cc]["box"], dct_out["o_bb"]["box"]):
                        tmp_class_list.append(cc)
                    else:
                        if dct_out[cc]["box"] is not None:
                            logger.info('dropping {} from o_bb'.format(cc))
                        dct_out[cc]["segment"] = img
                        dct_out[cc]["box"] = None
                        dct_out[cc]["confValue"] = 0
                        dct_out[cc]["confBand"] = 'LOW'
                    
                # initialize result
                bbr = dct_out["o_bb"]["box"] # bbr <=> bbox_result
                # in code below, dct_out[cc]["box"][0] != 0 condition is another 
                # layer of safety on top of None check
                logger.info('o_bb before expansion={}'.format(str(bbr)))
                    
                # modify xmin, ymin, xmax, and ymax (ii = 0, 1, 2, 3 resp.)
                if len(tmp_class_list) > 0:
                    for ii in range(4):
                        for cc in tmp_class_list:
                            if dct_out[cc]["box"] is not None and dct_out[cc]["box"][ii] != 0:
                                if ii == 0 or ii == 1:
                                    bbr[ii] = min(dct_out[cc]["box"][ii], bbr[ii]) # xmin, ymin modification
                                else:
                                    bbr[ii] = max(dct_out[cc]["box"][ii], bbr[ii]) # xmax, ymax modification
    
                dct_out["o_bb"]["box"] = bbr
                dct_out["o_bb"]["segment"] = img[bbr[1]:bbr[3],bbr[0]:bbr[2],:]
    
                logger.info('o_bb after expansion={}'.format(str(bbr)))
                
            else: # o_bb_t2
                tmp_class_list = []
                for cc in ["sn_t2", "dn_t2"]:
                    if check_bbox1_overlap_bbox2(dct_out[cc]["box"], dct_out["o_bb_t2"]["box"]):
                        tmp_class_list.append(cc)
                    else:
                        if dct_out[cc]["box"] is not None:
                            logger.info('dropping {} from o_bb_t2'.format(cc))
                        dct_out[cc]["segment"] = img
                        dct_out[cc]["box"] = None
                        dct_out[cc]["confValue"] = 0
                        dct_out[cc]["confBand"] = 'LOW'
    
                # initialize result
                bbr = dct_out["o_bb_t2"]["box"] # bbr <=> bbox_result
    
                # in code below, dct_out[cc]["box"][0] != 0 condition is another 
                # layer of safety on top of None check
    
                # modify xmin, ymin, xmax, and ymax (ii = 0, 1, 2, 3 resp.)
                if len(tmp_class_list) > 0:
                    for ii in range(4):
                        for cc in tmp_class_list:
                            if dct_out[cc]["box"] is not None and dct_out[cc]["box"][ii] != 0:
                                if ii == 0 or ii == 1:
                                    bbr[ii] = min(dct_out[cc]["box"][ii], bbr[ii]) # xmin, ymin modification
                                else:
                                    bbr[ii] = max(dct_out[cc]["box"][ii], bbr[ii]) # xmax, ymax modification
    
                dct_out["o_bb_t2"]["box"] = bbr
                dct_out["o_bb"]["segment"] = img[bbr[1]:bbr[3],bbr[0]:bbr[2],:]

    #            
    # clean raw dict and form output
    #
    seg_out = {"O_BB": {"segment": img, "box": [0,0,0,0], "confValue": None, "confBand": None},
               "SN":   {"segment": img, "box": [0,0,0,0], "confValue": None, "confBand": None},
               "SEG":  {"segment": img, "box": [0,0,0,0], "confValue": None, "confBand": None}}
    
    shroud_type = compute_shroud_type(dct_out)

    if shroud_type != 'o_bb_not_detected':

        if shroud_type == 'o_bb':
            bbox = dct_out["o_bb"]["box"]
            xmin0, ymin0 = bbox[0], bbox[1]
    
            if dct_out["o_bb"]["confValue"] > 0:
                seg_out["O_BB"]["segment"]   = dct_out["o_bb"]["segment"]
                seg_out["O_BB"]["box"]       = [0,0,0,0]
                seg_out["O_BB"]["confValue"] = dct_out["o_bb"]["confValue"]
                seg_out["O_BB"]["confBand"]  = dct_out["o_bb"]["confBand"]
            if dct_out["sn"]["confValue"] > 0:
                seg_out["SN"]["segment"]   = dct_out["sn"]["segment"]
                seg_out["SN"]["box"]   = [x-y for x,y in zip(dct_out["sn"]["box"],[xmin0, ymin0, xmin0, ymin0])]
                seg_out["SN"]["confValue"] = dct_out["sn"]["confValue"]
                seg_out["SN"]["confBand"]  = dct_out["sn"]["confBand"]
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

