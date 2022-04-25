import numpy as np
import logging
import pandas as pd

from ioul import get_iou, comp_norm_box_area_inside_roi

logger = logging.getLogger(__name__)

def comp_norm_ydist(bbox_roi, bbox):
    xmin, ymin, xmax, ymax = bbox_roi[0], bbox_roi[1], bbox_roi[2], bbox_roi[3]
    center_line_y =  0.5 * (ymin + ymax)
    roi_ysize = ymax - ymin
    assert(ymax > ymin)
    
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
    return (0.5 * (ymin + ymax) - center_line_y) / roi_ysize

def comp_norm_xloc(bbox_roi, bbox):
    xmin, ymin, xmax, ymax = bbox_roi[0], bbox_roi[1], bbox_roi[2], bbox_roi[3]
    left_x =  xmin
    roi_xsize = xmax - xmin
    assert(xmax > xmin)
    
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
    return (0.5 * (xmin + xmax) - left_x) / roi_xsize

def comp_norm_xwidth(bbox_roi, bbox):
    xmin, ymin, xmax, ymax = bbox_roi[0], bbox_roi[1], bbox_roi[2], bbox_roi[3]
    roi_xsize = xmax - xmin
    assert(xmax > xmin)
    
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
    return (xmax - xmin) / roi_xsize

def comp_norm_box_area(bbox_roi, bbox):
    xmin, ymin, xmax, ymax = bbox_roi[0], bbox_roi[1], bbox_roi[2], bbox_roi[3]
    roi_area =  (xmax - xmin) * (ymax - ymin)
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
    box_area =  (xmax - xmin) * (ymax - ymin)
    return box_area / roi_area

def comp_h_w_ratio(bbox):
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
    return (ymax - ymin) / (xmax - xmin)

def comp_box_area_ratio_above_center_y_line(bbox, bbox_roi):
    xmin, ymin, xmax, ymax = bbox_roi[0], bbox_roi[1], bbox_roi[2], bbox_roi[3]
    center_line_y =  0.5 * (ymin + ymax)
    
    xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
    
    if (ymin >= center_line_y) or (ymax <= center_line_y):
        box_area_ratio = 1000.0 # TODO: try to use np.inf for correctness here
    else:
        box_area_ratio = np.abs(ymax - center_line_y) / np.abs(center_line_y - ymin)
        box_area_ratio = np.max((box_area_ratio, 1.0/box_area_ratio))
        
    return box_area_ratio
    
def find_resolve_colocations(df, median_xwidth, loc_diff_ratio = 0.1, debug = 0):
    num_colocated = 0
    xloc_list = df['norm_xloc'].to_numpy()
    num_elems = len(xloc_list)
    if num_elems == 1:
        return df, num_colocated

    # compute colocation column  
    if debug> 0:
        logger.info('xloc = {}'.format(str(xloc_list)))
        logger.info('median width = {}'.format(median_xwidth))
    is_neigh_coloc = []
    for ii in range(num_elems-1):
        is_neigh_coloc.append(int(xloc_list[ii+1] - xloc_list[ii] < loc_diff_ratio * median_xwidth))
    is_neigh_coloc.append(-1)
    df['is_neigh_coloc'] = is_neigh_coloc

    if debug > 0:
        logger.info('df before neigh coloc:')
        logger.info(df.to_string())
        
    num_colocated = np.count_nonzero(df['is_neigh_coloc'].to_numpy() == 1)
    num_colocs = num_colocated 
    while (num_colocs > 0):
        num_elems = len(df)
        if num_elems <= 1:
            break
        
        # scan from beginning of array till last but one
        found = 0
        for ii in range(num_elems-1):
            if is_neigh_coloc[ii] == 1:
                found = 1
                break
        if not found:
            break

        # remove appropriate coloc neighbor and recompute coloc flag
        if df.loc[df.index[ii],'score'] > df.loc[df.index[ii+1],'score']:
            if ii == num_elems-2:
                new_coloc_flag = -1
            else:
                if df.loc[df.index[ii+1],'is_neigh_coloc'] ==  1:
                    new_coloc_flag = 1
                else:
                    new_coloc_flag = 0
            df.loc[df.index[ii],'is_neigh_coloc'] = new_coloc_flag
            df.drop(index=df.index[ii+1], inplace=True)
        else:
            df.drop(index=df.index[ii], inplace=True)

        num_colocs = np.count_nonzero(df['is_neigh_coloc'].to_numpy() == 1)

    return df, num_colocated 

def make_bbox_df(bbox_roi, boxes_list, classes_list, scores_list, cn, debug):

    # create dataframe to store table of boxes
    df = pd.DataFrame(index = np.arange(len(boxes_list),dtype=int), \
                      columns = ['class', 'score', 'iou', 'norm_ydist', 'norm_xloc', \
                                 'norm_xwidth','norm_box_area', 'norm_area_in_roi', 'h_w_ratio', \
                                 'box_area_ratio'])
    for ii in range(len(boxes_list)):
        bbox = boxes_list[ii]
        df.iloc[ii,:] = [cn[classes_list[ii]], scores_list[ii], get_iou(bbox, bbox_roi), \
                         comp_norm_ydist(bbox_roi, bbox), \
                         comp_norm_xloc(bbox_roi, bbox), \
                         comp_norm_xwidth(bbox_roi, bbox), \
                         comp_norm_box_area(bbox_roi, bbox), \
                         comp_norm_box_area_inside_roi(bbox, bbox_roi), \
                         comp_h_w_ratio(bbox), \
                         comp_box_area_ratio_above_center_y_line(bbox, bbox_roi)]
    return df

def compute_str_from_bbox(bbox_sn, boxes_list, classes_list, scores_list, cn, verbose = 1, debug = 1):

    if debug > 0 and verbose == 0:
        verbose = 1
        
    # find boxes overlapping this box, e.g. sn, seg etc
    df_sn = make_bbox_df(bbox_sn, boxes_list, classes_list, scores_list, cn, debug = debug)
    if len(df_sn) == 0:
        return ''
    
    # remove iou=0.0
    df_sn = df_sn[df_sn['iou'] > 0.0]  
    if len(df_sn) == 0:
        return ''

    # keep norm_ydist within +/-0.3
    df_sn = df_sn[np.abs(df_sn['norm_ydist']) < 0.3]  
    if len(df_sn) == 0:
        return ''

    # sort rows based on norm_xdist
    df_sn = df_sn.sort_values('norm_xloc', ignore_index=True)

    # filter out boxes whose xloc is outside [0,1]
    df_sn = df_sn[ (df_sn['norm_xloc'] >= 0.0) &  (df_sn['norm_xloc'] <= 1.0)]
    if len(df_sn) == 0:
        return ''

    if verbose > 0:
        logger.info(df_sn.to_string())

    # filter out small boxes
    area_thresh = 0.1 * np.amax(df_sn.loc[:,'norm_box_area'].to_numpy())
    df_sn = df_sn[df_sn['norm_box_area'] > area_thresh]
    if len(df_sn) == 0:
        return ''

    # filter out horizontal boxes using h_w_ratio < 1.0
    df_sn = df_sn[df_sn['h_w_ratio'] > 1.0]
    if len(df_sn) == 0:
        return ''

    # filter out boxes that lie much above or below the center y-line of bbox_roi
    df_sn = df_sn[  df_sn['box_area_ratio'] < 10.0 ]
    if len(df_sn) == 0:
        return ''

    if verbose > 0:
        logger.info(df_sn.to_string())

    # compute norm_box_width and remove boxes in the that very close to 
    #     each other or closely overlapping with each other
    # compute median inter box distance
    median_xwidth = np.median(df_sn['norm_xwidth'].to_numpy())
    df_sn, num_colocated = find_resolve_colocations(df_sn.copy(), median_xwidth, debug = debug)

    if verbose > 0:
        logger.info('resolved {} colocations for df_sn'.format(num_colocated))

    if len(df_sn) == 0:
        return ''

    if verbose > 0:
        logger.info(df_sn.to_string())

    # compute the string from the dataframe
    sn_str = ''.join(df_sn['class'].to_list())

    if verbose > 0:
        logger.info(sn_str)

    return sn_str

def getClassResults(class_map, bboxes, outputs):
        
    classes = outputs['instances'].pred_classes
    boxes = outputs['instances'].pred_boxes
    scores = outputs['instances'].scores

    classes_list = classes.tolist()
    scores_list = scores.tolist()
    boxes_list = boxes.tensor.tolist()

    cn = list(class_map.values())
    
    # compute sn_str
    bbox_sn  = bboxes[0]
    if np.all(np.array(bbox_sn) == 0):
        sn_str = ''
    else:
        sn_str = compute_str_from_bbox(bbox_sn, boxes_list, classes_list, scores_list, cn, verbose = 0, debug = 0)

    # for type2 shrouds we need to delete SNH from the beginning of the serial number
    if sn_str.startswith('SNH'):
        sn_str = sn_str.replace('SNH','')

    # compute seg_str
    bbox_seg = bboxes[1]
    if np.all(np.array(bbox_seg) == 0):
        seg_str = ''
    else:
        seg_str = compute_str_from_bbox(bbox_seg, boxes_list, classes_list, scores_list, cn, verbose = 0, debug = 0)

    # compute final OCR string
    if len(seg_str)>2:
        labelDict=sn_str
    else:    
        labelDict = sn_str + '-' + seg_str

    return labelDict,0.9 #Siva: Change it with probability/confidence
