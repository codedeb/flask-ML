from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from itertools import combinations, permutations


def detector(config_path, model_weight_path, threshold):
    cfg = get_cfg()
    cfg.merge_from_file(config_path)
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = threshold  # set threshold for this model
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.WEIGHTS = model_weight_path
    predictor = DefaultPredictor(cfg)
    return predictor

def iou_calc(mylist, thresh=0.5):
    list_return = []
    for x,y in combinations(mylist, 2):
        a = get_inter(x, y)
        # print(a)
        if a>thresh:
            list_return.append([mylist.index(x), mylist.index(y)])
    return list_return

def get_iou(bb1, bb2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes. Parameters
    ----------
    bb1 : list : [x1, y1, x2, y2]
    The (x1, y1) position is at the top left corner,
    the (x2, y2) position is at the bottom right corner
    bb2 : list : [x1, y1, x2, y2]
    The (x1, y1) position is at the top left corner,
    the (x2, y2) position is at the bottom right corner Returns
    -------
    float
    in [0, 1]
    """
    assert bb1[0] < bb1[2]
    assert bb1[1] < bb1[3]
    assert bb2[0] < bb2[2]
    assert bb2[1] < bb2[3] # determine the coordinates of the intersection rectangle
    x_left = max(bb1[0], bb2[0])
    y_top = max(bb1[1], bb2[1])
    x_right = min(bb1[2], bb2[2])
    y_bottom = min(bb1[3], bb2[3]) 
    if x_right < x_left or y_bottom < y_top:
        return 0.0 # The intersection of two axis-aligned bounding boxes is always an

    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top) # compute the area of both AABBs
    bb1_area = (bb1[2] - bb1[0]) * (bb1[3] - bb1[1])
    bb2_area = (bb2[2] - bb2[0]) * (bb2[3] - bb2[1]) # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou

def get_inter(bb1, bb2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes. Parameters
    ----------
    bb1 : list : [x1, y1, x2, y2]
    The (x1, y1) position is at the top left corner,
    the (x2, y2) position is at the bottom right corner
    bb2 : list : [x1, y1, x2, y2]
    The (x1, y1) position is at the top left corner,
    the (x2, y2) position is at the bottom right corner Returns
    -------
    float
    in [0, 1]
    """
    assert bb1[0] < bb1[2]
    assert bb1[1] < bb1[3]
    assert bb2[0] < bb2[2]
    assert bb2[1] < bb2[3] # determine the coordinates of the intersection rectangle
    x_left = max(bb1[0], bb2[0])
    y_top = max(bb1[1], bb2[1])
    x_right = min(bb1[2], bb2[2])
    y_bottom = min(bb1[3], bb2[3]) 

    if x_right < x_left or y_bottom < y_top:
        return 0.0 # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top) # compute the area of both AABBs
    bb1_area = (bb1[2] - bb1[0]) * (bb1[3] - bb1[1])
    bb2_area = (bb2[2] - bb2[0]) * (bb2[3] - bb2[1]) # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    inter = intersection_area / min(bb1_area, bb2_area)
    assert inter >= 0.0
    assert inter <= 1.0
    return inter

def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)
    return list_object


