# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 20:11:03 2021

@author: aseschng
"""
#!/usr/bin/env python3
"""
Author: Chng Eng Siong
Date: 6 Aug 2021
Objective: to convert the ctm file to text file ready for WER
Usage: python3 run_convertCTM_toWERscoringText.py --ctm yourCTMFileName.ctm --hotword hotwordList.txt

This function allows CTM files to saved as text files so that WER can be called
we will  need a hotword list to convert as well

"""
#
import logging
import os, sys, io
import argparse
from   libCTM     import C_ArrayUttCTM   # eng siong's CTM library 
from   libWord    import C_WordList

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
log = logging.getLogger("{}".format(os.path.basename(sys.argv[0])))




# Example to run the code
# python3 run_convertCTM_toWERscoringText.py  --ctm ./TestDataOp/dual_WordwithHotWord.ctm --hotwordRawList ./TestData_Clean/hotwordRawList.txt --opFileName ./TestDataOp/dual
# if your ctm file has filename extension .txt, then it assumes every line is a sentence
#  -> it will generate 3 types of outputfiles:
#        a) yourCTM_hotwordONLY.txt
#        b) yourCTM_Wordwithhotword.txt
#        b) yourCTM_WordONLY.txt


       
def real_main():        
    log.info("{}".format("Save CTM as text file for WER scoring ..."))
    parse = argparse.ArgumentParser()
    parse.add_argument('--ctm', required=True,  help="ctm file ")
    parse.add_argument('--hotwordRawList', required=True,  help="hotword raw list file ")
    parse.add_argument('--opFileName', required=True,  help="opfilename to be saved")
    args = parse.parse_args()
 
    print('Release 6rd Aug 2021\n')    
    uttFileCTM = C_ArrayUttCTM()
    if (args.ctm[-4:len(args.ctm)] == '.txt'):
        uttFileCTM.readTextFile(args.ctm) 

    if (args.ctm[-4:len(args.ctm)] == '.ctm'):
        uttFileCTM.readCTMFile(args.ctm) 

    listHotWord = C_WordList()
    listHotWord.read_WordList( args.hotwordRawList, True)  # we must remember to tell the function that this is HOTWORDS

    # the CTM class .saveCTM_HotWordOnly returns a uttArrayCTM class that have each utterance with ONLY hotwords!
    uttArrayHotWordONLY = uttFileCTM.saveCTM_HotWordOnly(listHotWord)
    uttArrayHotWordONLY.writeTextFile(args.opFileName+'_HOTWordONLY.txt')

    # the CTM class .saveCTM_WordOnly returns a uttArrayCTM class that have each utterance with ONLY hotwords!
    uttArrayWordONLY = uttFileCTM.saveCTM_WordOnly(listHotWord)
    uttArrayWordONLY.writeTextFile(args.opFileName+'_WordONLY.txt')

    
    # the CTM class .saveCTM_WordOnly returns a uttArrayCTM class that have each utterance with ONLY hotwords!
    uttArrayWordAndHotWordLabel = uttArrayWordONLY.saveCTM_WordAndHotWordLabel(listHotWord)
    uttArrayWordAndHotWordLabel.writeTextFile(args.opFileName+'_WordAndHotWordLabel.txt')

    
    print('===============  completed ===================')
    
    
def main():
    real_main()
    
if __name__ == "__main__":
    main()
