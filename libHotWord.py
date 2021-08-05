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

"""
example, 3 iplines describing the hotword "Vy Ly Thy" and has 2 alternate pronunciation 
Jalan Bahar     (note no : => default grapheme based dictionary)
Vu Ly Thy:      (this colon is useless since right field is missing)
Vu Ly Thy: voo lee tea
Vu Ly Thy: voo lai tea
"""

@dataclass
class C_OneHotWord:
    hotWordLabel: str
    hotWordStr: str      
    hotWordArrayPron: []
    def __init__(self, hotWordStr):
        hotWordStr = hotWordStr.rstrip().lower()
        tmpStr = '__'+hotWordStr.replace(' ','_')
        self.hotWordLabel = tmpStr
        self.hotWordStr = hotWordStr
        self.hotWordArrayPron = [hotWordStr.lower()]

    def addPron(self,in_pronStr):
        pronStr = in_pronStr.lower().strip(' \t\n')
        tmp     = pronStr
        tmp=tmp.replace(' ','')
        if (len(tmp)>0):
            tokenArray=tmp.split('_')
            if ( len(tokenArray) > 0):
                self.hotWordArrayPron.append(pronStr)
        else:
            pass


    def getPronEntry(self,ipStr):
        opStr = ""
        if len(ipStr) <= 0:
            return opStr

        ipStr = ipStr.replace(' ','')    
        opStr = ipStr[0]+'_WB'
        for i in range(1,len(ipStr)):
            opStr = opStr+' '+ipStr[i]

        if (len(ipStr)>1):
            opStr = opStr+'_WB'    

        return(opStr)    

    def writeOneWordLexicon(self,opfile):
        print('p0, hotWordLabl=',self.hotWordLabel)
        for pronStr in self.hotWordArrayPron:
            lexEntry = self.getPronEntry(pronStr)
            opfile.write("{0} {1}\n".format(self.hotWordLabel, lexEntry))

    def writeOneWordLexicon_withHotWordStr(self,opfile):
        opfile.write("{0}:{1}:{2}".format(self.hotWordLabel, self.hotWordStr, self.hotWordArrayPron[0]))
        for i in range(1,len(self.hotWordArrayPron)):
            opfile.write(",{0}".format(self.hotWordArrayPron[i]))
        opfile.write("\n")    
 

@dataclass
class C_HotWordList:
    fileName: str
    listReadStr: []
    listHotWordStr: []
    dictLabelToHWStr: dict
    dictHWStrToLabel: dict
    dictHWStrToHotWord: List[C_OneHotWord]  # of CHotWord


    def __init__(self):
        self.fileName = ''
        self.listReadStr    = []
        self.listHotWordStr = []
        self.dictLabelToHWStr = {}
        self.dictHWStrToLabel = {}
        self.dictHWStrToHotWord = {}


    # reading a file containg 2 fields
    # field 1== HWStr
    # field 2== Label of the hotword
    def fn_textParseLine(self,line):
        tokenArray=line.split(':')
        hotWordStr = tokenArray[0].replace('\t',' ').strip('\n');
        if hotWordStr in self.dictHWStrToLabel.keys():            
            currHotWord = self.dictHWStrToHotWord[hotWordStr]
            if (len(tokenArray) >= 2):
                currHotWord.addPron(tokenArray[1])
        else:
            oneHotWord = C_OneHotWord(hotWordStr)
            self.dictHWStrToHotWord[hotWordStr] = oneHotWord
            self.dictHWStrToLabel[hotWordStr] = oneHotWord.hotWordLabel  
            self.dictLabelToHWStr[oneHotWord.hotWordLabel] = hotWordStr

            self.listHotWordStr.append(hotWordStr)
        return 0


    def read_HotWordList(self,infilename):
        self.fileName = infilename
        infile = open(infilename,'r')
        for line in infile:
            line = line.strip()            
            self.listReadStr.append(line)
            self.fn_textParseLine(line)

        print('completed reading:',infilename,' has ',len(self.dictHWStrToLabel),' unique hotwords\n')    


    # we will now create the hotword lexicon
    def write_HotWordLexicon(self,opfilename):
        opfile = open(opfilename,'w')
        print('Saving lexicon of hotword')
        for oneHotWordStr in self.listHotWordStr:
            oneHotWord = self.dictHWStrToHotWord[oneHotWordStr]
            oneHotWord.writeOneWordLexicon(opfile)
        opfile.close()
        print('completed saving:',opfilename,' has ',len(self.dictHWStrToLabel),' unique hotwords\n')    

    # we will now create the hotword lexicon, where field 1 == label
    # field 2 == original hotword string
    #field 3 == all pronunciation, separated by =
    def write_HotWordLexicon_withHotWordStr(self,opfilename):
        opfile = open(opfilename,'w')
        print('Saving lexicon of hotword')
        for oneHotWordStr in self.listHotWordStr:
            print('writing ',oneHotWordStr)
            oneHotWord = self.dictHWStrToHotWord[oneHotWordStr]
            oneHotWord.writeOneWordLexicon_withHotWordStr(opfile)
        opfile.close()
        print('completed saving:',opfilename,' has ',len(self.dictHWStrToLabel),' unique hotwords\n')    



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
    listHotWord = C_HotWordList()
    listHotWord.read_HotWordList(    './TestData/UserKeywordList.txt')
    listHotWord.write_HotWordLexicon('./TestData/UserKeywordListLexicon.txt')
    listHotWord.write_HotWordLexicon_withHotWordStr('./TestData/UserKeywordListLexicon_withHotWordStr.txt')
    myDict_LabelToStr = listHotWord.dictLabelToHWStr
    myDict_StrToLabel = listHotWord.dictHWStrToLabel

    print('\n============P0==============')
    print(myDict_LabelToStr['__hubert_hill'])
    print(myDict_StrToLabel['Hubert Hill'])

    print('\n============P1==============')
    rawStr = "Jalan Gemala is near Hubert Hill and Singapore Art Museum"
    hotStr = multireplace(rawStr, myDict_StrToLabel, False)
    print(rawStr)
    print(hotStr)
    print('\n============P2==============')
    rawStr2 = multireplace(hotStr, myDict_LabelToStr, False)
    print('RawStr2 = ',rawStr2)
    print('sanity check {}'.format(rawStr == rawStr2))






def unit_test_HotWordList():
    listHotWord = C_HotWordList()
    listHotWord.read_HotWordList(    './TestData/UserKeywordList.txt')
    myDict_LabelToStr = listHotWord.dictLabelToHWStr
    myDict_StrToLabel = listHotWord.dictHWStrToLabel

    print('\n============P0==============')
    print(myDict_LabelToStr['__hubert_hill'])
    print(myDict_StrToLabel['Hubert Hill'])

    print('\n============P1==============')
    rawStr = "Jalan Gemala is near Hubert Hill and Singapore Art Museum"
    hotStr = multireplace(rawStr, myDict_StrToLabel, False)
    print(rawStr)
    print(hotStr)
    print('\n============P2==============')
    rawStr2 = multireplace(hotStr, myDict_LabelToStr, False)
    print('RawStr2 = ',rawStr2)
    print('sanity check {}'.format(rawStr == rawStr2))


def main():

    listHotWord = C_HotWordList()
    listHotWord.read_HotWordList(    './TestData/UserKeywordList.txt')
    listHotWord.write_HotWordLexicon('./TestData/UserKeywordListLexicon.txt')
    listHotWord.write_HotWordLexicon_withHotWordStr('./TestData/UserKeywordListLexicon_withHotWordStr.txt')
    unit_test_Keyword()
    unit_test_HotWordList()


#    oneHotWord = C_OneHotWord("Jalan Bahar")
#    oneHotWord = C_OneHotWord("Vu Ly Thy:")
#    oneHotWord = C_OneHotWord("Vu Ly Thy:voo lee tea")


    
if __name__ == "__main__":
    main()
