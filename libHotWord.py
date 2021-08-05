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
    hotWordStr: str     # this is the original hotword, case is important! 
    hotWordLabel: str   # this is __hotword_name_in_lower_case
    hotWordArrayPron: [] # This is the list of pronunciation ALL in lower case when expanded
    def __init__(self, in_hotWordStr):
        hotWordStr        = in_hotWordStr.rstrip()
        self.hotWordStr   = hotWordStr
        self.hotWordLabel = '__'+hotWordStr.replace(' ','_')  # the label is with __hotword_string
        self.hotWordArrayPron = [hotWordStr.lower()]          # all pronunciation is lowered case
 
    def addPron(self,in_pronStr):
        tmp     = re.sub('[\s+]', '', in_pronStr)
        #sanity check, lets deal with empty pronStr!
        if(len(tmp)>=1):
            pron_Str = in_pronStr.lower().strip(' \t\n')
            self.hotWordArrayPron.append(pron_Str)
  

    # We are now ONLY assuming for english lexicon 
    # for grapheme based
    def getPronEntry(self,ipStr):
        opStr = ""
        if len(ipStr) <= 0:
            return opStr

        ipStr = ipStr.replace(' ','')    
        opStr = ipStr[0]+'_WB_eng'
        for i in range(1,len(ipStr)-1):
            opStr = opStr+' '+ipStr[i]+'_eng'

        if (len(ipStr)>=2):
            opStr = opStr+' '+ipStr[len(ipStr)-1]+'_WB_eng'    

        return(opStr)    

    def writeOneWordLexicon(self,opfile):
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
            oneHotWord = self.dictHWStrToHotWord[oneHotWordStr]
            oneHotWord.writeOneWordLexicon_withHotWordStr(opfile)
        opfile.close()
        print('completed saving:',opfilename,' has ',len(self.dictHWStrToLabel),' unique hotwords\n')    


    # This function takes an inStr and convert those string that are hotwords to labels
    def convertStrToHotWordLabel(self,inStr):
        return(multireplace(inStr, self.dictHWStrToLabel, False))

    def convertStrToHotWordLabel_ONLY(self,inStr):
        tmpStr = multireplace(inStr, self.dictHWStrToLabel, False)
        opToken = tmpStr.split()  # lets retain only those that have __
        opStr = ''
        for tok in opToken:
            if tok[0:2] == '__':
                opStr = opStr+ ' '+tok
        return(opStr)        


    def convertLabelToWord(self,inStr):
        return( multireplace(inStr, self.dictLabelToHWStr, False))


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



def unit_test_Keyword(inRawKeyWord_FileName,opLexicon_FileName, opLexicon_withHWStr_FileName):
    listHotWord = C_HotWordList()
    listHotWord.read_HotWordList( inRawKeyWord_FileName)
    listHotWord.write_HotWordLexicon(opLexicon_FileName)
    listHotWord.write_HotWordLexicon_withHotWordStr(opLexicon_withHWStr_FileName)
 
 
    print('\n============P1==============')
    rawStr = "Jalan Gemala is near Hubert Hill and Singapore Art Museum"
 
    print('Using the hotword class to convert from raw, words_with_label, label_only')
    print('rawStr =', rawStr)
    strWithLabel = listHotWord.convertStrToHotWordLabel(rawStr)
    print('P1 (strWithLabel) :',strWithLabel)
    print('P2 (labelToWord)  :', listHotWord.convertLabelToWord(strWithLabel))
    labelOnly = listHotWord.convertStrToHotWordLabel_ONLY(rawStr)
    print('P3 (label ONLY)        :', labelOnly)
    print('P4 (label ONLY to word):', listHotWord.convertLabelToWord(labelOnly))
    print('\n============P2==============')




def unit_test_libHotWord():

    inRawKeyWord_FileName = './TestData/FULL_KeyWordRawList.txt'
    opLexicon_FileName    = './TestData/Small_KeyWordRawList_Lexicon.txt'
    opLexicon_withHWStr_FileName = './TestData/Small_KeyWordRawList_withHWStr_Lexicon.txt'
    unit_test_Keyword(inRawKeyWord_FileName, opLexicon_FileName, opLexicon_withHWStr_FileName)


#    oneHotWord = C_OneHotWord("Jalan Bahar")
#    oneHotWord = C_OneHotWord("Vu Ly Thy:")
#    oneHotWord = C_OneHotWord("Vu Ly Thy:voo lee tea")


    
if __name__ == "__main__":
    unit_test_libHotWord()
