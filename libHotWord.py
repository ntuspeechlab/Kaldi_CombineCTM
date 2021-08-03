#!/usr/bin/env python3
"""
Filename: libHotWord.py (to be imported as a module)
Author: Chng Eng Siong
Date: 3 Aug 2021
Last edited: 3rd Aug 2021 (CES), 11:07pm
Objective: Libraries supporting hotword
"""
#
import re
import logging
import os, sys, io
from   dataclasses import dataclass
from   typing import List


logging.basicConfig(
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)
log = logging.getLogger("{}".format(os.path.basename(sys.argv[0])))

# This simple class contains the HotKeyWord
# It reads a file and put the information into 2 dictionary
# one is key->pronunciation, and the other pronunciation->key
@dataclass
class C_HotWord:
    hotword_KeyToPron: dict
    hotword_PronToKey: dict
    fileName: str
    def __init__(self):
        hotword_KeyToPron = {}
        hotword_PronToKey = {}
        fileName = ''


    def read_HotWordDictionary(self,infilename):
        self.hotword_KeyToPron = {}
        self.hotword_PronToKey = {}
        self.fileName = infilename
        infile = open(infilename)
        for line in infile:
            (key, pron) = line.split(':')  # we assume that the dictionary is separated by :
            self.hotword_KeyToPron[key] = pron.strip()
            self.hotword_PronToKey[pron.strip()] = key

        return(self.hotword_KeyToPron, self.hotword_PronToKey)


"""
test_string = "original text is here"
replacements = {
"text" : "fake",
"original": "text",
"Is hEre": "was there"
}
opString =  multireplace(test_string, replacements, ignore_case=False)
print(test_string)
print(opString)
"""
#This code is from https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729
def multireplace(string, replacements, ignore_case=False):
    """
    Given a string and a replacement map, it returns the replaced string.
    :param str string: string to execute replacements on
    :param dict replacements: replacement dictionary {value to find: value to replace}
    :param bool ignore_case: whether the match should be case insensitive
    :rtype: str
    """
    if not replacements:
        # Edge case that'd produce a funny regex and cause a KeyError
        return string
    
    # If case insensitive, we need to normalize the old string so that later a replacement
    # can be found. For instance with {"HEY": "lol"} we should match and find a replacement for "hey",
    # "HEY", "hEy", etc.
    if ignore_case:
        def normalize_old(s):
            return s.lower()

        re_mode = re.IGNORECASE

    else:
        def normalize_old(s):
            return s

        re_mode = 0

    replacements = {normalize_old(key): val for key, val in replacements.items()}
    
    # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
    # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
    # 'hey ABC' and not 'hey ABc'
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = map(re.escape, rep_sorted)
    
    # Create a big OR regex that matches any of the substrings to replace
    pattern = re.compile("|".join(rep_escaped), re_mode)
    
    # For each match, look up the new string in the replacements, being the key the normalized old string
    return pattern.sub(lambda match: replacements[normalize_old(match.group(0))], string)



def unit_test_Keyword():
    dictName = "./TestData/LookupKeywordList.txt"
    myHotWord = C_HotWord()
    (myDict_KeyToPron, myDict_PronToKey) = myHotWord.read_HotWordDictionary(dictName)
    print(myDict_KeyToPron['__hubert_hill'])
    print(myDict_PronToKey['Hubert Hill'])

    rawStr = "Jalan Gemala is near Hubert Hill and Singapore Art Museum"
    hotStr = multireplace(rawStr, myDict_PronToKey, False)
    print(rawStr)
    print(hotStr)
    rawStr2 = multireplace(hotStr, myDict_KeyToPron, False)
    print('RawStr2 = ',rawStr2)
    print('sanity check {}'.format(rawStr == rawStr2))
