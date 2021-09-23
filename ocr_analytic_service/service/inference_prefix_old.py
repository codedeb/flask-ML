from .conf_band import confidence_band
import numpy as np

scoreThreshold = 0.7
widthOverlapPercent = 15
heightOverlapPercent = 15
numCharBoxDistance = 2
InfeasibleNeighbor = 1000
# overlapping boxes of char
xdeviationPercent = 5
ydeviationPercent = 5
numBoxGaps = 2  # to decide if the gap between the boxes indicate the separation of words
debugThreshold = 10
names = ['prefix']
names2LabelMap = {'prefix': 'PR'}


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

    def containsBox(self, innerBox):
        if self.xmin < innerBox.xmin and self.ymin < innerBox.ymin and self.xmax > innerBox.xmax and self.ymax > innerBox.ymax:
            return True
        else:
            return False


class LabelResult():
    def __init__(self, word, score, list_score):
        self.label = word
        self.score = score
        self.list_score = list_score


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
    def __init__(self, category, bbox, score):
        self.category = category
        self.score = score
        self.xmin = bbox[0]
        self.ymin = bbox[1]
        self.xmax = bbox[2]
        self.ymax = bbox[3]
        self.xyPos = int(self.ymin)*100000+int(self.xmin)
        self.euclidDistance = int(
            np.sqrt(np.square(self.ymin)+np.square(self.xmin)))
        self.width = self.xmax-self.xmin
        self.height = self.ymax - self.ymin

    def geteuclidDistance(self):
        return self.euclidDistance

    def getHeight(self):
        return(self.height)

    def getWidth(self):
        return(self.width)

    def getXyPos(self):
        return self.xyPos

    def getNextResultLet(self, results):
        xdist = self.width*numCharBoxDistance
        neighborIndex = InfeasibleNeighbor
        isResultMulitpleBoxes = False
        for i in range(len(results)):  # Find current box
            # will exclude the self identified same x n y co-ordinates
            if self.xmin == results[i].xmin and self.ymin == results[i].ymin and self.xmax == results[i].xmax and self.ymax == results[i].ymax:
                currentBoxFOund = True
                currentIndex = i
                break
            else:
                continue
        # Assumption is that search for next is sequential in the results
        # for the other indices from current one
        for i in range(currentIndex, len(results)):
            if i == currentIndex:
                continue  # skip current index
            if ((abs((self.xmax - results[i].xmin) / self.width*100) < widthOverlapPercent) and (abs((self.ymin - results[i].ymin) / self.height*100) < heightOverlapPercent)):
                if xdist > (results[i].xmin - self.xmax):
                    xdist = (results[i].xmin - self.xmax)
                    neighborIndex = i
        if neighborIndex == InfeasibleNeighbor:
            return -1, False, False
        else:
            isResultMulitpleBoxes = False
            overlappingBoxes = [neighborIndex]
            for j in range(currentIndex, len(results)):
                if j == currentIndex:
                    continue
                if abs((results[currentIndex].xmin-results[j].xmin)/results[currentIndex].width)*100 < xdeviationPercent and \
                        abs((results[currentIndex].ymin - results[j].ymin) / results[currentIndex].height) * 100 < ydeviationPercent:
                    overlappingBoxes.append(j)
                    isResultMulitpleBoxes = True

            wordGap = False
            # if gap between characters is more than numBoxGaps boxes, its assumed to be word gap
            if (results[neighborIndex].xmin - self.xmax) > numBoxGaps*self.width:
                wordGap = True
            else:
                wordGap = False

            return overlappingBoxes, wordGap, isResultMulitpleBoxes


class_map = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9',  10: 'B', 11: 'C', 12: 'D', 13: 'E',  14: 'G',
             15: 'H',  16: 'K', 17: 'M', 18: 'N',  19: 'P', 20: 'T',  21: 'W', 22: 'ROI', 23: 'ROI-SN', 24: 'PSN', 25: 'PR', 26: 'BL', 27: 'TL'}


class Results:
    def __init__(self, classes_list, bboxList, scoreList):
        self.results = []
        self.lines = []
        self.class_names = []
        for i in range(len(classes_list)):
            cn = list(class_map.values())
            item = classes_list[i]
            self.class_names.append(cn[item])
            self.results.append(
                resultLet(self.class_names[i], bboxList[i], scoreList[i]))
        self.results.sort(key=lambda x: x.euclidDistance)

    def getClosesToOrigin(self):
        return(self.results[0])

    def getLinesNwords(self):
        if len(self.lines) < 1:
            self.createLinesNwords()
        return(self.lines)

    def createLinesNwords(self):
        currentWord = []

        currentIndex = 0
        setCharIndex = set(range(len(self.results)))

        lineIdex = 0
        wordIndex = 0
        charIndex = 0
        self.lines = []  # first word with index = 0
        currentLine = []
        currentWord = []  # Set current word to empty list ?? or should I set current word to line 0 and word zero
        # Start with first character in the results
        for currIndex in range(len(self.results)):

            if currIndex in setCharIndex:  # If the current charater under consideration still needs to be considered
                #debugPrint(debugMessage((str(currIndex)) + ' is considered; processing it for its neighbor',0))
                currentWord.append([currIndex])  # Append it to current word
                # and remove from further consideration
                setCharIndex.remove(currIndex)
                # get next (nearest right side character) from the same line; the function also finds alternative
                # proposals for next and if the next character is word distance away or if it is the last in that line
                wordChar, iswordEnd, isMultipleBoxes = self.results[currIndex].getNextResultLet(
                    self.results)
                if wordChar == -1:
                    self.lines.append(currentLine)
                    currentLine = []
                    currentWord = []
                    continue
                # if there are more characters in the line; else start a new line and start the process for that line
                if iswordEnd:  # If the current character is the start of new word then
                    # Store current word into current line
                    currentLine.append(currentWord)
                    # reset current word to empty list; will it also make the save word to empty? check
                    currentWord = []
                # word char is list having one or more characters
                currentWord.append(wordChar)
                # if there are multiple char propositions for the same space delete all but one from further consideration
                if isMultipleBoxes:
                    # just keep one overallping char to go to next word
                    for j in range(len(wordChar)-1):
                        setCharIndex.remove(wordChar[j])
            else:
                debugPrint(debugMessage(
                    str(currIndex) + ' is already considered; Skipping the processing', 0))


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
        if score < charAlternatives[i+1].score:
            currChar = charAlternatives[i].category
            score = charAlternatives[i].score
    return currChar, score


def getBestWordWithScore(words):
    word = []
    score = 1.0
    list_score = []
    for j in range(len(words)):
        if len(words[j]) > 1:
            charClass, ClassScore = get_bestCharClass(words[j])
            word.append(charClass)
            score = score * ClassScore
            list_score.append(ClassScore)
        else:
            word.append(words[j][0].category)
            score = score * words[j][0].score
            list_score.append(words[j][0].score)
    return word, score, list_score


def get_named_strings(names, results):
    extractedResults = {}

    for i in range(len(names)):
        label2Process = names2LabelMap[names[i]]
        extractedResults[label2Process] = []
        outBox = None
        for j in range(len(results.results)):
            if results.results[j].category == label2Process:
                outBox = OuterBox(
                    results.results[j].xmin, results.results[j].ymin, results.results[j].xmax, results.results[j].ymax)

                break
        insideBoxes = []  # Initialize boxes contained within the label; get boxes -->
        for j in range(len(results.results)):
            if outBox.containsBox(results.results[j]):
                # ELiminating all the boxes less than threshold; Bad for learning
                if results.results[j].score > scoreThreshold:
                    insideBoxes.append(results.results[j])
        words = []
        for j in range(len(insideBoxes)):
            alternateChars = [insideBoxes[j]]
            for k in range(j+1, len(insideBoxes)):
                if insideBoxes[k].score > scoreThreshold:
                    if isOverLapping(insideBoxes[j], insideBoxes[k]):
                        alternateChars.append(insideBoxes[k])
            words.append(alternateChars)
        # Following gives the best word based on the score.
        # But what we need is the list of all possible words with their scores
        word, score, list_score = getBestWordWithScore(words)
        extractedResults[label2Process].append(LabelResult(word, score, list_score))
    return extractedResults


def getPrefix(im, prediction, key='PR'):
    outputs = prediction(im)
    classes = outputs['instances'].pred_classes
    boxes = outputs['instances'].pred_boxes
    scores = outputs['instances'].scores
    classes_list = classes.tolist()
    scores_list = scores.tolist()
    boxes_list = boxes.tensor.tolist()
    results = Results(classes_list, boxes_list, scores_list)
    labelDict = get_named_strings(names, results)
    prefix = ''.join(labelDict.get(key)[0].label)
    score = labelDict.get(key)[0].score
    list_score_fnl = labelDict.get(key)[0].list_score
    conf, conf_band = confidence_band(list_score_fnl, 4)
    out_obj = {}
    out_obj['ocrValue'] = prefix
    out_obj['confValue'] = conf
    out_obj['confBand'] = conf_band
    return out_obj
