#!/usr/bin/env python3
"""
Author: Chng Eng Siong
Date: 31 July 2021
Last edited: 1st Aug 2021 (CES), 11:07pm
Objective: combing CTM files of Master and HotWordDecoder to form DualASR CTM File
Usage: python3 test_combineCTM.py --master_ctm your_master.ctm --hotword_ctm your_hotword.ctm --collar_rate 0.25 --dual_ctm your_dual.ctm  
 
"""
#
import logging
import os, sys, io
import argparse
from   libCTM import C_ArrayUttCTM   # eng siong's library 
import libCTM

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
log = logging.getLogger("{}".format(os.path.basename(sys.argv[0])))




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

    print('Release 1st Aug 2021, 1107pm\n')    
    uttFileMasterCTM = C_ArrayUttCTM()
    uttFileMasterCTM.readCTMFile(args.master_ctm) 

    uttFileHotWordCTM = C_ArrayUttCTM()
    uttFileHotWordCTM.readCTMFile(args.hotword_ctm)  

    dualDecoderCTM = C_ArrayUttCTM()
    collar  = args.collar_rate
    # This value should be between 0~0.5? tells you how much to eat into the next word duration
    
    for (eachMasterUtt, eachHotWordUtt) in zip(uttFileMasterCTM.arrayUttCTM,
                                               uttFileHotWordCTM.arrayUttCTM):
        oneUttHotWordONLYCTM = libCTM.fn_retainOnlyHotWord(eachHotWordUtt)
        retCTM               = libCTM.fn_combineMasterCTM_HotWordCTM(eachMasterUtt, 
                                                  oneUttHotWordONLYCTM, collar)
        dualDecoderCTM.addUttCTM(retCTM)
        
    dualDecoderCTM.writeCTMFile(args.dual_ctm)
    
    
    print('===============  completed ===================')
    
    
def main():
    real_main()
    
if __name__ == "__main__":
    main()
