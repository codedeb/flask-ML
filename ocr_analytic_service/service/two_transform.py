# USAGE
# python DPM_TESS_Transform_V1.py --input Images/images07 --output Transformed/DeSkewed

import cv2
import numpy as np
import imutils
import argparse
from imutils import paths

import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")

	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]

	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]

	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect

	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))

	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))

	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")

	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

	# return the warped image
	return warped


def order_points_clockwise(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # now, sort the right-most coordinates according to their
    # y-coordinates so we can grab the top-right and bottom-right
    # points, respectively
    rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
    (tr, br) = rightMost

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="int32")


def main(nm):
    # Adjusting Contrast and Brightness, if required
    alpha = 1.0 # Contrast control (1.0-3.0)
    beta = 0 # Brightness control (0-100)
    
    # Cropping Images co-ordinates
    dx1 = 50
    dy1 = 150
    dx2 = 850
    dy2 = 320
    
    #img_as_read = cv2.imread(fl_nm, cv2.IMREAD_GRAYSCALE)
    img_as_read = nm.copy()
    logger.info('in two :%s' % img_as_read)
    # Re-size the image
    img = imutils.resize(img_as_read, width=1000)
    # threshold
    thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)[1]
    # apply open morphology
    #kernel = np.ones((5,5), np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15,15))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    # Canny Edge Detection
    logger.info('before for morph:%s' % morph)
    canny = cv2.Canny(morph, 120, 255, 1)
    # Find the corners
    logger.info('before for canny:%s' % canny)
    corners = cv2.goodFeaturesToTrack(canny,4,0.5,50)
    c_list = []
    logger.info('before for :%s' % corners)
    for corner in corners:
        x,y = corner.ravel()
        c_list.append([int(x), int(y)])
    logger.info('after for :%s' % c_list)

    if(len(c_list) == 4):
        corner_points = np.array([c_list[0], c_list[1], c_list[2], c_list[3]])
        ordered_corner_points = order_points_clockwise(corner_points)
        logger.info('before tuple for : %s')
        ocp = [tuple(x) for x in ordered_corner_points]
        logger.info('after tuple for : %s' % ocp)
        pts = np.array(ocp, dtype = "float32")
        transformed = four_point_transform(img, pts) # Save this image if you need the full transformed image
        # Adjust for Contrast
        adjusted = cv2.convertScaleAbs(transformed, alpha=alpha, beta=beta)
        # Crop the transformed image
        image_crop = transformed[dy1:dy2, dx1:dx2]  # Save this image if you need the cropped, transformed image
        if np.ndim(image_crop)==3:
            return_image = image_crop.copy()
        else:
            return_image = np.stack((image_crop,)*3, axis=-1)
    # cv2.imshow("Original", img)
    # cv2.imshow("Transformed", transformed)
    # cv2.imshow("Adjusted", adjusted)
    # cv2.waitKey(0)
    logger.info('return img from two :%s' % return_image)
    return return_image
