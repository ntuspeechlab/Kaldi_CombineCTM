#!/usr/bin/env python3
"""
Filename: run_test_libCTM.py (to be imported as a module)
Author: Chng Eng Siong
Date: 31 July 2021
Last edited: 1st Aug 2021 (CES), 11:07pm
Objective: combing CTM files of Master and HotWordDecoder to form DualASR CTM File
"""
#
from   libHotWord import C_HotWord   # eng siong's library 
import libHotWord

dictName = "./TestData/LookupKeywordList.txt"
myHotWord = C_HotWord()
(myDict_KeyToPron, myDict_PronToKey) = myHotWord.read_HotWordDictionary(dictName)
print(myDict_KeyToPron['__hubert_hill'])
print(myDict_PronToKey['Hubert Hill'])

rawStr = "Jalan Gemala is near Hubert Hill and Singapore Art Museum"
hotStr = libHotWord.multireplace(rawStr, myDict_PronToKey, False)
print(rawStr)
print(hotStr)
rawStr2 = libHotWord.multireplace(hotStr, myDict_KeyToPron, False)
print('RawStr2 = ',rawStr2)
print('sanity check {}'.format(rawStr == rawStr2))
