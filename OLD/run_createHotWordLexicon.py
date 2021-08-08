# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6, 2021

@author: aseschng
"""
#!/usr/bin/env python3
"""
Author: Chng Eng Siong
Date: 6 July 2021
Last edited: 6 Aug 2021 (CES), 
Objective: to generate hotword lexicon

Usage: 
python3 run_createHotWordLexicon.py --hotwordRawList ./TestData_Clean/hotwordRawList.txt --opLexicon ./TestData_Op/opLexicon.txt --opLexicon_withHWStr  ./TestData_Op/opLexicon_withHWStr.txt

ex:
    hotwordRawList      = './TestData_Clean/hotwordRawList.txt'
    opLexicon           = './TestData_Op/hotword_Lexicon.txt'
    opLexicon_withHWStr = './TestData_Op/hotwordRaw_Lexicon_withHWStr.txt'

"""
#
import logging
import os, sys, io
import argparse
from   libWord import C_WordList

logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
log = logging.getLogger("{}".format(os.path.basename(sys.argv[0])))


parse = argparse.ArgumentParser()
parse.add_argument('--hotwordRawList', required=True,  help="hotword raw list file ")
parse.add_argument('--opLexicon',      required=True,  help="lexicon filename")
parse.add_argument('--opLexicon_withHWStr', required=True,  help="lexicon with Hotwordstr filename")
args = parse.parse_args()
 

listHotWord = C_WordList()
listHotWord.read_WordList( args.hotwordRawList, True)   # second parameter tells system that its hotword reading
listHotWord.write_WordLexicon(args.opLexicon)
listHotWord.write_WordLexicon_withWordStr(args.opLexicon_withHWStr)
 
 