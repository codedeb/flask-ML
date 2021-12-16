import jellyfish as jf
import logging

logging.basicConfig(format='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

#Siva: ***Important **** Code cleanup using try catch and logging for maintaining and updating the code

#Siva: This needs to be created as the object with constants being initialized from config file and config file
#being specified via init method.
#It requires: 1. alphaNum list 2. charConfDistance of size alphaNum, 3. List of groundTruth Prefixes (lPrefixes)
#4. maxDistance
#Convert global variables to object properties, enable get and set methods
#Enable loading and saving of charConfusionDistance from outside of the app (an important piece of continuous
#Learning.

#Siva: Create and init AplhaNum character list
# To Do: 35 to be as config len(alphanums) - 1
alphaNums = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
class ConfusionProb():
    # Probability of character being mistaken for another; At preset simple assumption is that it is equal for all
    # other characters (36-1 of them) and equals 0.1%. So a character being recognized as it is 96.5% (100-0.1*35)
    # These probs will be updated by learning algorithm based on actual mis-classifications based on frequency of occurances
    # Requires thinking and proper design to maintain semantics
    # probability if 'x' being recognized as 'x'
    selfProb = 1 - 35 * 0.001
    # probability of misclassifying into another character
    misClassificationProb = 0.001
    # Siva: Create and init AplhaNum character confusion matrix
    # Its a square matrix of alphaNums
    alphaNums=[]
    charConfusionDistance = {}
    def __init__(self,an,anMatrix=None):
        self.alphaNums = an
        if anMatrix != None:
            self.charConfusionDistance = anMatrix
        else:
            self.charConfusionDistance = self.initAlphaNumDistance(self.charConfusionDistance,self.alphaNums,self.selfProb,self.misClassificationProb)

    def initAlphaNumDistance(self,charConfusionDistance,alphaNums,selfProb,misClassificationProb):
        #charConfusionDistance = {}
        for item in alphaNums:
            charConfusionDistance[item] = {}
            for innerItem in alphaNums:
                if item == innerItem:
                    charConfusionDistance[item][innerItem] = selfProb
                else:
                    charConfusionDistance[item][innerItem] = misClassificationProb
        return charConfusionDistance

    # Siva: Following is based on the frequency of errors of detection
    # out of 100 times, 1 is actually L 2 time, 1 is D 1 times, and 1 97 times
    # So character cofusion distance is [sourceCharacter][toCharacter] = frequencyOfThisConfusion/Total Occurances
    # Overall probability scores need to add up to 1
    # Here charConfDistance is a squae matrix of aplpaNums
    # This matrix needs to be read from a file; This matrix should be created and maintained from the user feedback
    # and observed errors from the algorithm
    # Siva: Not a simple task to automate for continuous learning

    def updateCellProb(self,f, t, freq, total):
        if isinstance(f, str) and isinstance(t, str):
            try:
                self.charConfusionDistance[f][t] = freq / total
                self.charConfusionDistance[f][f] = self.selfProb - self.charConfusionDistance[f][t] + self.misClassificationProb
                return True
            except:
                print('UpdateCellProb: failed to update probability from %s to %; inputs are: %s, %s, %s, %s', f, t, f,
                      t, freq, total)
            return False
        else:
            print('From and To objects need to be strings')
            return False  # don't change anything but return error


#Siva: List of valid prefixes
#In final version these need to be read from a filw whihc is created maintained outside of the app
lPrefixes =['C2NP','K2LP','K2MM','K2LM','K3WP','K3FM','K1BP','K1AP','K3FP','K2DP','K1JP','K3JP','K1AM','K2NM']

#Siva: Return the distance from source word to destination word for a given matrix of confusion distance
def getwordDistance(wf,wt,charConfDistance):
    prob = 1
    if len(wf) != len(wt):
        print('Error: Word lengths are not same. \nAt present works only for words of same length')
        exit()
    for i in range(len(wf)):
        if wf[i] == wt[i]:
            continue
        else:
            prob = prob * charConfDistance[wf[i]][wt[i]]  #Siva default distance is 1 for each position
    return (prob)
#Siva: for a given source word get the list of  words from ground truth list with minimum distance,
# and the minimum distance
def getClosest(word,lWords,maxDistance):
    wrdDst = {}
    least = maxDistance
    closest=[]
    for item in lWords:
        wrdDst[item] = jf.damerau_levenshtein_distance(word,item)
        if wrdDst[item] < least:
            least = wrdDst[item]
    for item in lWords:
        if least == wrdDst[item]:
            closest.append(item)
    return closest,least
#charConfDistance = initAlphaNumDistance()
# alphaNums = ['0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

#Siva: Function to be exported from this module
#Need to convert this to Object and expose only following as the public function

def getCorrectPrfix(pfx): #Give closest from Ground truth and its distance from source word
    logger.info('Correct prefix Input:%s' % pfx)
    if pfx == '':
        logger.info('Null Prefix received; Cant process')
        return('',0.0)
    if pfx in lPrefixes:
        logger.info('list: %s' % lPrefixes)
        return pfx,0.0

    # Siva: Max number of operations of 'insert, delete, swap, that need to be done to go from source string
    # to destination String

    correct,distance = getClosest(pfx,lPrefixes,maxDistance)
    logger.debug('Correct Prefix: %s ' % correct)
    logger.debug('Distance: %s ' % distance)
    w2d = {} #Man, this naming is getting on my nerves; Need better naming
    overallProb = 1
    overallDistance = maxDistance
    for w in correct:
        if len(pfx) != len(w): #Siva: If the inpword and corrected word are of not same length accept the algo distance
            w2d [w] = distance*overallProb
        else: #Siva: else modify the distance based on the confusion frequency
            w2d[w] = distance* (1-getwordDistance(pfx,w,confusionProb.charConfusionDistance)) #since shorter distance is better; we weight the distance with 1-prob so that low prob will yield high distance
        if w2d[w] < overallDistance:
            overallDistance = w2d[w]
            ans = w
    # logger.info(w2d,'Least Weighted:',overallDistance)
    # logger.info(ans,overallDistance)
    logger.debug('overallDistance: %s ' % overallDistance)
    return(ans,overallDistance)
#***Set the confusion object and update the frequency based probabilities
maxDistance = 1000
confusionProb = ConfusionProb(alphaNums)
# charConfDistance = initAlphaNumDistance()

confusionProb.updateCellProb('1', 'L', 2, 100)
confusionProb.updateCellProb('1', 'L', 1, 100)
confusionProb.updateCellProb('N', 'L', 2, 100)
confusionProb.updateCellProb('X', 'M', 2, 100)
confusionProb.updateCellProb('W', 'L', 3, 100)
confusionProb.updateCellProb('2', 'L', 1, 100)
confusionProb.updateCellProb('P', 'L', 2, 100)
confusionProb.updateCellProb('B', 'L', 1, 100)

#Input word for testing
# inpword = '2NP'
# for wrd in lPrefixes:
#    print('***',wrd,getCorrectPrfix(wrd))
# print('***',inpword,getCorrectPrfix(inpword))