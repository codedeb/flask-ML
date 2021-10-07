# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 14:02:22 2021

@author: 302016159
"""

import numpy as np

def confidence_band(scores_list, lgt):
    if len(scores_list) > 0:
        # conf = round(sum(scores_list) / len(scores_list), 3)
        scores_list = [float(item) for item in scores_list]
        conf = np.prod(scores_list)
        if len(scores_list) != lgt:
            conf_band = "LOW"
            conf = 0
        elif conf > 0.9:
            conf_band = "HIGH"
        elif conf >= 0.6 and conf <= 0.9:
            conf_band = "MEDIUM"
        elif conf < 0.6:
            conf_band = "LOW"

    else:
        if len(scores_list) == 0:
            conf = 0
            conf_band = "LOW"
    return conf, conf_band


def overall_band(list_conf_band):
    dct_bandmap = {"HIGH":2, "MEDIUM":1, "LOW":0}
    dct_outmap = {v:k for k, v in dct_bandmap.items()}
    list_conf_map = [dct_bandmap[item] for item in list_conf_band]
    lowest_conf = min(list_conf_map)
    return dct_outmap[lowest_conf]