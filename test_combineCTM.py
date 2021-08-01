#!/usr/bin/env python3
"""
Author: Chng Eng Siong
Date: 31 July 2021
Last edited: 1st Aug 2021 (CES)
Objective: combing CTM files of Master and HotWordDecoder to form DualASR CTM File
"""
#
import logging
import os, sys, io
import argparse
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
    def __init__(self, fileID, StartTime,DurTime,wordStr):
            self.fileID    = fileID
            self.StartTime = StartTime
            self.DurTime   = DurTime
            self.EndTime   = StartTime+DurTime
            self.wordStr   = wordStr

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
                OneWordCTM = C_WordCTM(UttID,StartTime, DurTime, wordStr) 
            
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


# find and return which index in MasterCTM is timeVal in
def fn_find_CurrWord(MasterCTM, timeVal):
    foundIdx   = -1;
    startTime  = 0

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


#Example to run the code
#python3 test_combineCTM.py --master_ctm ./TestData/master.ctm --hotword_ctm ./TestData/hotword.ctm --collar_rate 0.25 --dual_ctm ./TestData/dual.ctm  
       
def real_main():        
    log.info("{}".format("Combining Master and Hotword CTM filesgenerated by KALDI ..."))
    parse = argparse.ArgumentParser()
    parse.add_argument('--master_ctm', required=True,  help="ctm file generated by Master Kaldi ASR")
    parse.add_argument('--hotword_ctm', required=True, help="ctm file generated by Keyword Kaldi ASR")
    parse.add_argument('--collar_rate', type=float, default=0.25, help="Overlapping time to insert hotword (%) between Master and Keyword")
    parse.add_argument('--dual_ctm', required=True, help="merged output")

    args = parse.parse_args()
    print(args.master_ctm,args.hotword_ctm,args.collar_rate, args.dual_ctm)

    print('Release 1st Aug 2021, 930pm\n')    
    uttFileMasterCTM = C_ArrayUttCTM()
    uttFileMasterCTM.readCTMFile(args.master_ctm) 

    uttFileHotWordCTM = C_ArrayUttCTM()
    uttFileHotWordCTM.readCTMFile(args.hotword_ctm)  

    dualDecoderCTM = C_ArrayUttCTM()
    collar  = args.collar_rate
    # This value should be between 0~0.5? tells you how much to eat into the next word duration
    
    for (eachMasterUtt, eachHotWordUtt) in zip(uttFileMasterCTM.arrayUttCTM,
                                               uttFileHotWordCTM.arrayUttCTM):
        oneUttHotWordONLYCTM = fn_retainOnlyHotWord(eachHotWordUtt)
        retCTM               = fn_combineMasterCTM_HotWordCTM(eachMasterUtt, 
                                                  oneUttHotWordONLYCTM, collar)
        dualDecoderCTM.addUttCTM(retCTM)
        
    dualDecoderCTM.writeCTMFile(args.dual_ctm)
    print('===============  completed ===================')
    
    
def main():
    real_main()
    #unit_test_combine()
    
if __name__ == "__main__":
    main()
