import numpy as np
import logging
import pandas as pd

from .ioul import get_iou, comp_norm_box_area_inside_roi
from .confBand import confidence_band

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
    #         if no colocations then output is: 0,0,0,...,0,-1
    #         if 2 are colocated then:          0,1,0,0,...,0,-1 OR 0,0,0,...,1,-1 OR 1,0,0,...,0,-1
    #         similarly for 3 and higher co-locations
    #         Can also have: -1 ; 1,-1 ; 0,-1 ; 0,1,-1 ; 0,1,0,-1 etc.
    if debug > 0:
        print('xloc = {}'.format(str(xloc_list)))
        print('median width = {}'.format(median_xwidth))
    is_neigh_coloc = []
    for ii in range(num_elems-1):
        is_neigh_coloc.append(int(xloc_list[ii+1] - xloc_list[ii] < loc_diff_ratio * median_xwidth))
    is_neigh_coloc.append(-1)
    df['is_neigh_coloc'] = is_neigh_coloc

    if debug > 0:
        print('df before neigh coloc:')
        print(df.to_string())

    # compute starting and ending indices for each group of colocated characters using a state machine
    # states: start=0, end=-1, one_found=1, zero_found=2
    # terminal states: -1
    # inputs: 1, 0, -1
    # state transition table:
    # new_state (curr_state, input) =
    #        input ->  0,  1, -1
    # curr_state
    #   |
    #   V
    #   0              2,  1, -1 
    #   1              2,  1, -1 
    #   2              2,  1, -1 
    # output/action table (Mealy machine): action performed when input arrives at current_state
    #                                0 = advance pointer to next number of array, 
    #                               -1 = quit (by going into terminal state), 
    #                                1 = save curr pointer to start_indx
    #                                2 = save curr pointer to end_indx
    # action (curr_state, input) =
    #        input ->        0,       1,      -1
    # curr_state
    #   |
    #   V
    #   0              (1,2,0),   (1,0), (1,2,-1)
    #   1                (2,0),     (0),   (2,-1) 
    #   2              (1,2,0),   (1,0), (1,2,-1)
    start_indx_list = []
    end_indx_list = []
    ii = 0
    curr_state = 'start' 
    fail_safe_ctr = 0
    while True:
        if fail_safe_ctr > len(df):
            print('Warning: State machine exited due to fail safe')
            break

        # terminal states
        if curr_state == 'end':
            break

        curr_row = df.iloc[ii,:]
        curr_input = curr_row['is_neigh_coloc']
        
        if curr_state == 'start':
            if curr_input == 0:
                start_indx_list.append(ii)
                end_indx_list.append(ii)
                ii += 1;
                
                new_state = 'zero_found'
            elif curr_input == 1:
                start_indx_list.append(ii)
                ii += 1;
                
                new_state = 'one_found'
            else: # curr_input == -1:
                start_indx_list.append(ii)
                end_indx_list.append(ii)
                ii += 1;
                
                new_state = 'end'
        elif curr_state == 'one_found':
            if curr_input == 0:
                end_indx_list.append(ii)
                ii += 1;
                
                new_state = 'zero_found'
            elif curr_input == 1:
                ii += 1;
                
                new_state = 'one_found'
            else: # curr_input == -1:
                end_indx_list.append(ii)
                ii += 1;
                
                new_state = 'end'
        elif curr_state == 'zero_found':
            if curr_input == 0:
                start_indx_list.append(ii)
                end_indx_list.append(ii)
                ii += 1;
                
                new_state = 'zero_found'
            elif curr_input == 1:
                start_indx_list.append(ii)
                ii += 1;
                
                new_state = 'one_found'
            else: # curr_input == -1:
                start_indx_list.append(ii)
                end_indx_list.append(ii)
                ii += 1;
                
                new_state = 'end'
        else:
            pass
        curr_state = new_state
        fail_safe_ctr += 1
                
    if debug > 0:
        print('start_indx_list = {}'.format(start_indx_list))
        print('end_indx_list = {}'.format(end_indx_list))

    if len(start_indx_list) !=  len(end_indx_list):
        logger.info('Warning: resolve colocation function failed')
        return df,0
    df_out = df.drop(index=df.index).copy() # copy is just to be safe
    num_coloc = len(df) - len(start_indx_list)

    for ii in range(len(start_indx_list)):
        rows_ov = df[start_indx_list[ii]:(end_indx_list[ii]+1)]
        max_row = rows_ov[rows_ov['score']==np.max(rows_ov['score'])]
        df_out = pd.concat([df_out, max_row])
        
    return df_out, num_coloc

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

def del_outliers_ywidth_inplace(box_y_prop, debug = 1):

    # percentile always removes one or more of the elements
    # use +/- 3 sigma criterion for outlier in conjunction with percentile
    
    [low_cut, hi_cut] = np.percentile(box_y_prop['ywidth'],[1,99])
    mean_val = np.mean(box_y_prop['ywidth'])
    stdval = np.std(box_y_prop['ywidth'], ddof=1)
    if 1: # =0 for debugging non-empty index list
        low_cut = np.min((low_cut, mean_val - 3 * stdval))
        hi_cut = np.max((hi_cut, mean_val + 3 * stdval))
    if debug:
        print(low_cut, hi_cut)
    
    flags_low = box_y_prop['ywidth'] < low_cut
    box_y_prop.drop(index=box_y_prop.index[flags_low], inplace=True)

    flags_hi = box_y_prop['ywidth'] > hi_cut
    box_y_prop.drop(index=box_y_prop.index[flags_hi], inplace=True)

    return        
    
def make_bbox_df_ylines(bbox_roi, boxes_list, classes_list, scores_list, cn, loc_diff_ratio = 1.0, debug = 1):

    # 
    box_y_prop = pd.DataFrame(index = np.arange(len(boxes_list),dtype=int), \
                              columns = ['yloc', 'ywidth'])

    for ii in range(len(boxes_list)):
        bbox = boxes_list[ii]
        # sprint('ii = {}, bbox = {}'.format(ii,bbox))
        xmin, ymin, xmax, ymax = bbox[0], bbox[1], bbox[2], bbox[3]
        box_y_prop.loc[ii,'yloc']   =  0.5 * (ymin + ymax)
        box_y_prop.loc[ii,'ywidth'] =  ymax - ymin

    median_ywidth = np.median(box_y_prop['ywidth'].to_numpy())

    if debug > 0:
        print('median_ywidth = {}'.format(median_ywidth))
        print(box_y_prop.to_string())
    
    # sort by yloc
    box_y_prop.sort_values(by = "yloc", ascending = True, inplace = True)

    if debug > 0:
        print(box_y_prop.to_string())

    # remove boxes whose ywidth are too extreme ie outliers
    del_outliers_ywidth_inplace(box_y_prop, debug = debug)
    
    if debug > 0:
        print(box_y_prop.to_string())

    # compute cluster number
    num_elems = len(box_y_prop)
    cluster_list = []
    cluster_id = 0
    if num_elems > 0:
        cluster_list.append(cluster_id) # first element gets first id
        
        for ii in range(1,num_elems):
            # start a new line of boxes if distance between box centers is greater than one box
            #      works since boxes are sorted in y-direction
            #      no need to check for nearest of all points since we sorted them
            if (box_y_prop.loc[box_y_prop.index[ii],'yloc'] - \
                box_y_prop.loc[box_y_prop.index[ii-1],'yloc']) > (loc_diff_ratio * median_ywidth):
                cluster_id += 1
            cluster_list.append(cluster_id)

        box_y_prop['cluster_id'] = cluster_list
    else:
        box_y_prop['cluster_id'] = []

    if debug > 0:
        print(box_y_prop.to_string())

    df_list = []
    for cc in range(cluster_id+1):
                
        # find boxes in the current cluster
        box_prop_curr = box_y_prop[box_y_prop['cluster_id'] == cc].copy()
        if debug > 0:
            print('index for cluster {} = {}'.format(cc, box_prop_curr.index.tolist()))
        
        boxes_list_curr = [boxes_list[ii] for ii in box_prop_curr.index.tolist()]
        scores_list_curr = [scores_list[ii] for ii in box_prop_curr.index.tolist()]
        classes_list_curr = [classes_list[ii] for ii in box_prop_curr.index.tolist()]

        # create dataframe to store table of boxes for each y line
        df = pd.DataFrame(index = np.arange(len(boxes_list_curr),dtype=int), \
                          columns = ['class', 'score', 'norm_xloc', \
                                     'norm_xwidth','norm_box_area', 'h_w_ratio'])
        for ii in range(len(boxes_list_curr)):
            bbox = boxes_list_curr[ii]
            # don't need comp_norm_ydist
            # bbox_roi is the whole image ; needed for x-dim
            # can't do much with y-dim
            df.iloc[ii,:] = [cn[classes_list_curr[ii]], scores_list_curr[ii], \
                             comp_norm_xloc(bbox_roi, bbox), \
                             comp_norm_xwidth(bbox_roi, bbox), \
                             comp_norm_box_area(bbox_roi, bbox), \
                             comp_h_w_ratio(bbox)]
        
        df_list.append(df)
        
    return df_list

# remove SNO box and letters before it. 
# also remove a single letter punctuation or letter H (-,#,.,/,:,H) after it
def process_SNO_boxes_SN_prefixes(df_sn, verbose = 0, debug = 0):

    if debug > 0:
        verbose = 1
        
    sno_rows = df_sn[df_sn['class'] == 'SNO']
    if len(sno_rows) > 0:

        # delete all SNO boxes since they have been saved
        df_sn = df_sn.loc[lambda df: df['class'] != 'SNO', :]
        
        # choose the SNO with the smallest x-location
        min_xloc_sno = np.min(sno_rows['norm_xloc'])
        sno_row = sno_rows[sno_rows['norm_xloc'] == min_xloc_sno]
           # caution: handle the rare case when 2 sno boxes have the same xloc
           
        if verbose > 0:
            print('sno_row =\n{}'.format(sno_row.to_string()))
        
        max_x = float(sno_row['norm_xloc']) + 0.5 * float(sno_row['norm_xwidth'])
        # keep everything after first sno_box
        df_sn = df_sn[df_sn['norm_xloc'] >= max_x]
    
        if len(df_sn) > 0:
            if df_sn.loc[df_sn.index[0],'class'] == '-' or  \
                df_sn.loc[df_sn.index[0],'class'] == '#' or \
                df_sn.loc[df_sn.index[0],'class'] == '.' or \
                df_sn.loc[df_sn.index[0],'class'] == '/' or \
                df_sn.loc[df_sn.index[0],'class'] == ':':
                df_sn.drop(index=df_sn.index[0], inplace=True)

    # drop SN related prefixes
    # {SN, S/N}x{:,-,#,/,.} U {SNH}
    if len(df_sn) >= 3 and \
        df_sn.loc[df_sn.index[0],'class'] == 'S' and \
        df_sn.loc[df_sn.index[1],'class'] == 'N' and \
        df_sn.loc[df_sn.index[2],'class'] == 'H':
        df_sn.drop(index=df_sn.index[[0,1,2]], inplace=True)
    else:
        if len(df_sn) >= 2 and \
            df_sn.loc[df_sn.index[0],'class'] == 'S' and \
            df_sn.loc[df_sn.index[1],'class'] == 'N':
            df_sn.drop(index=df_sn.index[[0,1]], inplace=True)
        elif len(df_sn) >= 3 and \
            df_sn.loc[df_sn.index[0],'class'] == 'S' and \
            df_sn.loc[df_sn.index[1],'class'] == '/' and \
            df_sn.loc[df_sn.index[2],'class'] == 'N':
            df_sn.drop(index=df_sn.index[[0,1,2]], inplace=True)
        else:
            pass

        if len(df_sn) > 0:
            if df_sn.loc[df_sn.index[0],'class'] == '-' or \
                df_sn.loc[df_sn.index[0],'class'] == '#' or \
                df_sn.loc[df_sn.index[0],'class'] == '.' or \
                df_sn.loc[df_sn.index[0],'class'] == '/' or \
                df_sn.loc[df_sn.index[0],'class'] == ':':
                df_sn.drop(index=df_sn.index[0], inplace=True)

    return df_sn

def compute_str_from_bbox(bbox_sn, boxes_list, classes_list, scores_list, cn, verbose = 1, debug = 1):

    if debug > 0 and verbose == 0:
        verbose = 1
        
    # find boxes overlapping sn box
    df_sn = make_bbox_df(bbox_sn, boxes_list, classes_list, scores_list, cn, debug = debug)
    if len(df_sn) == 0:
        return '', 0.0, 'LOW'
    
    # remove iou=0.0
    df_sn = df_sn[df_sn['iou'] > 0.0]  
    if len(df_sn) == 0:
        return '', 0.0, 'LOW'

    # keep norm_ydist within +/-0.3
    df_sn = df_sn[np.abs(df_sn['norm_ydist']) < 0.3]  
    if len(df_sn) == 0:
        return '', 0.0, 'LOW'

    # sort rows based on norm_xdist
    df_sn = df_sn.sort_values('norm_xloc', ignore_index=True)

    # filter out boxes whose xloc is outside [0,1]
    df_sn = df_sn[ (df_sn['norm_xloc'] >= 0.0) &  (df_sn['norm_xloc'] <= 1.0)]
    if len(df_sn) == 0:
        return '', 0.0, 'LOW'

    if verbose > 0:
        print(df_sn.to_string())

    # filter out small boxes
    area_thresh = 0.1 * np.amax(df_sn.loc[:,'norm_box_area'].to_numpy())
    df_sn = df_sn[df_sn['norm_box_area'] > area_thresh]
    if len(df_sn) == 0:
        return '', 0.0, 'LOW'

    # filter out boxes that lie much above or below the center y-line of bbox_roi
    df_sn = df_sn[df_sn['box_area_ratio'] < 10.0]
    if len(df_sn) == 0:
        return '', 0.0, 'LOW'

    if verbose > 0:
        print(df_sn.to_string())

    # compute norm_box_width and remove boxes in the that very close to 
    #     each other or closely overlapping with each other
    # compute median inter box distance
    median_xwidth = np.median(df_sn['norm_xwidth'].to_numpy())
    df_sn, num_colocated = find_resolve_colocations(df_sn.copy(), median_xwidth, debug = debug)

    if verbose > 0:
        print('resolved {} colocations for df_sn'.format(num_colocated))

    if len(df_sn) == 0:
        return '', 0.0, 'LOW'

    if verbose > 0:
        print(df_sn.to_string())

    # remove first SNO box and chars before it (if SNO was detected)
    # also remove a single letter punctuation or letter H (-,#,.,/,:,H) after it
    # after above processing, if SN prefixes are left then remove them, {SN, S/N}x{:,-,#,/,.} U {SNH}
    df_sn = process_SNO_boxes_SN_prefixes(df_sn, debug = debug)
    if verbose > 0:
        print(df_sn.to_string())

    if len(df_sn) == 0:
        return '', 0.0, 'LOW'

    # compute the string from the dataframe
    sn_str = ''.join(df_sn['class'].to_list())

    conf, conf_band = confidence_band(df_sn['score'], len(df_sn['score']))

    if verbose > 0:
        print(sn_str)
    
    return sn_str, conf, conf_band

def compute_str_from_bbox_o_bb_sn(bbox_sn, boxes_list, classes_list, scores_list, cn, verbose = 1, debug = 1):

    if debug > 0 and verbose == 0:
        verbose = 1
        
    # find boxes overlapping this box, which is the whole image in o_bb_sn
    df_list = make_bbox_df_ylines(bbox_sn, boxes_list, classes_list, scores_list, cn, debug = debug)
    if len(df_list) == 0:
        return '', 0.0, 'LOW'

    sno_detected = []
    str_yline_list = []
    conf_list = []
    conf_band_list = []

    for df_sn in df_list:
        
        # sort rows based on norm_xdist
        df_sn = df_sn.sort_values('norm_xloc')
        # df_sn = df_sn.sort_values('norm_xloc', ignore_index=True)
    
        if verbose > 0:
            print(df_sn.to_string())
    
        # filter out small boxes
        area_thresh = 0.1 * np.amax(df_sn.loc[:,'norm_box_area'].to_numpy())
        df_sn = df_sn[df_sn['norm_box_area'] > area_thresh]
        if len(df_sn) == 0:
            str_yline_list.append('')
            sno_detected.append(0)
            conf_list.append(0.0)
            conf_band_list.append("LOW")
    
        # do NOT filter out horizontal boxes (using h_w_ratio < 1.0) since SNO box is horizontal
        # df_sn = df_sn[df_sn['h_w_ratio'] > 1.0]
        # if len(df_sn) == 0:
        #    return ''
    
        # compute norm_box_width and remove boxes in the that very close to 
        #     each other or closely overlapping with each other
        # compute median inter box distance
        if 1:
            median_xwidth = np.median(df_sn['norm_xwidth'].to_numpy())
            df_sn, num_colocated = find_resolve_colocations(df_sn.copy(), median_xwidth, debug = debug)
        else:
            num_colocated = 0
            
        if verbose > 0:
            print('resolved {} colocations for df_sn'.format(num_colocated))

        if verbose > 0:
            print(df_sn.to_string())
    
        # compute the string from the dataframe
        if len(df_sn) == 0:
            str_yline_list.append('')
            sno_detected.append(0)

            conf_list.append(0.0)
            conf_band_list.append("LOW")
        else:    
            str_yline_list.append(''.join(df_sn['class'].to_list()))
            sno_detected.append(int(np.any(df_sn['class'] == 'SNO')))

            conf, conf_band = confidence_band(df_sn['score'], len(df_sn['score']))
            conf_list.append(conf)
            conf_band_list.append(conf_band)

        if verbose > 0:
            print(str_yline_list[-1])

    # find the longest line without SNO box as output string
    if len(str_yline_list) == 0:
        sn_str = ''
        conf = 0.0
        conf_band = "LOW"
    elif len(str_yline_list) == 1:
        sn_str = str_yline_list[0]
        conf = conf_list[0]
        conf_band = conf_band_list[0]
    else:
        sn_str_len = np.array([(1-sno_detected[ii])*len(str_yline_list[ii]) \
                               for ii in range(len(str_yline_list))])
        indx = np.min(np.nonzero(sn_str_len == np.max(sn_str_len)))
        sn_str = str_yline_list[indx]
        conf = conf_list[indx]
        conf_band = conf_band_list[indx]

    if verbose > 0:
        print(sn_str)

    return sn_str, conf, conf_band

def getClassResults(class_map, bboxes, outputs, label_type):

    if label_type == 'label_not_detected':
        return '', 0.0, 'LOW'
        
    classes = outputs['instances'].pred_classes
    boxes = outputs['instances'].pred_boxes
    scores = outputs['instances'].scores

    classes_list = classes.tolist()
    scores_list = scores.tolist()
    boxes_list = boxes.tensor.tolist()

    cn = list(class_map.values())
    
    # compute sn_str
    bbox_sn  = bboxes[1]
    if np.all(np.array(bbox_sn) == 0):
        sn_str = ''
    else:
        if label_type == 'ln_cp_tp_o_bb':
            sn_str, conf, conf_band = compute_str_from_bbox(bbox_sn, boxes_list, classes_list, scores_list, cn, verbose = 0, debug = 0)
        else: # ln_cp_tp_o_bb_sn
            # here, bbox_sn is the whole image ; needed for xloc calculations
            sn_str, conf, conf_band = compute_str_from_bbox_o_bb_sn(bbox_sn, boxes_list, classes_list, scores_list, cn, verbose = 0, debug = 0)

    return sn_str, conf, conf_band #Siva: Change it with probability/confidence
