#!/usr/bin/env python3
"""
Filename: libCTM.py (to be imported as a module)
Author: Chng Eng Siong
Date: 31 July 2021
Last edited: 1st Aug 2021 (CES), 11:07pm
Objective: combing CTM files of Master and HotWordDecoder to form DualASR CTM File
"""
#
import logging
import os, sys, io
import argparse
from   dataclasses import dataclass
from   typing import List
from   libWord import C_WordList


logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
log = logging.getLogger("{}".format(os.path.basename(sys.argv[0])))


# This simple class contains a single word's information from CTM
# CTM is kaldi format to retain start/end time, in this case we are rememebering for each word
# the original kaldi has startTime and duration, we have kept the end time for convenience!
# the fileID is basically the utterance id (?) infromation 
@dataclass
class C_WordCTM:
    fileID: str
    StartTime: float
    EndTime: float
    DurTime: float    
    wordStr: str
    def __init__(self, fileID, StartTime,DurTime,wordStr):
            self.fileID    = fileID
            self.StartTime = StartTime
            self.DurTime   = DurTime
            self.EndTime   = StartTime+DurTime
            self.wordStr   = wordStr


#
# This simple class contains an utterance's information from CTM
# given an utterance, we have an array (list) of wordCTM
# we will also keep the uttStr, basically keeping all the words in the wordCTM as a string
# uttName is the name of the utterance
# uttStr == the array of word in the wordCTM
#
@dataclass
class C_UttCTM:
    uttName: str
    arrayWord: List[C_WordCTM]
    uttStr: str
 
    def __init__(self, uttName, uttStr):
        self.uttName   = uttName
        self.uttStr    = uttStr
        self.arrayWord = []
       
    # we assume we will add one word at a time
    # this allow us to update the uttStr as we add into the class    
    def addWordCTM(self, oneWordCTM):
        self.arrayWord +=[oneWordCTM]
        if len(self.uttStr) != 0:
            self.uttStr  += ' '+oneWordCTM.wordStr
        else:
            self.uttStr   = oneWordCTM.wordStr
            # this is the first word added, thats why uttStr has length == 0

    
# This class contains all utterance from a CTM file
# We will remember the filename, and keep all the utterance as a list
@dataclass
class C_ArrayUttCTM:
    fileName: str
    arrayUttCTM: List[C_UttCTM]
    dictNameToUtt = {}    

    def __init__(self):
        self.fileName = ''
        self.arrayUttCTM = []
        self.dictNameToUtt = {}

    def addUttCTM(self, oneUttCTM):
        self.arrayUttCTM += [oneUttCTM]
        if self.verifyUttNameExist(oneUttCTM.uttName) == 0:
            self.dictNameToUtt[oneUttCTM.uttName] = oneUttCTM
            # we will savely add the utt into the array
        else:
            log.warning("Trying to add oneUttCTM but uttName already exist"+oneUttCTM.uttName)

    def verifyUttNameExist(self,testUttName):
        if testUttName in self.dictNameToUtt.keys(): 
            return 1
        else:
            return 0           

    def getCTMfromUttName(self, testUttName):
        if self.verifyUttNameExist(testUttName) == 1:
            return self.dictNameToUtt[testUttName]
        else:
            return 0



    # the CTM file format is this
    # fileID 1 startTime duration singleWord (or hotwordlabel)
    def fn_ctmParseLine(self,line):
        tokenArray=line.split()
        if len(tokenArray)!=5:
            log.warning("Fatal Error in CTM line '{}', expecting 5 tokens ONLY".format(line))
        else:
            (fileID, StartTime, EndTime, DurTime, wordStr) = (tokenArray[0], float(tokenArray[2]), 
                                                     round(float(tokenArray[2])+float(tokenArray[3]),5),
                                                     float(tokenArray[3]),tokenArray[4])
        return (fileID, StartTime, EndTime, DurTime, wordStr)




    def writeCTMFile(self, fileName):
        log.info("Writing CTM File : ({})".format(fileName))

        opfile = open(fileName,"w",encoding='utf8')
        for eachUtt in self.arrayUttCTM:
            for eachWord in eachUtt.arrayWord: 
                opfile.write("{0} 1 {1:6.2f} {2:6.2f} {3}\n".format(
                    eachWord.fileID, eachWord.StartTime, eachWord.DurTime, eachWord.wordStr))
        opfile.close()
        log.info("Completed Writing CTM File ({}) has ({}) entries".format(fileName,len(self.arrayUttCTM)))


        
    def readCTMFile(self, fileName):
        self.arrayUttCTM = []
        currUttName = ''
        log.info("Reading CTM File : ({})".format(fileName))
        with open(fileName, 'r', encoding='utf8') as infile:
            for line in infile:
                line = line.strip()
                line = line.lower()
                (uttID, startTime, endTime, durTime, wordStr) = self.fn_ctmParseLine(line)
                oneWordCTM = C_WordCTM(uttID,startTime, durTime, wordStr) 
            
                # This happens only the first time
                if  currUttName == '':
                    currUttName = uttID
                    oneUttCTM   = C_UttCTM(uttID,'')

                # Lets keep adding word        
                if currUttName == uttID:
                    oneUttCTM.addWordCTM(oneWordCTM)
                else:  # We have parse to a new utterance in the ctm file
                    self.addUttCTM(oneUttCTM)
                    oneUttCTM   = C_UttCTM(uttID,'')
                    currUttName =  uttID
                    oneUttCTM.addWordCTM(oneWordCTM)

            # To take care of the last utterance to be saved!            
            self.addUttCTM(oneUttCTM)
            log.info("Completed Reading CTM File ({}) has ({}) entries".format(fileName,len(self.arrayUttCTM)))
            infile.close()



    # This format is for WER scoring, each line is uttID and the string (of the utterance)
    # here we assume that the CTM file ONLY contain the fileID and string (of the utterence)
    def fn_textParseLine(self,line):
        tokenArray=line.split()
        fileID = tokenArray[0];
        if (len(tokenArray)>=1):
            uttStr = tokenArray[1]
            for tt in tokenArray[2:len(tokenArray)]:
                uttStr += ' '+tt
        else:
            uttStr = ''

        return (fileID, uttStr)

           

    # This function assumes the CTM file ONLY contain fileID and string
    def readTextFile(self, fileName):
        self.arrayUttCTM = []
        currUttName = ''
        log.info("Reading CTM Text File : ({})".format(fileName))
        with open(fileName, 'r', encoding='utf8') as infile:
            for line in infile:
                line = line.strip()
                line = line.lower()
                (uttID, uttStr) = self.fn_textParseLine(line)
                if (len(uttStr)> 0):
                    oneUttCTM  = C_UttCTM(uttID, uttStr) 
                    self.addUttCTM(oneUttCTM)    
                        


    # uttid  text-per-sentence
    def writeTextFile(self, fileName):
        log.info("Writing Text File : ({})".format(fileName))

        opfile = open(fileName,"w",encoding='utf8')
        for eachUtt in self.arrayUttCTM:
            # we can write the utterance if we have an array of words
            if (len(eachUtt.arrayWord) > 0):
                opfile.write("{0} ".format(eachUtt.arrayWord[0].fileID))
                for eachWord in eachUtt.arrayWord: 
                    opfile.write("{0} ".format(eachWord.wordStr))
            else:
                    # or we directly use the uttStr, which should be the same!!!!
                    # The two SHOULD be the same! bottom -> we initialse from text file
                    opfile.write("{0} ".format(eachUtt.uttName))
                    opfile.write(eachUtt.uttStr)
                    # the uttStr should have saved it as well !!! :)    
            opfile.write('\n')    
        opfile.close()
        log.info("Completed Text File ({}) has ({}) entries".format(fileName,len(self.arrayUttCTM)))


    # here we ONLY consider hotword of the forms __xxx_yy_xxx, __xx_yy_xx
    # This is just a quick hack! 
    # we should be checking the hotword list
    #def fn_splitHotWord(self,inStr):
    #    split_hotWordStr = inStr.replace('__','').replace('_',' ')
    #    return(split_hotWordStr)

    # uttid  text-per-sentence
    #def writeTextFile_SplitHotWord(self, fileName):
    #    log.info("Writing Text File : ({})".format(fileName))

    #    opfile = open(fileName,"w",encoding='utf8')
    #    for eachUtt in self.arrayUttCTM:
    #        opfile.write("{0} ".format(eachUtt.uttName))
    #        split_hotWordStr = self.fn_splitHotWord(eachUtt.uttStr)
    #        opfile.write("{0} ".format(split_hotWordStr))
    #        # the uttStr should have saved it as well !!! :)    
    #        opfile.write('\n')    
    #    opfile.close()
    #    log.info("Completed Text File ({}) has ({}) entries".format(fileName,len(self.arrayUttCTM)))


    # 
    # this function returns a CTM with ONLY HOTWORD entiries
    # listHotWord is a dictionary containing ALL the hotwords already
    # it has a method to convert its input string to required format
    #
    def saveCTM_HotWordOnly(self,listHotWord):
        newArrayCTM = C_ArrayUttCTM()
        for eachUtt in self.arrayUttCTM:
            hotWordOnlyStr = listHotWord.convertStrToHotWordLabel_ONLY(eachUtt.uttStr)
            oneUttCTM  = C_UttCTM(eachUtt.uttName, hotWordOnlyStr) 
            newArrayCTM.addUttCTM(oneUttCTM)
        return newArrayCTM

    # this function returns a CTM with Word ONLY entiries
    # listHotWord is a dictionary containing ALL the hotwords already
    # it has a method to convert its input string to required format
    #
    def saveCTM_WordOnly(self,listHotWord):
        newArrayCTM = C_ArrayUttCTM()
        for eachUtt in self.arrayUttCTM:
            wordAndhotWordStr = listHotWord.convertLabelToWord(eachUtt.uttStr)
            oneUttCTM  = C_UttCTM(eachUtt.uttName,wordAndhotWordStr) 
            newArrayCTM.addUttCTM(oneUttCTM)
        return newArrayCTM

    # this function returns a CTM with Word And HOTWordLabel entiries
    # listHotWord is a dictionary containing ALL the hotwords already
    # it has a method to convert its input string to required format
    #
    def saveCTM_WordAndHotWordLabel(self,listHotWord):
        newArrayCTM = C_ArrayUttCTM()
        for eachUtt in self.arrayUttCTM:
            wordAndhotWordLabel = listHotWord.convertStrToHotWordLabel(eachUtt.uttStr)
            oneUttCTM  = C_UttCTM(eachUtt.uttName,wordAndhotWordLabel) 
            newArrayCTM.addUttCTM(oneUttCTM)
        return newArrayCTM
                    
## End of definition for class C_ArrayUttCTM
            

# I dont like this function as IT does not use dictionary to solve the problem
# This function removes all words in the CTM that are 
# NOT hotwords, --> no __ in the 
# begining of the string
# BUT IT MUST be retained NOW because We are using the oneUTTCTM's original information of time
# #        if listHotWord.verifyIsHOTWORD(oneUttCTM.arrayWord[i].wordStr.lower()) == 1:
# and NOW the hotword is case sensitive, BUT the decoder op is NOT,
# so we have to prepare the lexicon for it first
#
def fn_retainOnlyHotWord(listHotWord, oneUttCTM):
    ret_utt = C_UttCTM(oneUttCTM.uttName,'')
    for i in range(0,len(oneUttCTM.arrayWord)):
        if oneUttCTM.arrayWord[i].wordStr[0:2] =='__':
            ret_utt.addWordCTM(oneUttCTM.arrayWord[i])
    return(ret_utt)



# combing the master and hotword decoder, we need to find where the word is in word index
# find and return which index in MasterCTM is timeVal in
def fn_find_CurrWord(MasterCTM, timeVal):
    foundIdx   = -1;

    # we have to be careful, words are not continuous in time
    for i in range(0,len(MasterCTM.arrayWord)):
        endTime = MasterCTM.arrayWord[i].EndTime
        if timeVal <= endTime:
            foundIdx = i
            break;
   
    if foundIdx == -1:  # this ONLY happens when we reach the end of the list
        foundIdx = len(MasterCTM.arrayWord)-1        

    return foundIdx        



# current collar is collar*durationword Word (should be a value between 0.1~0.4 I guess)       
def fn_findStartEndMasterIdx(MasterCTM, HotWordStartTime,HotWordEndTime,collar=0.1):

    StartIdx = fn_find_CurrWord(MasterCTM, HotWordStartTime)
    # case A, currWord in StartIdx is retained, and HotWord StartTime is pointing to end of currWord
    if HotWordStartTime >= MasterCTM.arrayWord[StartIdx].StartTime+((1-collar)*MasterCTM.arrayWord[StartIdx].DurTime):
        if (StartIdx+1 < len(MasterCTM.arrayWord)):
            StartIdx = StartIdx+1
        

    EndIdx = fn_find_CurrWord(MasterCTM, HotWordEndTime)
    # case C, currWord in EndIdx is retained, and HotWord EndTime is pointing to previous word's endTime!
    if HotWordEndTime <= MasterCTM.arrayWord[EndIdx].StartTime+(collar*MasterCTM.arrayWord[EndIdx].DurTime):
        if (EndIdx-1 >= 0) and (EndIdx-1 >= StartIdx):
            EndIdx = EndIdx-1

    return (StartIdx,EndIdx)




# This function combines the Master CTM and HotWord CTM
# We assume that the Master and HotWord CTM are arrange according to time!!!
def    fn_combineMasterCTM_HotWordCTM(MasterCTM, HotWordCTM, collar):        

    # By Kaldi, we can ONLY check that the two Utterances are same name
    if MasterCTM.uttName != HotWordCTM.uttName:    
        log.warning("cannot combine Master ({}) and HotWordCTM ({})".format(MasterCTM.uttName, HotWordCTM.uttName))

    retUttCTM = C_UttCTM(MasterCTM.uttName,'')  # By Kaldi convention, we cannot change UttName    
    numHotWord = len(HotWordCTM.arrayWord)
    lastStartIdx = 0

    if numHotWord == 0:     # there are cases when NO hotword is found!
        for j in range(0,len(MasterCTM.arrayWord)):
            retUttCTM.addWordCTM(MasterCTM.arrayWord[j])
    else:
        for i in range(numHotWord):
            HotWordStartTime = HotWordCTM.arrayWord[i].StartTime
            HotWordEndTime   = HotWordCTM.arrayWord[i].EndTime
            (startIdx_MasterCTMForHotWord,endIdx_MasterCTMForHotWord) = fn_findStartEndMasterIdx(MasterCTM, 
                HotWordStartTime,HotWordEndTime, collar)

            for j in range(lastStartIdx,startIdx_MasterCTMForHotWord):
                retUttCTM.addWordCTM(MasterCTM.arrayWord[j])
            retUttCTM.addWordCTM(HotWordCTM.arrayWord[i])
            lastStartIdx = endIdx_MasterCTMForHotWord+1;
            if (i == numHotWord-1):
                for j in range(endIdx_MasterCTMForHotWord+1,len(MasterCTM.arrayWord)):
                    retUttCTM.addWordCTM(MasterCTM.arrayWord[j])

    return retUttCTM


# A simple unit test for fn_combineMasterCTM_HotWordCTM function #
def unit_test_combine():        
    MasterUttCTM = C_UttCTM('Master CTM')
    MaxN = 10
    w = [C_WordCTM('testID',i*1.0,1.0, 'w'+str(i)) for i in range(MaxN)]
    for i in range(0,MaxN):
        MasterUttCTM.addWordCTM(w[i])

    print(MasterUttCTM,'\n')    

    HotWordUttCTM = C_UttCTM('HotWord CTM')
    hw1 = C_WordCTM('testID',1.1,0.2, '__hw1') ## What happen here!!!
    hw2 = C_WordCTM('testID',5.9,1.9, '__hw2') 
    hw3 = C_WordCTM('testID',9.0,0.2,'__hw3') 
    HotWordUttCTM.addWordCTM(hw1)
    HotWordUttCTM.addWordCTM(hw2)
    HotWordUttCTM.addWordCTM(hw3)

    print(HotWordUttCTM,'\n')
    collar = 0.1;
    retCTM =   fn_combineMasterCTM_HotWordCTM(MasterUttCTM, HotWordUttCTM, collar)
    print(retCTM)
    
################  Functions supporting CTM combination #############

    
# There is NO MAIN function, just testing codes    
#unit_test_combine()
    
