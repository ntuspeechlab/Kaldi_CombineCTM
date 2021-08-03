# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 20:11:03 2021

@author: aseschng
"""
#!/usr/bin/env python3
"""
Author: Chng Eng Siong
Date: 31 July 2021
Last edited: 1st Aug 2021 (CES), 11:07pm
Objective: to convert the ctm file to text file
Usage: python3 run_saveCTM_as_Text.py --ctm yourCTMFileName.ctm
"""
#
import logging
import os, sys, io
import argparse
from   libCTM import C_ArrayUttCTM   # eng siong's CTM library 

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
log = logging.getLogger("{}".format(os.path.basename(sys.argv[0])))




# Example to run the code
# python3 run_saveCTM_as_Text.py --ctm ./TestData/yourCTMFileName.ctm
# it will generate youCTMFileName.txt

       
def real_main():        
    log.info("{}".format("Save CTM as text file for WER scoring ..."))
    parse = argparse.ArgumentParser()
    parse.add_argument('--ctm', required=True,  help="ctm file ")
    args = parse.parse_args()
 
    print('Release 3rd Aug 2021, 807pm\n')    
    uttFileCTM = C_ArrayUttCTM()
    uttFileCTM.readCTMFile(args.ctm) 

    opFileName = args.ctm[0:len(args.ctm)-4]+'.txt'
    uttFileCTM.writeTextFile(opFileName)
    
    
    print('===============  completed ===================')
    
    
def main():
    real_main()
    
if __name__ == "__main__":
    main()
