def clean_class(classes_list, scores_list, boxes_list, class_names):
    clean_box_list = []
    clean_classes_list = []
    clean_scores_list = []
    for clas_name in class_names:
        list_hold_idx = []
        for index, clas in enumerate(classes_list):
            if clas == clas_name:
                list_hold_idx.append(index)
        scores_sublist = [scores_list[i] for i in list_hold_idx]
        if len(scores_sublist) > 0:
            max_score = max(scores_sublist)
            max_score_idx = scores_list.index(max_score)
            clean_box_list.append(boxes_list[max_score_idx])
            clean_classes_list.append(classes_list[max_score_idx])
            clean_scores_list.append(scores_list[max_score_idx])
        else:
            continue
    return clean_box_list, clean_classes_list, clean_scores_list
