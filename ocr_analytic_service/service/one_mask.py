# -*- coding: utf-8 -*-
"""
Created on Tue May  4 17:49:35 2021

@author: 302016159
"""

import cv2
import numpy as np
import pandas as pd
import os
import math
from sklearn.cluster import DBSCAN
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def displayimg(img):
    return cv2.imshow("image", cv2.resize(img, (800, 600)))


def grey(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def gaussianblur(img, kernel_size=5):
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def medianblur(img, size=9):
    return cv2.medianBlur(img, size)


def binary(img, thresh):
    # ret, thresh1 = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    ret, thresh1 = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)
    return thresh1


def denoise(img):
    return cv2.fastNlMeansDenoising(img, None, 30.0, 7, 21)


def adaptivethresh(img):
    adapt_type = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    thresh_type = cv2.THRESH_BINARY_INV
    return cv2.adaptiveThreshold(img, 255, adapt_type, thresh_type, 21, 2)


def equalize(img, cliplimit=2.0):
    clahe = cv2.createCLAHE(clipLimit=cliplimit, tileGridSize=(8, 8))
    b = clahe.apply(img[:, :, 0])
    g = clahe.apply(img[:, :, 1])
    r = clahe.apply(img[:, :, 2])
    equalized = np.dstack((b, g, r))
    return equalized


def cannyline(img, low_thresh, high_thresh):
    return cv2.Canny(img, low_thresh, high_thresh)


def houghlines(edges):
    rho = 1
    theta = np.pi/180
    threshold = 15
    min_line_length = 300
    max_line_gap = 20
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
    return lines


def processimage(img):
    gray = grey(img)
    blur = medianblur(gray, 9)
    img_dn = denoise(blur)
    bin_img = adaptivethresh(img_dn)
    # cv2.imwrite(os.path.join(out_dir, inp_fil[:-4]+'_lines.jpg'), bin_img)
    lines = houghlines(bin_img)
    return lines


def processlines(lines, df_sort, df_coord, list_slopes, img):
    if len(lines)==0:
        return [], df_coord, df_sort
    for line in lines:
        for x1, y1, x2, y2 in line:
            slp1 = math.atan((float(y2) - y1) / (float(x2) - x1))
            slp = (float(y2) - y1) / (float(x2) - x1)
            arr_coord, list_df = extendcoord(x1, y1, slp, abs(slp1), img.shape[0], img.shape[1])
            df_sort.loc[len(df_sort)] = list_df
            # cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 5)
            for x3, y3, x4, y4 in arr_coord[0]:
                # cv2.line(img, (x3, y3), (x4, y4), (255, 0, 0), 5)
                list_onecoord = [x3, y3, x4, y4]
            # cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 5)
            # cv2.line(img, (x3, y3), (x4, y4), (255, 0, 0), 5)
            # img = cv2.imread(os.path.join(inp_dir, inp_fil))
            # sld = math.atan(m)*180/np.pi
            df_coord.loc[len(df_coord)] = list_onecoord
            list_slopes.append(slp1)
    return list_slopes, df_coord, df_sort


def extendcoord(x1, y1, slope, slope1, wdt, hgt):
    if math.isinf(slope):
        return np.array([int(x1), 0, int(x1), wdt], ndmin=3), [int(x1), int(wdt/2)]
    elif slope==0:
        return np.array([0, int(y1), hgt, int(y1)], ndmin=3), [int(hgt/2), int(y1)]
    else:
        interc = y1 - slope*x1
        y_st1 = interc
        y_st2 = slope*hgt + interc
        x_st1 = -interc/slope
        x_st2 = (wdt-interc)/slope
        if y_st1 > wdt or y_st1 < 0 or y_st2 > wdt or y_st2 < 0:
            return np.array([int(x_st1), 0, int(x_st2), wdt], ndmin=3), [int((x_st1+x_st2)/2), int(wdt/2)]
        else:
            return np.array([0, int(y_st1), hgt, int(y_st2)], ndmin=3), [int(hgt/2), int((y_st1+y_st2)/2)]
    return None


def dbcluster(df_sort, eps=6, min_samples=1):
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(df_sort)
    df_sort['labels'] = list(clustering.labels_)
    return df_sort, list(clustering.labels_)


def reduce_lines(df_coord, df_sort):
    df1 = pd.DataFrame(data=df_sort['labels'].value_counts(), columns=['labels'])
    df1 = df1.reset_index()
    df1.columns = ['labels', 'counts']
    df1 = df1.sort_values(by='counts', ascending=False)
    df1 = df1[0:4]
    list_labels = df1['labels'].tolist()
    
    list_meanlines = []
    for label in list_labels:
        df_labidx = df_sort[df_sort['labels']==label]
        list_indices = df_labidx.index.tolist()
        df_lab = df_coord[df_coord.index.isin(list_indices)]
        list_meanlines.append([int(n) for n in df_lab.mean().tolist()])
    list_x0 = [item for item in list_meanlines if item[0]==0]
    list_y0 = [item for item in list_meanlines if item[1]==0]
    list_intersec = []
    if len(list_x0)!=2 or len(list_y0)!=2:
        return []
    else:
        for itemx in list_x0:
            for itemy in list_y0:
                list_hold = line_intersection(([itemx[0], itemx[1]], [itemx[2], itemx[3]]), ([itemy[0], itemy[1]], [itemy[2], itemy[3]]))
                list_hold = [int(np.round(num)) for num in list_hold]
                list_intersec.append(list_hold)
    return list_intersec


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return [x, y]


def maskimg(img, list_intersec):
    mask = np.zeros(img.shape[0:2], dtype=np.uint8)
    points = np.array(list_intersec)
    points_1 = order_points_old(points)
    slp_d = (math.atan((float(points_1[1][1]) - points_1[0][1]) / (float(points_1[1][0]) - points_1[0][0])))*(180/np.pi)
    points_1 = points_1.astype(int)
    # plotreducedlines(img, points_1)
    points_o = np.array([points_1])
    polyp = cv2.fillConvexPoly(mask, points_o, (255))
    res = cv2.bitwise_and(img, img, mask=mask)
    return res, slp_d


def plotreducedlines(img, arr_inp):
    list_line1 = list(arr_inp[0]) + list(arr_inp[1])
    list_line2 = list(arr_inp[1]) + list(arr_inp[2])
    list_line3 = list(arr_inp[2]) + list(arr_inp[3])
    list_line4 = list(arr_inp[3]) + list(arr_inp[0])
    cv2.line(img, (list_line1[0], list_line1[1]), (list_line1[2], list_line1[3]), (255, 0, 0), 5)
    cv2.line(img, (list_line2[0], list_line2[1]), (list_line2[2], list_line2[3]), (255, 0, 0), 5)
    cv2.line(img, (list_line3[0], list_line3[1]), (list_line3[2], list_line3[3]), (255, 0, 0), 5)
    cv2.line(img, (list_line4[0], list_line4[1]), (list_line4[2], list_line4[3]), (255, 0, 0), 5)
    # cv2.imwrite(os.path.join(out_dir, inp_fil[:-4]+'_redline.jpg'), img)
    return None


def order_points_old(pts):
	rect = np.zeros((4, 2), dtype="float32")

	s = pts.sum(axis=1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]

	diff = np.diff(pts, axis=1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	return rect


def rotateimg(img, theta):
    w = img.shape[1]
    h = img.shape[0]
    x = w/2
    y = h/2
    M = cv2.getRotationMatrix2D((x, y), theta, 1.0)
    return cv2.warpAffine(img, M, (w, h))
    

def main(fl_nm):
    logger.info('flnm : %s' % fl_nm)
    img = cv2.imread(fl_nm)
    img_cp = img.copy()
    logger.info('lines before')
    lines = processimage(img)
    logger.info('lines after')
    list_slopes = []
    df_coord = pd.DataFrame(columns=['x3', 'y3', 'x4', 'y4'])
    df_sort = pd.DataFrame(columns=['x', 'y'])

    list_slopes, df_coord, df_sort = processlines(lines, df_sort, df_coord, list_slopes, img)
    # list_slopes_d = [item*180/np.pi for item in list_slopes]
    df_sort, list_labels = dbcluster(df_sort, eps=20, min_samples=1)
    
    # cv2.imwrite(os.path.join(out_dir, inp_fil[:-4]+'_lines.jpg'), img)
    list_intersec = reduce_lines(df_coord, df_sort)
    if len(list_intersec)!=0:
        res_img, slp_rot = maskimg(img_cp, list_intersec)
        res_img = rotateimg(res_img, slp_rot)
        # cv2.imwrite(os.path.join(out_dir, inp_fil[:-4]+'_mask.jpg'), res_img)
    else:
        print("Unable to process image!")
        res_img = img_cp

    # dct_slopes[inp_fil] = list_slopes_d
    # dct_coord[inp_fil] = df_coord
    # dct_df[inp_fil] = df_sort
    # dct_clust[inp_fil] = list_labels
    # dct_intersec[inp_fil] = list_intersec
    # cv2.imwrite(os.path.join(out_dir, inp_fil[:-4]+'_box.jpg'), img)
    # print(inp_fil+' done!')
    return res_img
