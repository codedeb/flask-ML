#class_map
#Results
#labelDict
#names2LabelMap
import time
import numpy as np
import logging
from ocr_wrapper_service.constants import ModelDetails

logger = logging.getLogger(__name__)

debug = True
inferenceOutputFolder = 'output_4New'
#modelToUse = 'model_final_prefixNsegments.pth'
#modelToUse = 'model_final_PR_seg_PSN.pth'
#modelToUse = 'model_0094999.pth'
#modelToUse = 'model_0075k.pth'
# modelToUse = 'shroud/model_final_shroud.pth'
modelToUse = ModelDetails.shroud_model_path
configToUse = ModelDetails.shroud_config_path

#modelToUse = 'model_0124999.pth'
#TestImagesPath = 'test_images_8'
num=str(125)+'_PlusTVAS123_final_V2_PP'
suffix = '_Results_PP_V2'+num+'.csv'
testDict = {#'C:/2021_Projects/OCR/detect/ModifiedValImages':'C:/2021_Projects/OCR/detect/ModifiedValImages_Output_test_'+num
            #'C:/2021_Projects/OCR/ROI_S1B_John_Sevier_1/ROI_S1B_John_Sevier':'C:/2021_Projects/OCR/ROI_S1B_John_Sevier_1_results_'+num
            #'C:/2021_Projects/OCR/ROI_S1B_John_Sevier':'C:/2021_Projects/OCR/ROI_S1B_John_Sevier_results'
            #'../Data_29Jul2021/RawImages/newTest1':'../Data_29Jul2021/ResultImages/newTest1'
            #'../Data_29Jul2021/RawImages/9':'../Data_29Jul2021/ResultImages/9_new'#,
            #'../Data_29Jul2021/RawImages/9_ROI':'../Data_29Jul2021/ResultImages/9_ROI',
            'C:\\2021_Projects\\OCR\\detect\\Shroud\\data\\input':'C:\\2021_Projects\\OCR\\detect\\Shroud\\data\\output'
            #'../Data_29Jul2021/RawImages/4':'../Data_29Jul2021/ResultImages/4',
            ##'../Data_29Jul2021/RawImages/5':'../Data_29Jul2021/ResultImages/5',
            #'../Data_29Jul2021/RawImages/6':'../Data_29Jul2021/ResultImages/6',
            #'../Data_29Jul2021/RawImages/7':'../Data_29Jul2021/ResultImages/7',
            #'../Data_29Jul2021/RawImages/8':'../Data_29Jul2021/ResultImages/8',
            #'../Data_29Jul2021/RawImages/9':'../Data_29Jul2021/ResultImages/9',
            #'../Data_29Jul2021/RawImages/10':'../Data_29Jul2021/ResultImages/10',
            #'../Data_29Jul2021/RawImages/11':'../Data_29Jul2021/ResultImages/11',
            #'../Data_29Jul2021/RawImages/12':'../Data_29Jul2021/ResultImages/12',
            #'../Data_29Jul2021/RawImages/13':'../Data_29Jul2021/ResultImages/13',
            #'../Data_29Jul2021/RawImages/14':'../Data_29Jul2021/ResultImages/14',
            #'../Data_29Jul2021/RawImages/15':'../Data_29Jul2021/ResultImages/15'
            }
x_lowTolRange = 0.68#0.85 #How far away the first character of PR can be away from PR box; need larger tolerance as it is 1st
x_highTolRange = 1.1#1.15 #how far away the last character is to be from PR need lesser tolerance as we assume PR box to be larger on width side
y_lowTolRange = 0.9#0.85 #How far away the first character of PR can be away from PR box; need larger tolerance as it is 1st
y_highTolRange = 1.1#1.15 #how far away the last character is to be from PR need lesser tolerance as we assume PR box to be larger on width side

scoreThreshold = 0.8
widthOverlapPercent = 15 #Siva: widthOverlapPercent is the fraction of overlap allowed for neighbor; Sorry naming is wrong -:)
heightOverlapPercent = 15 #Siva: heightOverlapPercent is the fraction of overlap allowed for neighbor; Sorry naming is wrong -:)
numCharBoxDistance = 2 #expectrd min distance between boxes
InfeasibleNeighbor = 1000 #if distances between two beoxes is this number then they are not neighbors
#overlapping boxes of char
xdeviationPercent = 15 #Siva: 1-xdeviationPercent is the fraction that overlaps for considering two boxes to be same; Sorry naming is wrong -:)
ydeviationPercent = 15 #Siva: 1-ydeviationPercent is the fraction that overlaps for considering two boxes to be same; Sorry naming is wrong -:)
numBoxGaps =  2 # to decide if the gap between the boxes indicate the separation of words
debugThreshold = 10

#Label Box related measurements
expectedMinNumRows_ROI = 0#4
expectedMaxNumRows_ROI = 20
expectedMinNumChars_PR = 0#2
expectedMaxNumChars_PR = 8
chWidth = 60
chHeight = 65
#names = ['SN','SEG'] # List of values to be extracted in human readable form
#names2LabelMap = {'prefix':'PR','boundingBox':'BB'} #Give full map of the human readable names and labels
names2LabelMap = {'SN':'SN','SEG':'SEG'}
class debugMessage:
    message=''
    level = 0
    def __init__(self,message,level=0):
        self.message = message
        self.level = level
def debugPrint(debugMessage):
    #need to reqrite the debugPrint to print detailed information based on the level
    if debugMessage.level < debugThreshold:
        print(debugMessage.message)
class OuterBox():
    def __init__(self,xmin,ymin,xmax,ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.xyPos = int(self.ymin) * 100000 + int(self.xmin)
        self.euclidDistance = int(np.sqrt(np.square(self.ymin) + np.square(self.xmin)))
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin
    def containsBox(self,innerBox):
        if self.xmin*x_lowTolRange < innerBox.xmin and self.ymin *y_lowTolRange < innerBox.ymin and self.xmax *x_highTolRange > innerBox.xmax and self.ymax *y_highTolRange> innerBox.ymax:
            return True
        else:
            return False
class LabelResult():
    def __init__(self,word,score):
        self.label = word
        self.score = score

class word:
    charIndex = []
    score = 0
    def __init__(self,charList,score):
        self.charIndex = charList
        self.score = score
    def getCharIndices(self):
        return (self.charIndex)
    def getScore(self):
        return(self.score)

class resultLet:
    def __init__(self, category,bbox,score):
        self.category = category
        self.score = score
        self.xmin = bbox[0]
        self.ymin = bbox[1]
        self.xmax = bbox[2]
        self.ymax = bbox[3]
        self.xyPos = int(self.ymin)*100000+int(self.xmin)
        self.euclidDistance = int(np.sqrt(np.square(self.ymin)+np.square(self.xmin)))
        self.width = self.xmax-self.xmin
        self.height = self.ymax - self.ymin
    def geteuclidDistance(self):
        return self.euclidDistance
    def getHeight(self):
        return(self.height)
    def getWidth(self):
        return(self.width)
    def getXyPos(selfs ):
        return self.xyPos
    def getNextResultLet(self,results):
        xdist = self.width*numCharBoxDistance
        neighborIndex = InfeasibleNeighbor
        isResultMulitpleBoxes = False
        for i in range(len(results)): #Find current box
            if self.xmin == results[i].xmin and self.ymin == results[i].ymin and self.xmax == results[i].xmax and self.ymax == results[i].ymax : #will exclude the self identified same x n y co-ordinates
                currentBoxFOund = True
                currentIndex = i
                break
            else:
                continue
        # Assumption is that search for next is sequential in the results
        for i in range(currentIndex,len(results)): #for the other indices from current one
            if i == currentIndex:
                continue #skip current index
            if ((abs((self.xmax - results[i].xmin) / self.width*100) < widthOverlapPercent) and (abs((self.ymin - results[i].ymin) / self.height*100) < heightOverlapPercent)) : # assume 10% of width as overlap for next box, and an absolute height difference of 10%; these can be set at the top
                if xdist > (results[i].xmin - self.xmax): #check this logic. Should dist be abs? currently we give preference to most overlapping box with in tolerance
                    xdist = (results[i].xmin - self.xmax)
                    neighborIndex = i
        if neighborIndex == InfeasibleNeighbor:
            return -1, False,False # return value of -1 means its end of the line; Caller needs to ignore wordGap flag as it has no meeaning
        else:
            #find all the boxes that are within x% width of the new neighbor's xmin, and y% height of new nighbor
            #these boxes are considered to represent same char but as different class.
            isResultMulitpleBoxes  = False
            overlappingBoxes = [neighborIndex]
            for j in range(currentIndex,len(results)):
                if j == currentIndex:
                    continue
                if abs((results[currentIndex].xmin-results[j].xmin)/results[currentIndex].width)*100 < xdeviationPercent and abs((results[currentIndex].ymin - results[j].ymin) / results[currentIndex].height) * 100 < ydeviationPercent :
                    overlappingBoxes.append(j)
                    isResultMulitpleBoxes = True

            wordGap = False
            if (results[neighborIndex].xmin - self.xmax) > numBoxGaps*self.width: #if gap between characters is more than numBoxGaps boxes, its assumed to be word gap
                wordGap = True
            else:
                wordGap = False

            return overlappingBoxes,wordGap, isResultMulitpleBoxes

class Results:
    results = []
    lines = []
    def __init__(self,cn,classes_list,bboxList,scoreList):
        self.results=[]
        self.lines = []
        class_names = []
        for i in range(len(classes_list)):
            item = classes_list[i]
            class_names.append(cn[item])
            self.results.append(resultLet(class_names[i], bboxList[i], scoreList[i]))
            # print(item)
            # print(class_names[i])
        self.results.sort(key=lambda x: x.euclidDistance)

    def getClosesToOrigin(self):
        return(results[0])
    def getLinesNwords(self):
        if len(self.lines) < 1:
            self.createLinesNwords()
        return(self.lines)
    def createLinesNwords(self):
        #return None #A temparary stop to disable this code.
        line = [] # #line is list of words
        words = [] # words list list characters; each character is a list containing the proposals for that position
        currentWord = [] #word is list of indices list because each character might have alternatives
        #Assumption is that the the results are sorted according to Eucledian distance from Orgin
        currentIndex = 0 #first line and first char
        setCharIndex = set (range(len(self.results)) ) # make set of all character indices in results list; We need to take
                                                  # them out of consideration for alternative characters if they are
                                                  # are already alternative characters for others
        lineIdex = 0
        wordIndex = 0
        charIndex = 0
        self.lines = [] #first word with index = 0
        currentLine = []
        currentWord = [] #Set current word to empty list ?? or should I set current word to line 0 and word zero
        for  currIndex  in range(len(self.results)) : #Start with first character in the results

            if currIndex in setCharIndex: # If the current charater under consideration still needs to be considered
                #debugPrint(debugMessage((str(currIndex)) + ' is considered; processing it for its neighbor',0))
                currentWord.append([currIndex]) # Append it to current word
                setCharIndex.remove(currIndex)  # and remove from further consideration
                # get next (nearest right side character) from the same line; the function also finds alternative
                # proposals for next and if the next character is word distance away or if it is the last in that line
                wordChar, iswordEnd, isMultipleBoxes = self.results[currIndex].getNextResultLet(self.results)
                if wordChar == -1:
                    self.lines.append(currentLine)
                    currentLine = []
                    currentWord = []
                    continue
                # if there are more characters in the line; else start a new line and start the process for that line
                if iswordEnd: #If the current character is the start of new word then
                    #Store current word into current line
                    currentLine.append(currentWord)
                    currentWord = [] # reset current word to empty list; will it also make the save word to empty? check
                currentWord.append(wordChar) #word char is list having one or more characters
                #if there are multiple char propositions for the same space delete all but one from further consideration
                if isMultipleBoxes:
                    for j in range(len(wordChar)-1): #just keep one overallping char to go to next word
                        setCharIndex.remove(wordChar[j])
            else:
                debugPrint(debugMessage(str(currIndex) + ' is already considered; Skipping the processing',0))



            #    if (iswordEnd):
            #        if (isMultipleBoxes):



def resultletCompLess(o1,o2):
    if o1.xyPos < o1.xyPos:
        return True
    else:
        return False

def isOverLapping(box1, lBoxes):
    isResultMulitpleBoxes = False
    overlappingBoxes = []
    #for j in range(len(lBoxes)):
        #if j == currentIndex:
        #    continue
    if abs((box1.xmin - lBoxes.xmin) / box1.width) * 100 < xdeviationPercent and (abs(box1.ymin - lBoxes.ymin) / box1.height)* 100 < ydeviationPercent:
        return(True)
    else:
        return(False)
    #overlappingBoxes.append(j)
    #isResultMulitpleBoxes = True
    #return isResultMulitpleBoxes, overlappingBoxes

def get_bestCharClass(charAlternatives):
    if len(charAlternatives) == 1:
        return charAlternatives[0].Category, charAlternatives[0].score
    currChar = charAlternatives[0].category
    score = charAlternatives[0].score
    for i in range(len(charAlternatives)-1):
        if score < charAlternatives[i+1].score: #Character with highest score is the winner
            currChar = charAlternatives[i+1].category
            score = charAlternatives[i+1].score
    return currChar, score
def getBestWordWithScore(words):
    word = []
    score = 1.0
    scoreString = ''
    for j in range(len(words)):
        #word=[]
        #score = 1.0
        if len(words[j]) > 1:
            charClass, ClassScore = get_bestCharClass(words[j])
            if len(charClass) == 1:
                word.append(charClass)
                score = score * ClassScore
                scoreString = scoreString+'*'+str(ClassScore)
        else:
            if len(words[j][0].category) == 1:
                word.append(words[j][0].category)
                score = score * words[j][0].score
                scoreString = scoreString + '*' + str(words[j][0].score)
    return word, score, scoreString
cn = []
def getClassResults(class_map,bboxes,outputs,names=['SN','SEG']):
    logger.info('Shrouds post processing get class results! %s' % names)
    classes = outputs['instances'].pred_classes
    boxes = outputs['instances'].pred_boxes
    scores = outputs['instances'].scores

    classes_list = classes.tolist()
    scores_list = scores.tolist()
    boxes_list = boxes.tensor.tolist()
    class_names = []
    cn = list(class_map.values())
    # results=[]
    logger.info('get class results checking results! %s' % cn)
    results = Results(cn,classes_list, boxes_list, scores_list)
    resultsInitateTime = time.time()
    #debugState = debug
    #debug = False

    labelDict = get_named_strings(names, results, bboxes)  # ,filename.upper())
    logger.info('get class results calling labeldict! %s' % labelDict)
    #debug = True
    return labelDict,0.9 #Siva: Change it with probability/confidence

def get_named_strings(names,results,SegBoxes=[],fname=None):
    logger.info('get_named_strings input! %s' % names)
    extractedResults = {}
    outBoxList = []
    if fname == None:
        if len(SegBoxes)<1:
            print('Bounding Boxes not supplied and is not a test using filename')
            return None

    for i in range(len(names)):
        label2Process = names2LabelMap[names[i]]
        extractedResults[label2Process] = []
        outBox = None
        #outBoxList = []
        #ROIBox = getCorrectROI(results)
        #if ROIBox == None:
            #print('ROI Box not found for anchoring PR. Returning None results')
            #return None # Siva: A hack when ROI is not found for cropped images just ignore the ROI and continue
        if len(SegBoxes)>1:
            outBox = OuterBox(SegBoxes[i][0],SegBoxes[i][1],SegBoxes[i][2],SegBoxes[i][3])
        elif fname != None and label2Process in segDict[fname].keys():
            outBox = OuterBox(segDict[fname][label2Process]['xmin'],segDict[fname][label2Process]['ymin'],
                              segDict[fname][label2Process]['xmax'],segDict[fname][label2Process]['ymax'])
        if outBox != None:
            outBoxList.append(outBox)
            #outBox = OuterBox(outBoxCorrect.xmin, outBoxCorrect.ymin, outBoxCorrect.xmax, outBoxCorrect.ymax)
            insideBoxes = [] #Initialize boxes contained within the label; get boxes -->
            for j in range(len(results.results)):
                if outBox.containsBox(results.results[j]):
                    if results.results[j].score >scoreThreshold: #ELiminating all the boxes less than threshold; Bad for learning
                        if results.results[j].category != label2Process:
                            #print ('Box '+ str(j)+': '+'Distance: '+ str(results.results[j].euclidDistance)+', Char: '+ results.results[j].category+ ', Prob: '+ str(results.results[j].score ))
                            insideBoxes.append(results.results[j])
            words = []
            setAlterChars = set()
            for j in range(len(insideBoxes)):
                alternateChars = [insideBoxes[j]]
                #setAlterChars = set()
                if j in setAlterChars:
                    continue
                for k in range(j+1,len(insideBoxes)):
                    #if k in setAlterChars:
                        #continue
                    if insideBoxes[k].score > scoreThreshold:
                        if isOverLapping(insideBoxes[j],insideBoxes[k]):
                            alternateChars.append(insideBoxes[k])
                            setAlterChars.add(k)
                words.append(alternateChars)
            #Following gives the best word based on the score.
            #But what we need is the list of all possible words with their scores
            word,score,scoreString = getBestWordWithScore(words)
        else:
            word ="None"
            score=0.0
            scoreString = "0.0"
        extractedResults[label2Process].append(LabelResult(word,scoreString))
        print(''.join(word)+'-'+''.join(scoreString))
    logger.info('get_named_strings extracting !')
    print(''.join((extractedResults['SN'][0]).label)+'-'+''.join((extractedResults['SEG'][0]).label))
    if debug == False:
        return ''.join((extractedResults['SN'][0]).label)+'-'+''.join((extractedResults['SEG'][0]).label)
    return extractedResults
segDict = {}
def getSegmentDetailsDict():
    import csv
    import pandas as pd
    dfSegDict = pd.read_csv('C:/2021_Projects/OCR/detect/Shroud/data/Shroud_segmentation_annotation.csv')
    groupeDF = dfSegDict.groupby(['filename'])
    for okey, val in groupeDF:
        j = groupeDF.get_group(okey).reset_index(drop=True)
        key = okey.upper() #Convert all strings to uppercase
        segDict[key] = {}
        segDict[key]['width'] = j['width'][0]
        segDict[key]['height'] = j['height'][0]
        for i in range(j.shape[0]):
            cls = j['class'][i].upper()
            segDict[key][cls] = {}
            segDict[key][cls]['xmin'] = j['xmin'][i]
            segDict[key][cls]['ymin'] = j['ymin'][i]
            segDict[key][cls]['xmax'] = j['xmax'][i]
            segDict[key][cls]['ymax'] = j['ymax'][i]
#data=prepare_data(print_data=True)
cn = []

def test_stub_shroud():
    # import some common detectron2 utilities
    from detectron2.engine import DefaultPredictor
    from detectron2.config import get_cfg
    from detectron2.utils.visualizer import Visualizer
    from detectron2.data import MetadataCatalog
    getSegmentDetailsDict()
    import cv2
    import pandas as pd
    import os
    # Create config
    cfg = get_cfg()
    #cfg.merge_from_file('config_file__pr_seg_PSN_12Aug.yaml')
    cfg.merge_from_file('shroud/config_file_shroud.yaml')

    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.1  # set threshold for this model
    #cfg.MODEL.RETINANET.SCORE_THRESH_TEST = 0.1
    cfg.MODEL.DEVICE = "cpu"


    cfg.MODEL.WEIGHTS = modelToUse

    predictor = DefaultPredictor(cfg)
    #path = 'augmented_data'

    #class_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',  10: 'B', 11: 'C', 12: 'D', 13: 'E',  14: 'G', 15: 'H',  16: 'K', 17: 'M', 18: 'N',  19: 'P', 20: 'T',  21: 'W'}
    #class_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',  10: 'B', 11: 'C', 12: 'D', 13: 'E',  14: 'G', 15: 'H',  16: 'K', 17: 'M', 18: 'N',  19: 'P', 20: 'T',  21: 'W', 22: 'ROI', 23: 'ROI-SN', 24: 'PSN', 25: 'PR', 26: 'BL', 27: 'TL'}
    #class_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',  11: 'B', 12: 'C', 13: 'D', 14: 'E',  16: 'G', 17: 'H',  20: 'K', 22: 'M', 23: 'N',  25: 'P', 29: 'T',  32: 'W'}
    #class_map = {0: '0', 1: '0_DP', 2: '1', 3: '1_DP', 4: '2', 5: '2_DP', 6: '3', 7: '3_DP', 8: '4', 9: '4_DP', 10: '5', 11: '5_DP', 12: '6', 13: '6_DP', 14: '7', 15: '7_DP', 16: '8', 17: '8_DP', 18: '9', 19: '9_DP', 20: 'A', 21: 'B', 22: 'BL', 23: 'C', 24: 'D', 25: 'E', 26: 'G', 27: 'H', 28: 'K', 29: 'M', 30: 'N', 31: 'P', 32: 'PR', 33: 'PSN', 34: 'ROI', 35: 'ROI-SN', 36: 'T', 37: 'TL', 38: 'W'}
    #class_map = {0: '0', 1: '0_', 2: '0_DP', 3: '1', 4: '1_DP', 5: '2', 6: '2_DP', 7: '3', 8: '3_DP', 9: '4', 10: '4_DP', 11: '5', 12: '5_DP', 13: '6', 14: '6_DP', 15: '7', 16: '7_DP', 17: '8', 18: '8_DP', 19: '9', 20: '9_DP', 21: 'A', 22: 'B', 23: 'BL', 24: 'C', 25: 'D', 26: 'E', 27: 'F', 28: 'G', 29: 'H', 30: 'I', 31: 'K', 32: 'L', 33: 'M', 34: 'N', 35: 'P', 36: 'PR', 37: 'PSN', 38: 'R', 39: 'ROI', 40: 'ROI-SN', 41: 'S', 42: 'T', 43: 'TL', 44: 'W'}
    #class_map = {0: '0', 1: '0_', 2: '0_DP', 3: '1', 4: '1_DP', 5: '2', 6: '2_DP', 7: '3', 8: '3_DP', 9: '4', 10: '4_DP', 11: '5', 12: '5_DP', 13: '6', 14: '6_DP', 15: '7', 16: '7_DP', 17: '8', 18: '8_DP', 19: '9', 20: '9_DP', 21: 'A', 22: 'B', 23: 'BL', 24: 'C', 25: 'D', 26: 'E', 27: 'F', 28: 'G', 29: 'H', 30: 'I', 31: 'K', 32: 'L', 33: 'M', 34: 'N', 35: 'P', 36: 'PR', 37: 'PSN', 38: 'R', 39: 'ROI', 40: 'ROI-SN', 41: 'S', 42: 'T', 43: 'TL', 44: 'V', 45: 'W', 46: 'p'}
    #class_map = {0: '0', 1: '0_', 2: '0_DP', 3: '1', 4: '1_DP', 5: '2', 6: '2_DP', 7: '3', 8: '3_DP', 9: '4', 10: '4_DP', 11: '5', 12: '5_DP', 13: '6', 14: '6_DP', 15: '7', 16: '7_DP', 17: '8', 18: '8_DP', 19: '9', 20: '9_DP', 21: 'A', 22: 'B', 23: 'BL', 24: 'C', 25: 'D', 26: 'E', 27: 'F', 28: 'G', 29: 'H', 30: 'I', 31: 'K', 32: 'L', 33: 'M', 34: 'N', 35: 'P', 36: 'PR', 37: 'PSN', 38: 'R', 39: 'ROI', 40: 'ROI-SN', 41: 'S', 42: 'T', 43: 'TL', 44: 'V', 45: 'W', 46: 'p'}
    class_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10:'A',  11: 'B', 12: 'C', 13: 'D', 14: 'E', 15:'F', 16: 'G', 17: 'H',18:'I',19:'J',  20: 'K', 21:'L',22: 'M', 23: 'N', 24:'O', 25: 'P', 26:'Q',27:'R',28:'S', 29: 'T', 30:'U', 31:'V', 32: 'W',33:'X',34:'Y',35:'Z'}
    #df = pd.DataFrame([])
    class_names = []
    cn = list(class_map.values())
    for key,val in testDict.items():
        TestImagesPath = key
        inferenceOutputFolder = val
        print('Input Directory: '+ TestImagesPath)
        print('Output directory: '+inferenceOutputFolder)
        if not (os.path.exists(os.path.join(os.getcwd(), inferenceOutputFolder))):
            os.mkdir(os.path.join(os.getcwd(), inferenceOutputFolder))
        resultsCSVFile = os.path.join(os.getcwd(),TestImagesPath+suffix)
        f = open(resultsCSVFile,'w')
        for image_path in os.listdir(TestImagesPath):
            startTime = time.time()
            input_path = os.path.join(TestImagesPath, image_path)
            filename = os.path.basename(input_path)

            im = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
            # dim = (1024,512)
            # img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            #im = cv2.bilateralFilter(im, 15, 75, 75)
            #im = cv2.bilateralFilter(im, 15, 75, 75)
            #im = cv2.medianBlur(im, 15)

            #Siva-->Kashsih: Change for pre-processing fileter -- Start
            bgr = cv2.imread(input_path, 1)
            lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(7, 7))
            l = clahe.apply(l)
            lab = cv2.merge((l, a, b))
            bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            im = bgr #CLAHE filtered image
            # Siva-->Kashsih: Change for pre-processing fileter -- End
            timeRead = time.time()
            # Make prediction
            class_names = []
            cn = list(class_map.values())

            outputs = predictor(im)
            timePredict = time.time()
            classes= outputs['instances'].pred_classes
            boxes= outputs['instances'].pred_boxes
            scores = outputs['instances'].scores

            classes_list = classes.tolist()
            scores_list = scores.tolist()
            boxes_list = boxes.tensor.tolist()
            class_names = []
            cn = list(class_map.values())
            #results=[]
            results = Results(cn,classes_list, boxes_list, scores_list)
            resultsInitateTime = time.time()
            # check This -- Siva
            #clean_box_list, clean_classes_list = clean_class(classes_list, scores_list, boxes_list, list(range(len(class_map))))
            #clean_box_list, clean_classes_list = clean_class(classes_list, scores_list, boxes_list, class_names)
            bboxes = []
            if 'SN' in segDict[filename.upper()].keys():
                box1 = segDict[filename.upper()]['SN']['xmin'],segDict[filename.upper()]['SN']['ymin'],\
                       segDict[filename.upper()]['SN']['xmax'],segDict[filename.upper()]['SN']['ymax']
            else:
                box1 = 0,0,0,0
            bboxes.append(box1)
            if 'SEG' in segDict[filename.upper()].keys():
                box2 = segDict[filename.upper()]['SEG']['xmin'],segDict[filename.upper()]['SEG']['ymin'],\
                       segDict[filename.upper()]['SEG']['xmax'],segDict[filename.upper()]['SEG']['ymax']
            else:
                box2 = 0, 0, 0, 0
            bboxes.append(box2)

            #debugState = True
            debug = False
            resultString = getClassResults(class_map,bboxes,outputs)

            labelDict = resultString
            print('Outpur of get_named_strings with bboxes and debug set to False -- Returning String; File: '+ filename)
            print(labelDict)
            debug = False
            endTime = time.time()
debug = False
# test_stub_shroud()


