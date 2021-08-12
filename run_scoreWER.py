# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 20:11:03 2021

@author: aseschng
"""
#!/usr/bin/env python3
"""
Author: Chng Eng Siong
Date: 6 Aug 2021
Objective: This file scores WER
Usage: python3 run_scoreWER.py --ref refFile --hyp inHypFile --op opWERresultFile
       we will use subprocess of python to call compute-wer
"""

import logging
import argparse
import subprocess
import sys,os

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
log = logging.getLogger("{}".format(os.path.basename(sys.argv[0])))



# We will assume we have three types of extension
#        a) HypCTM_hotwordONLY.txt
#        b) HypCTM_Wordwithhotword.txt
#        b) HypCTM_WordONLY.txt


#run_scoreWER.py --ref refFile --hyp inHypFile --op opWERresultFile
       
def real_main():        
    log.info("{}".format("WER scoring for CTM for (hotwordONLY, Wordwithhotword, WordONLY) ..."))
    parse = argparse.ArgumentParser()
    parse.add_argument('--ref', required=True,  help="ref file ")
    parse.add_argument('--hyp', required=True,  help="hyp file ")
    parse.add_argument('--remarkStr', required=True,  help="remarkString to describe Expt")
    parse.add_argument('--opFileName', required=True,  help="opfilename to be saved")
    args = parse.parse_args()
 
    print('Release 6rd Aug 2021\n')    
    typeExtension = ['_WordONLY.txt','_WordAndHotWordLabel.txt', '_HOTWordONLY.txt']
    refFile  = args.ref
    hypFile  = args.hyp
    opFIle   = args.opFileName

    for ext in typeExtension:
        refFileExt = refFile+ext
        hypFileExt = hypFile+ext
        result = subprocess.run(["compute-wer", "--text", "--mode=present",
            "ark:"+refFileExt,"ark:"+hypFileExt], capture_output=True, text=True)
        print("\nWER "+args.remarkStr + ext+'\n'+result.stdout)
        #print("stderr:", result.stderr)

    print('===============  completed ===================')
    
    
def main():
    real_main()
    
if __name__ == "__main__":
    main()
