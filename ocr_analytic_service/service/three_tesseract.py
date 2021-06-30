# USAGE
# python DPM_TESS_Quick_Run_RoI_Image2Data.py --input Cropped/roi

# Import the necessary packages
import imutils
import cv2
import pytesseract
import numpy as np
import logging


logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def strip(list2strip):
    stripped = []
    num_list = []
    for x in list2strip:
        if len(x) > 4:
            stripped.append(x)
    for y in stripped:
        n_list = list(map(int, ''.join([x if x.isdigit() else ' ' for x in y]).split()))
        num_list.append(n_list)
    number_list = flatten(num_list)
    return(number_list,stripped)


def extract_text(results):
    for i in range(0, len(results["text"])):
        text = results["text"][i]
        conf = int(results["conf"][i])
        if text != '':
            text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
    return text, conf


def find_max_list_idx(list): # find the list that has the max no. of elements in a list of lists
    list_len = [len(i) for i in list]
    return np.argmax(np.array(list_len))


def flatten(l): # flatten a single depth list of lists
    return [item for sublist in l for item in sublist]


def condense(f_list):
    # Initializing the list to be returned
    c_list = []

    # Checking and extracting elements that contain the bits 'C2'
    indices = [i for i in range(len(f_list)) if f_list[i][:2] == 'c2']
    elements = [f_list[index] for index in indices]
    c_list.append(elements)

    # Checking and extracting elements that contain the bits with any numerical digits
    indices = [i for i in range(len(f_list)) if(any(map(str.isdigit, f_list[i])))]
    elements = [f_list[index] for index in indices]
    for element in elements:
        numbers = [int(word) for word in element.split() if word.isdigit()]
        c_list.append(numbers)

    # Checking and extracting elements that contain the bits with any numerical digits, having overall length more than 1 (for SN)
    indices = [i for i in range(len(f_list)) if len(f_list[i]) > 1]
    elements = [f_list[index] for index in indices]
    indices = [i for i in range(len(elements)) if(any(map(str.isdigit, elements[i])))]
    elements = [elements[index] for index in indices]
    elements = [str(i) for i in elements]
    c_list.append(elements)

    # Returning the list of unique set of collected elements above
    return(list(set(flatten(c_list))))


def rednumlist(numlist):
    snumlist = [str(item) for item in numlist]
    rednumlist = [item for item in snumlist if len(item)==6]
    if len(rednumlist)!=0:
        return [rednumlist[0]]
    else:
        return []


# Indicating the location of pytesseract
# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def main(nm):

    #Re-sizing width value
    set_width = 500

    # Configure Tesseract to only OCR alphanumeric characters
    alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    options = "-c tessedit_char_whitelist={}".format(alphanumeric)
    # Set the PSM mode
    psm = 7 # Page Segmentation Mode
    options += " --psm {}".format(psm)
    options += " outputbase digits"
    # Return the Tesseract options string
    # print("[OPTIONS] {}".format(options))

    # Define the kernel for EROSION and DILATION
    kernel = np.ones((3, 3), np.uint8)

    # Load the input image from disk and resize it
    # image = cv2.imread(nm)
    image = nm.copy()
    image_rs = image.copy()
    image_rs = imutils.resize(image, width=set_width)
    image_gray = cv2.cvtColor(image_rs, cv2.COLOR_RGB2GRAY)

    canny = cv2.Canny(image_gray, 120, 255, 1)
    canny_inv = cv2.bitwise_not(canny)
    h, w = canny_inv.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    canny_floodfill = canny_inv.copy()
    cv2.floodFill(canny_floodfill, mask, (0, 0), 255)
    blur7 = cv2.GaussianBlur(canny_floodfill, (7, 7), 0)
    (ret3, image_bw_o7) = cv2.threshold(blur7, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cio = cv2.morphologyEx(image_bw_o7, cv2.MORPH_OPEN, kernel)
    cic = cv2.morphologyEx(cio, cv2.MORPH_CLOSE, kernel)

    blur5 = cv2.GaussianBlur(image_gray, (5, 5), 0)
    (ret3, image_bw_o5) = cv2.threshold(blur5, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    blur7 = cv2.GaussianBlur(image_gray, (7, 7), 0) #Default
    (ret3, image_bw_o7) = cv2.threshold(blur7, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    image_open = cv2.morphologyEx(image_bw_o7, cv2.MORPH_OPEN, kernel)
    image_close = cv2.morphologyEx(image_open, cv2.MORPH_CLOSE, kernel)
    im_floodfill = image_close.copy()
    h, w = image_bw_o7.shape[:2]
    mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(im_floodfill, mask, (0, 0), 255)
    im_floodfill_inv = cv2.bitwise_not(im_floodfill)

    # Feed the image to Tesseract and print the output
    results = pytesseract.image_to_data(image_gray, config=options, output_type=pytesseract.Output.DICT)
    GR, conf_GR = extract_text(results)
    results = pytesseract.image_to_data(image_bw_o5, config=options, output_type=pytesseract.Output.DICT)
    O5, conf_O5 = extract_text(results)
    results = pytesseract.image_to_data(image_bw_o7, config=options, output_type=pytesseract.Output.DICT)
    O7, conf_O7 = extract_text(results)
    results = pytesseract.image_to_data(image_close, config=options, output_type=pytesseract.Output.DICT)
    CL, conf_CL = extract_text(results)
    results = pytesseract.image_to_data(im_floodfill, config=options, output_type=pytesseract.Output.DICT)
    FF, conf_FF = extract_text(results)
    results = pytesseract.image_to_data(im_floodfill_inv, config=options, output_type=pytesseract.Output.DICT)
    IN, conf_IN = extract_text(results)
    results = pytesseract.image_to_data(cio, config=options, output_type=pytesseract.Output.DICT)
    CO, conf_CO = extract_text(results)
    results = pytesseract.image_to_data(cic, config=options, output_type=pytesseract.Output.DICT)
    CI, conf_CI = extract_text(results)

    # Processing the output
    my_input_list = [[GR], [O5], [O7], [CL], [FF], [IN], [CO], [CI]]
    input_list = flatten(my_input_list)
    string_list = [each_string.lower() for each_string in input_list]

    # SENDING inputs to the CONDENSE Module
    condensed = condense(string_list)
    # print("CONDENSE Output ", imagePath[(len(args["input"])+1):pathlength],",",condensed)
    mother_list = [str(i) for i in condensed]
    # mother_list = list(set(mother_list))
    mother_list = list(dict.fromkeys(mother_list))

    final_list = []
    if(len(mother_list) > 0):
        check_elements = ['nm', 'np']
        for element in check_elements:
            result = [s for s in mother_list if element in s]
            if(len(result)) > 0 and element == 'nm':
                final_list.append('C2NM')
            if(len(result)) > 0 and element == 'np':
                final_list.append('C2NP')
    number_list, stripped = strip(mother_list)
    rednumber_list = rednumlist(number_list)
    ret_list = final_list+rednumber_list
    # Average Confidence:
    avg_conf = (conf_GR+conf_O5+conf_O7+conf_CL+conf_FF+conf_IN+conf_CO+conf_CI)/8
    logger.info('avg conf %s' % avg_conf)
    return ret_list, avg_conf
