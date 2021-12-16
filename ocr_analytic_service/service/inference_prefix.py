import numpy as np
import cv2
import os
import logging
import boto3

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    s3_resource = boto3.resource('s3', region_name=os.getenv('REGION'))
except:
    s3_resource = boto3.resource('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                 AWS_SECRET_ACCESS_KEY=os.getenv('aws_secret_access_key'),
                                 region_name=os.getenv('REGION'))
    pass


x_lowTolRange = 0.68#0.85 #How far away the first character of PR can be away from PR box; need larger tolerance as it is 1st
x_highTolRange = 1.1#1.15 #how far away the last character is to be from PR need lesser tolerance as we assume PR box to be larger on width side
y_lowTolRange = 0.68#0.85 #How far away the first character of PR can be away from PR box; need larger tolerance as it is 1st
y_highTolRange = 1.1#1.15 #how far away the last character is to be from PR need lesser tolerance as we assume PR box to be larger on width side

scoreThreshold = 0.2
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
names = ['prefix'] # List of values to be extracted in human readable form
names2LabelMap = {'prefix':'PR'} #Give full map of the human readable names and labels


class debugMessage:
    message = ''
    level = 0

    def __init__(self, message, level=0):
        self.message = message
        self.level = level


def debugPrint(debugMessage):
    # need to reqrite the debugPrint to print detailed information based on the level
    if debugMessage.level < debugThreshold:
        print(debugMessage.message)


class OuterBox():
    def __init__(self, xmin, ymin, xmax, ymax):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.xyPos = int(self.ymin) * 100000 + int(self.xmin)
        self.euclidDistance = int(
            np.sqrt(np.square(self.ymin) + np.square(self.xmin)))
        self.width = self.xmax - self.xmin
        self.height = self.ymax - self.ymin

    def containsBox(self,innerBox):
        if self.xmin*x_lowTolRange < innerBox.xmin and self.ymin *y_lowTolRange < innerBox.ymin and self.xmax *x_highTolRange > innerBox.xmax and self.ymax *y_highTolRange> innerBox.ymax:
            return True
        else:
            return False


class LabelResult():
    def __init__(self, word, score):
        self.label = word
        self.score = score
        # self.list_score = list_score


class word:
    charIndex = []
    score = 0

    def __init__(self, charList, score):
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


# Class map and config and model needs to be sync
class_map = {0: '0', 1: '0_', 2: '0_DP', 3: '1', 4: '1_DP', 5: '2', 6: '2_DP', 7: '3', 8: '3_DP', 9: '4', 10: '4_DP', 11: '5', 12: '5_DP', 13: '6', 14: '6_DP', 15: '7', 16: '7_DP', 17: '8', 18: '8_DP', 19: '9', 20: '9_DP', 21: 'A', 22: 'B', 23: 'BL', 24: 'C', 25: 'D', 26: 'E', 27: 'F', 28: 'G', 29: 'H', 30: 'I', 31: 'K', 32: 'L', 33: 'M', 34: 'N', 35: 'P', 36: 'PR', 37: 'PSN', 38: 'R', 39: 'ROI', 40: 'ROI-SN', 41: 'S', 42: 'T', 43: 'TL', 44: 'V', 45: 'W', 46: 'p'}
class_names = []
cn = list(class_map.values())

class Results:
    results = []
    lines = []
    def __init__(self,classes_list,bboxList,scoreList):
        self.results=[]
        self.lines = []
        for i in range(len(classes_list)):
            item = classes_list[i]
            class_names.append(cn[item])
            self.results.append(resultLet(class_names[i], bboxList[i], scoreList[i]))
        self.results.sort(key=lambda x: x.euclidDistance)

    def getClosesToOrigin(self):
        return(self.results[0])
    def getLinesNwords(self):
        if len(self.lines) < 1:
            self.createLinesNwords()
        return(self.lines)
    def createLinesNwords(self):
        line = []
        words = []
        currentWord = []
        currentIndex = 0
        setCharIndex = set (range(len(self.results)) )
        lineIdex = 0
        wordIndex = 0
        charIndex = 0
        self.lines = []
        currentLine = []
        currentWord = []
        for  currIndex  in range(len(self.results)) :

            if currIndex in setCharIndex:
                currentWord.append([currIndex])
                setCharIndex.remove(currIndex)
                wordChar, iswordEnd, isMultipleBoxes = self.results[currIndex].getNextResultLet(self.results)
                if wordChar == -1:
                    self.lines.append(currentLine)
                    currentLine = []
                    currentWord = []
                    continue
                if iswordEnd:
                    currentLine.append(currentWord)
                    currentWord = []
                currentWord.append(wordChar)
                if isMultipleBoxes:
                    for j in range(len(wordChar)-1):
                        setCharIndex.remove(wordChar[j])
            else:
                debugPrint(debugMessage(str(currIndex) + ' is already considered; Skipping the processing',0))


def resultletCompLess(o1, o2):
    if o1.xyPos < o1.xyPos:
        return True
    else:
        return False


def isOverLapping(box1, lBoxes):
    isResultMulitpleBoxes = False
    overlappingBoxes = []
    if abs((box1.xmin - lBoxes.xmin) / box1.width) * 100 < xdeviationPercent and \
            (abs(box1.ymin - lBoxes.ymin) / box1.height) * 100 < ydeviationPercent:
        return(True)
    else:
        return(False)


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


def getCorrectROI(results):
    correct = None
    score = 0.0
    ROIList = []
    for i in range(len(results.results)):
        if results.results[i].category == 'ROI':
            if results.results[i].height > expectedMinNumRows_ROI * chHeight and results.results[i].height < expectedMaxNumRows_ROI * chHeight :
                ROIList.append(results.results[i])
                if score < results.results[i].score :
                    score = results.results[i].score
                    correct = results.results[i]
    if correct == None:
        print('No Valid ROI found; Returning None')

    return correct


def getCorrectPR(ROI, results):
    correct = None
    score = 0.0
    PRList = []
    for i in range(len(results.results)):
        if results.results[i].category == 'PR':
            if ROI == None:
                correct = results.results[i]
                score = results.results[i].score
            try:
                chWidth = ROI.width/15.0
                chHeight = ROI.height/4.0
                if results.results[i].ymin > ROI.ymin + chHeight:
                    if results.results[i].width > expectedMinNumChars_PR * chWidth and results.results[
                        i].width < expectedMaxNumChars_PR * chWidth:
                        PRList.append(results.results[i])
                        if score < results.results[i].score:
                            score = results.results[i].score
                            correct = results.results[i]
            except:
                print('ROI box and PR box alignments are screwed up')
    if correct == None:
        print('No Valid PR found; Returning None')
        for ix in range(len(results.results)):    print('Label: '+
            results.results[ix].category + ', Dist: ' + str(results.results[ix].euclidDistance) + ', H: ' + str(
                results.results[ix].height) + ', W: ' + str(results.results[ix].width) + ', Ymin: ' + str(
                results.results[ix].ymin) + ', Xmin: ' + str(results.results[ix].xmin))
    return correct


def get_named_strings(names,results):
    extractedResults = {}
    for i in range(len(names)):
        label2Process = names2LabelMap[names[i]]
        extractedResults[label2Process] = []
        outBox = None
        outBoxList = []
        ROIBox = getCorrectROI(results)
        if ROIBox == None:
            print('ROI Box not found for anchoring PR. Returning None results')

        for j in range(len(results.results)):
            if results.results[j].category == label2Process:
                outBox = OuterBox(results.results[j].xmin,results.results[j].ymin,results.results[j].xmax,results.results[j].ymax)
                outBoxList.append(outBox)

        outBoxCorrect = getCorrectPR(ROIBox,results)
        if outBoxCorrect == None:
            print('Outbox '+label2Process+' is not found')
            return None
        if outBox == None:
            print('Outbox '+label2Process+' is not found')
            return None
        for obi in range(len(outBoxList)):

            outBox = outBoxList[obi]
            outBox = OuterBox(outBoxCorrect.xmin, outBoxCorrect.ymin, outBoxCorrect.xmax, outBoxCorrect.ymax)
            insideBoxes = []
            for j in range(len(results.results)):
                if outBox.containsBox(results.results[j]):
                    if results.results[j].score >scoreThreshold:
                        if results.results[j].category != label2Process:
                            insideBoxes.append(results.results[j])
            words = []
            setAlterChars = set()
            for j in range(len(insideBoxes)):
                alternateChars = [insideBoxes[j]]
                if j in setAlterChars:
                    continue
                for k in range(j+1,len(insideBoxes)):
                    if insideBoxes[k].score > scoreThreshold:
                        if isOverLapping(insideBoxes[j],insideBoxes[k]):
                            alternateChars.append(insideBoxes[k])
                            setAlterChars.add(k)
                words.append(alternateChars)
            word,score,scoreString = getBestWordWithScore(words)
            extractedResults[label2Process].append(LabelResult(word,scoreString))
    return extractedResults


def clean_class(classes_list, scores_list, boxes_list, class_names):
    clean_box_list = []
    clean_classes_list = []
    for clas_name in class_names:
        list_hold_idx = []
        for index, clas in enumerate(classes_list):
            if clas==clas_name:
                list_hold_idx.append(index)
        scores_sublist = [scores_list[i] for i in list_hold_idx]
        if len(scores_sublist)>0:
            max_score = max(scores_sublist)
            max_score_idx = scores_list.index(max_score)
            clean_box_list.append(boxes_list[max_score_idx])
            clean_classes_list.append(classes_list[max_score_idx])
        else:
            continue
    return clean_box_list, clean_classes_list


def getPrefix(im, predictor, filename, key='PR'):
    #Change for pre-processing fileter -- Start
    # bgr = im
    # lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    # l, a, b = cv2.split(lab)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(7, 7))
    # l = clahe.apply(l)
    # lab = cv2.merge((l, a, b))
    # bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    # im = bgr #CLAHE filtered image
    # Change for pre-processing fileter -- End
    # cv2.imwrite('/shared-volume/inputfile.jpg', im)
    try:
        file_prefix = 'prefix/' + filename
        prefix_dump_file_path = os.path.join(os.getenv('DUMP_IMAGES'), file_prefix)
        logger.info('Prefix Input Images will be dumped at:  %s' % prefix_dump_file_path)
        os.makedirs("IDM/dev/dump_images/prefix", exist_ok=True)
        imwriteStatus = cv2.imwrite(prefix_dump_file_path, im)
        image_path = 'IDM/dev/dump_images/prefix_input' + filename
        s3_resource.meta.client.upload_file(prefix_dump_file_path, os.getenv('BUCKET_NAME'), image_path)
    except Exception as e: 
        logger.info('Dumping Prefix input Images failure! %s' % e)

    outputs = predictor(im)
    classes = outputs['instances'].pred_classes
    boxes = outputs['instances'].pred_boxes
    scores = outputs['instances'].scores

    classes_list = classes.tolist()
    scores_list = scores.tolist()
    boxes_list = boxes.tensor.tolist()
    results = Results(classes_list, boxes_list, scores_list)

    clean_box_list, clean_classes_list = clean_class(classes_list, scores_list, boxes_list, list(range(len(class_map))))
    labelDict = get_named_strings(names, results)

    if labelDict == None:
        print('The '+ str(names) + 'not found; Returning empty String')
        return '', 0.0, '', 0.0, []
    try:
        prefix = ''.join(labelDict.get(key)[0].label)
        scoreString = labelDict.get(key)[0].score
        scoreList = scoreString.split('*')
        scoreList.remove('')
        score = 1.0
        minScore = 1.0
        minIdx = 0
        for i in range(len(scoreList)):
            score = score*float(scoreList[i])
            if minScore > float(scoreList[i]):
                minScore = float(scoreList[i])
                minIdx = i
    except:
        print('prefix could be empty because it contains no boxes or multiple spurious boxes exists without content')
        return '', 0.0, '', 1.0, []
    if prefix == '':
        print('prefix could be empty because it contains no boxes or multiple spurious boxes exists without content')
        return prefix, score,'',1.0,[]
    return prefix, score, prefix[minIdx],float(scoreList[minIdx]),scoreList