import itertools
import time
ious= []
def calculate_IOU(obj_list):
    st = time.time()
    for x,y in itertools.combinations(mylist, 2):
        x1, y1, x2, y2 = x	
        x3, y3, x4, y4 = y
        x_inter1 = max(x1, x3)
        y_inter1 = max(y1, y3)
        x_inter2 = min(x2, x4)
        y_inter2 = min(y2, y4)
        width_inter = abs(x_inter2 - x_inter1)
        height_inter = abs(y_inter2 - y_inter1)
        area_inter = width_inter * height_inter
        width_box1 = abs(x2 - x1)
        height_box1 = abs(y2 - y1)
        width_box2 = abs(x4 - x3)
        height_box2 = abs(y4 - y3)
        area_box1 = width_box1 * height_box1
        area_box2 = width_box2 * height_box2
        area_union = area_box1 + area_box2 - area_inter
        iou = area_inter / area_union
        ious.append(iou)
    res = time.time() -st
    print(res)
    print(len(ious))
    return ious
mylist = [[117, 58, 183, 141],
[295, 194, 314, 207],
[30, 235, 118, 364],
[83, 296, 146, 448],
[244, 235, 380, 332],
[76, 93, 85, 174],
[248, 112, 272, 214],
[248, 38, 292, 72],
[288, 32, 313, 199],
[118, 157, 239, 228]]

mylist = [[117, 58, 183, 141],
[295, 194, 314, 207],
[118, 157, 239, 228]]
#print(calculate_IOU(mylist))


def iou_calc(mylist, thresh=0.8):
    list_return = []
    for x,y in itertools.combinations(mylist, 2):
        a = get_iou(x, y)
        if a>0:
            list_return.append([mylist.index(x), mylist.index(y)])
    return list_return


def get_iou(bb1, bb2):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    bb1 : list : [x1, y1, x2, y2]
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner
    bb2 : list : [x1, y1, x2, y2]
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner

    Returns
    -------
    float
        in [0, 1]
    """
    if 0:
        assert bb1[0] < bb1[2]
        assert bb1[1] < bb1[3]
        assert bb2[0] < bb2[2]
        assert bb2[1] < bb2[3]
    else:
        if (bb1[0] == bb1[2]) or (bb1[1] == bb1[3]) or (bb2[0] == bb2[2]) or (bb2[1] == bb2[3]):
            return 0.0
        
    # determine the coordinates of the intersection rectangle
    x_left = max(bb1[0], bb2[0])
    y_top = max(bb1[1], bb2[1])
    x_right = min(bb1[2], bb2[2])
    y_bottom = min(bb1[3], bb2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of both AABBs
    bb1_area = (bb1[2] - bb1[0]) * (bb1[3] - bb1[1])
    bb2_area = (bb2[2] - bb2[0]) * (bb2[3] - bb2[1])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection_area / float(bb1_area + bb2_area - intersection_area)
    assert iou >= 0.0
    assert iou <= 1.0
    return iou

def comp_norm_box_area_inside_roi(bb1, bb2):
    """
    Calculate the area of bounding box (bb1) inside roi box (bb2).

    Parameters
    ----------
    bb1 : list : [x1, y1, x2, y2]
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner
    bb2 : list : [x1, y1, x2, y2]
        The (x1, y1) position is at the top left corner,
        the (x2, y2) position is at the bottom right corner

    Returns
    -------
    float
        in [0, 1]
    """
    if 0:
        assert bb1[0] < bb1[2]
        assert bb1[1] < bb1[3]
        assert bb2[0] < bb2[2]
        assert bb2[1] < bb2[3]
    else:
        if (bb1[0] == bb1[2]) or (bb1[1] == bb1[3]) or (bb2[0] == bb2[2]) or (bb2[1] == bb2[3]):
            return 0.0

    # determine the coordinates of the intersection rectangle
    x_left = max(bb1[0], bb2[0])
    y_top = max(bb1[1], bb2[1])
    x_right = min(bb1[2], bb2[2])
    y_bottom = min(bb1[3], bb2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    # The intersection of two axis-aligned bounding boxes is always an
    # axis-aligned bounding box
    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    # compute the area of bb1
    bb1_area = (bb1[2] - bb1[0]) * (bb1[3] - bb1[1])

    # compute the ratio of intersection area and area of bb1
    norm_box_area = intersection_area / float(bb1_area)

    assert norm_box_area >= 0.0
    assert norm_box_area <= 1.0

    return norm_box_area

def test_comp_norm_box_area_inside_roi():
        
    mylist = [[2,1,3,3],
              [1,2,4,4]]
    
    for x,y in itertools.permutations(mylist, 2):
        a = comp_norm_box_area_inside_roi(x, y)
        print(x)
        print(y)
        print(a)
        

    