#!/usr/bin/env python3
"""
Filename: libHotWord.py (to be imported as a module)
Author: Chng Eng Siong
Date: 6 Aug 2021
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


# This class maintains information for a single hotword!
# hotWordStr == the actual string representing the hotword, hence Orchard Road (case is important!)
# hotWord Label converts the hotword string into label, e.g __Orchard_Road
# hotWordArrayPron keeps a list of pronunciation associated with the hotword (all lowered case to match phoneme)
@dataclass
class C_OneHotWord:
    hotWordStr: str     # this is the original hotword, case is important! 
    hotWordLabel: str   # this is __hotword_name_in_lower_case
    hotWordArrayPron: [] # This is the list of pronunciation ALL in lower case when expanded

    # initialise a howtowrd by its hotwordstring
    # to the label and first pronunciation!
    def __init__(self, in_hotWordStr):
        hotWordStr        = in_hotWordStr.rstrip()
        self.hotWordStr   = hotWordStr
        self.hotWordLabel = '__'+hotWordStr.replace(' ','_')  # the label is with __hotword_string
        self.hotWordArrayPron = [hotWordStr.lower()]          # all pronunciation is lowered case
 
    # we can add more pronunciation
    def addPron(self,in_pronStr):
        tmp     = re.sub('[\s+]', '', in_pronStr)
        #sanity check, lets deal with empty pronStr!
        if(len(tmp)>=1):
            pron_Str = in_pronStr.lower().strip(' \t\n')
            self.hotWordArrayPron.append(pron_Str)
  

    # This function generates the lexicon entry given pronStr
    # We are now ONLY assuming for english lexicon 
    def getPronEntry(self,ipStr):
        if len(ipStr) <= 0:
            return ""

        opStr = ""
        ipStr = ipStr.replace(' ','')    # spaces in the pronunciation is ignored , no word boundary!
        opStr = ipStr[0]+'_WB_eng'       #_WB == word boundary, only happens in start, end of word
        for i in range(1,len(ipStr)-1):
            opStr = opStr+' '+ipStr[i]+'_eng'

        if (len(ipStr)>=2):
            opStr = opStr+' '+ipStr[len(ipStr)-1]+'_WB_eng'    # we have to take care last character of word

        return(opStr)    



    # saving the single word as lexicon entry
    # we save 2 fields, field1  == label (__Orchard_Road)
    # the second field , field2 == pronunciation string for kaldi in grapheme format
    def writeOneWordLexicon(self,opfile):
        for pronStr in self.hotWordArrayPron:
            lexEntry = self.getPronEntry(pronStr)
            opfile.write("{0} {1}\n".format(self.hotWordLabel, lexEntry))
            # IMPORTANT *** SHOULD WE WRITE @1, @2 for multuiple pronunciation?


    # saving the single word as lexicon entry with 3 fields!
    # we save 3 fields,  field1  == label (__Orchard_Road)
    # the second field , field2  == the hotword string (case sensitive) 
    # the third  field,  field3 == list of pronunciation string for kaldi in grapheme format
    def writeOneWordLexicon_withHotWordStr(self,opfile):
        opfile.write("{0}:{1}:{2}".format(self.hotWordLabel, self.hotWordStr, self.hotWordArrayPron[0]))
        for i in range(1,len(self.hotWordArrayPron)):
            opfile.write(",{0}".format(self.hotWordArrayPron[i]))
        opfile.write("\n")    
 


#
# This class deals with an array of hotword
# we also keep dictionary to map from _label to hotword and vice versa
# we also keep a lot of redundancies to save from searching

@dataclass
class C_HotWordList:
    fileName: str
    listReadStr: []
    listHotWordStr: []
    dictLabelToHWStr: dict
    dictHWStrToLabel: dict
    dictHWStrToHotWord: dict

    def __init__(self):
        self.fileName = ''
        self.listReadStr    = []
        self.listHotWordStr = []
        self.dictLabelToHWStr = {}
        self.dictHWStrToLabel = {}
        self.dictHWStrToHotWord = {}


    # function supporting reading the rawHotWordList.txt files
    # parsing a line containg 2 fields (hotwordstring: hotwordpronunciation str (if exist))
    # eg   
    # e.g,  Vu Ly Thy:vu lee tea
    #       Vu Ly Thy:voo ly tee
    # field 1== Hotword string
    # field 2== pronunciation of the hotword
    def fn_textParseLine(self,line):
        tokenArray=line.split(':')
        hotWordStr = tokenArray[0].replace('\t',' ').strip('\n');
        if hotWordStr in self.dictHWStrToLabel.keys():            
            currHotWord = self.dictHWStrToHotWord[hotWordStr]
            if (len(tokenArray) >= 2):
                currHotWord.addPron(tokenArray[1])
                # we are wary that there may be no pronString in second token! :)
                # 
        else:
            oneHotWord = C_OneHotWord(hotWordStr)
            self.dictHWStrToHotWord[hotWordStr] = oneHotWord
            self.dictHWStrToLabel[hotWordStr] = oneHotWord.hotWordLabel  
            self.dictLabelToHWStr[oneHotWord.hotWordLabel] = hotWordStr
            self.listHotWordStr.append(hotWordStr)
            # we keep the above information to ease tracking of the new hotword string
        return 0

    def add_HotWordList(self, setHotWord):
        for tokStr in setHotWord:
            self.listReadStr.append(tokStr)    
            self.fn_textParseLine(tokStr)


    # actual function reading the rawHotWordList.txt files
    def read_HotWordList(self,infilename):
        self.fileName = infilename
        infile = open(infilename,'r')
        for line in infile:
            line = line.strip()            
            self.listReadStr.append(line)
            self.fn_textParseLine(line)

        print('completed reading:',infilename,' has ',len(self.dictHWStrToLabel),' unique hotwords\n')    


    def verifyIsHOTWORD(self,testStr):
        if testStr in self.dictHWStrToLabel.keys(): 
            return 1
        else:
            return 0                   

    # saving the hotword lexicon, ONLY 2 fields,
    # writeOneWordLexicon writes (__Orchard_Road __o_WB_eng r_eng ... a_eng d_WB_eng)
    # the second field , field2 == pronunciation string for kaldi in grapheme format
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
    #field 3 == all pronunciation, separated by comma
    def write_HotWordLexicon_withHotWordStr(self,opfilename):
        opfile = open(opfilename,'w')
        print('Saving lexicon of hotword')
        for oneHotWordStr in self.listHotWordStr:
            oneHotWord = self.dictHWStrToHotWord[oneHotWordStr]
            oneHotWord.writeOneWordLexicon_withHotWordStr(opfile)
        opfile.close()
        print('completed saving:',opfilename,' has ',len(self.dictHWStrToLabel),' unique hotwords\n')    




    # This function takes an inStr and convert those string that are hotwords to labels
    # e.g, if "Orchard Road" is a hotword in dictionary, then __Orchard_Road is returned
    # here the case == True is used, => we ignore case
    def convertStrToHotWordLabel(self,inStr):
        return(multireplace(inStr, self.dictHWStrToLabel, True))

    # This function takes an inStr and remove all words except Hotword Labels
    #
    def convertStrToHotWordLabel_ONLY(self,inStr):
        # sanity check, lets convert hotwords into hotwords label first
        tmpStr = multireplace(inStr, self.dictHWStrToLabel, True)
        opToken = tmpStr.split()  # lets retain only those that have __
        opStr = ''   # stores the tokens retained, MUST only be those that have __ in front
        for tok in opToken:
            if tok[0:2] == '__':        # be careful, we MUST remember all hotwords start with '__'
                opStr = opStr+ ' '+tok
        return(opStr.strip())       # because the first token added the space, this is a hack! 

    def convertLabelToWord(self,inStr):
        return( multireplace(inStr, self.dictLabelToHWStr, True))
    # We should change this to False (case is important in future
    # IMPORTANT: this is to ignore case when we find, BUT actually we should?


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

    inRawKeyWord_FileName = './TestData_Clean/hotwordRawList.txt'
    opLexicon_FileName    = './TestDataOp/op_Lexicon.txt'
    opLexicon_withHWStr_FileName = './TestDataOp/Op_Lexicon_withStr.txt'
    unit_test_Keyword(inRawKeyWord_FileName, opLexicon_FileName, opLexicon_withHWStr_FileName)


#    oneHotWord = C_OneHotWord("Jalan Bahar")
#    oneHotWord = C_OneHotWord("Vu Ly Thy:")
#    oneHotWord = C_OneHotWord("Vu Ly Thy:voo lee tea")


    
if __name__ == "__main__":
    unit_test_libHotWord()
