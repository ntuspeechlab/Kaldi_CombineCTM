#!/usr/bin/env python3
"""
Author: Chng Eng Siong
Date: 31 July 2021
Objective: combing CTM files of Master and HotWordDecoder to form DualASR CTM File
"""
#
import logging
import os, sys, io
from dataclasses import dataclass
from typing import List


logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
log = logging.getLogger("{}".format(os.path.basename(sys.argv[0])))


# This simple class contains a single word's information from CTM
@dataclass
class C_WordCTM:
    fileID: str
    StartTime: float
    EndTime: float
    DurTime: float    
    wordStr: str

# This simple class contains an utterance's information from CTM
@dataclass
class C_UttCTM:
    uttName: str
    arrayWord: List[C_WordCTM]
    def __init__(self, uttName):
        self.uttName = uttName
        self.arrayWord = []
        
    def addWordCTM(self, oneWordCTM):
        self.arrayWord +=[oneWordCTM]

    
# This class contains all utterance from a CTM file
@dataclass
class C_ArrayUttCTM:
    fileName: str
    arrayUttCTM: List[C_UttCTM]    

    def __init__(self):
        self.fileName = ''
        self.arrayUttCTM = []
        
    def addUttCTM(self, oneUttCTM):
        self.arrayUttCTM += [oneUttCTM]

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
                (UttID, StartTime, EndTime, DurTime, wordStr) = self.fn_ctmParseLine(line)
                OneWordCTM = C_WordCTM(UttID,StartTime, EndTime, DurTime, wordStr) 
            
                # This happens only the first time
                if  currUttName == '':
                    currUttName = UttID
                    OneUttCTM  = C_UttCTM(UttID)

                # Lets keep adding word        
                if currUttName == UttID:
                    OneUttCTM.addWordCTM(OneWordCTM)
                else:  # We have parse to a new utterance in the ctm file
                    self.addUttCTM(OneUttCTM)
                    OneUttCTM  = C_UttCTM(UttID)
                    currUttName =  UttID
                    OneUttCTM.addWordCTM(OneWordCTM)

            # To take care of the last utterance to be saved!            
            self.addUttCTM(OneUttCTM)
            log.info("Completed Reading CTM File ({}) has ({}) entries".format(fileName,len(self.arrayUttCTM)))
            infile.close()
            
                    
## End of definition for class C_ArrayUttCTM
            

# This function removes all words in the CTM that are NOT hotwords, --> no __ in the 
# begining of the string
def fn_retainOnlyHotWord(oneUttCTM):
    ret_utt = C_UttCTM(oneUttCTM.uttName+' HOT_WORD_ONLY')
    for i in range(0,len(oneUttCTM.arrayWord)):
        if oneUttCTM.arrayWord[i].wordStr[0:2] =='__':
            ret_utt.addWordCTM(oneUttCTM.arrayWord[i])
    return(ret_utt)


# current collar is collar*durationword Word (should be a value between 0.1~0.4 I guess)       
def fn_findStartEndMasterIdx(MasterCTM, HotWordStartTime,HotWordEndTime,collar=0.1):
    StartIdx = 0;    EndIdx   = len(MasterCTM.arrayWord)-1;
    # Lets find StartTime for HotWord in Master
    for i in range(1,len(MasterCTM.arrayWord)):
        durCurrWord = MasterCTM.arrayWord[i-1].EndTime-MasterCTM.arrayWord[i-1].StartTime
        if (HotWordStartTime- 0.5*durCurrWord) >= MasterCTM.arrayWord[i-1].StartTime :
            continue
        else:
            StartIdx = i-1;
            break

    # Lets find EndTime for HotWord in Master
    EndIdx = len(MasterCTM.arrayWord)-1  # lets just set to the end first!
    for i in range(0,len(MasterCTM.arrayWord)-1):
        durCurrWord = MasterCTM.arrayWord[i+1].EndTime-MasterCTM.arrayWord[i+1].StartTime
        if  (HotWordEndTime  >= (MasterCTM.arrayWord[i+1].StartTime + 0.5*durCurrWord)):
            continue;
        else:
            EndIdx = i;
            break  # get out of here
            
    return (StartIdx,EndIdx)



# This function combines the Master CTM and HotWord CTM
# We assume that the Master and HotWord CTM are arrange according to time!!!
def    fn_combineMasterCTM_HotWordCTM(MasterCTM, HotWordCTM, collar):        
    retUttCTM = C_UttCTM('Dual Utterance')    
    numHotWord = len(HotWordCTM.arrayWord)
    lastStartIdx = 0
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
    w = [C_WordCTM('testID',i*1.0,(i+1)*1.0,'w'+str(i)) for i in range(MaxN)]
    for i in range(0,MaxN):
        MasterUttCTM.addWordCTM(w[i])

    print(MasterUttCTM,'\n')    

    HotWordUttCTM = C_UttCTM('HotWord CTM')
    hw1 = C_WordCTM('testID',1.45,3.54, '__hw1') 
    hw2 = C_WordCTM('testID',5.90,7.70, '__hw2') 
    hw3 = C_WordCTM('testID',7.85,10.54,'__hw3') 
    HotWordUttCTM.addWordCTM(hw1)
    HotWordUttCTM.addWordCTM(hw2)
    HotWordUttCTM.addWordCTM(hw3)

    print(HotWordUttCTM,'\n')
    retCTM =   fn_combineMasterCTM_HotWordCTM(MasterUttCTM, HotWordUttCTM)
    print(retCTM)
    
################  Functions supporting CTM combination #############

  
       
def main():        
    log.info("{}".format("Combining Master and Hotword CTM filesgenerated by KALDI ..."))

    print('Release 31st July 2021, 11pm\n')    
    uttFileMasterCTM = C_ArrayUttCTM()
    uttFileMasterCTM.readCTMFile('./TestData/Master3Utt.ctm') 

    uttFileHotWordCTM = C_ArrayUttCTM()
    uttFileHotWordCTM.readCTMFile('./TestData/HotWord3Utt.ctm')  

    dualDecoderCTM = C_ArrayUttCTM()
    collar  = 0.25
    # This value should be between 0~0.5? tells you how much to eat into the next word duration
    
    for (eachMasterUtt, eachHotWordUtt) in zip(uttFileMasterCTM.arrayUttCTM,
                                               uttFileHotWordCTM.arrayUttCTM):
        oneUttHotWordONLYCTM = fn_retainOnlyHotWord(eachHotWordUtt)
        retCTM               = fn_combineMasterCTM_HotWordCTM(eachMasterUtt, 
                                                  oneUttHotWordONLYCTM, collar)
        dualDecoderCTM.addUttCTM(retCTM)
        
    dualDecoderCTM.writeCTMFile('./TestData/dualDecoder3Utt.ctm')
    print('===============  completed ===================')
    
    
    
    
if __name__ == "__main__":
    main()