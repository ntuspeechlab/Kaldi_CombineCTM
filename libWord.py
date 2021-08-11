#!/usr/bin/env python3
"""
Filename: libWord.py (to be imported as a module)
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


# This class maintains information for 
# a single word as well as hotword!
# if its hotWordFlag==True then
#    hotWordStr == the actual string representing the hotword, hence Orchard Road (case is important!)
#    hotWord Label converts the hotword string into label, e.g __Orchard_Road
#    hotWordArrayPron keeps a list of pronunciation associated with the hotword (all lowered case to match phoneme)
# if hotWordFlag == False then
# the ONLY difference is when writing the __ as label!

@dataclass
class C_OneWord:
    hotWordFlag: int  # 1 is True, 0 is False
    wordStr: str      # this is the hotword, case is important! 
    wordLabel: str    # If its hotword then  __hotword_name_in_lower_case, else no __ in first two character
    wordArrayPron: [] # This is the list of pronunciation ALL in lower case when expanded

    # initialise a howtowrd by its hotwordstring
    # to the label and first pronunciation!
    def __init__(self, inWordStr, hotWordFlag):   # MUST set hotword FLag for each word
        self.hotWordFlag  = hotWordFlag
        wordStr           = inWordStr.rstrip()
        self.wordStr      = wordStr
        if hotWordFlag == True:
            self.wordLabel = '__'+wordStr.replace(' ','_')  # the label is with __word_string
        else:
            self.wordLabel    = wordStr.replace(' ','_')  # the label is with word_string
            # THE only difference is NO __ in front

        self.wordArrayPron = [wordStr.lower()]          # all pronunciation is lowered case
 
    # we can add more pronunciation
    def addPron(self,inPronStr):
        tmp     = re.sub('[\s+]', '', inPronStr)
        #sanity check, lets deal with empty pronStr!
        if(len(tmp)>=1):
            pronStr = inPronStr.lower().strip(' \t\n')
            self.wordArrayPron.append(pronStr)
  

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
        countPron = 0
        for pronStr in self.wordArrayPron:
            lexEntry = self.getPronEntry(pronStr)
            if countPron == 0:
                opfile.write("{0} {1}\n".format(self.wordLabel, lexEntry))
            else:
                opfile.write("{0}#{2} {1}\n".format(self.wordLabel, lexEntry, countPron))
                    
            countPron=countPron+1

            # IMPORTANT *** SHOULD WE WRITE #1, #2 for multiple pronunciation???


    # saving the single word as lexicon entry with 3 fields!
    # we save 3 fields,  field1  == label (__Orchard_Road)
    # the second field , field2  == the hotword string (case sensitive) 
    # the third  field,  field3 == list of pronunciation string for kaldi in grapheme format
    def writeOneWordLexicon_withWordStr(self,opfile):
        opfile.write("{0}:{1}:{2}".format(self.wordLabel, self.wordStr, self.wordArrayPron[0]))
        for i in range(1,len(self.wordArrayPron)):
            opfile.write(",{0}".format(self.wordArrayPron[i]))
        opfile.write("\n")    
 


#
# This class deals with an array of word
# we also keep dictionary to map from _label to word/hotword and vice versa
# we also keep a lot of redundancies to save from searching

@dataclass
class C_WordList:
    fileName: str
    listReadStr: []
    listWordStr: []
    dictLabelToWStr: dict
    dictWStrToLabel: dict
    dict_HotWordStrToLabel: dict
    dict_HotWordLabelToWordStr: dict
    dictWStrToCWord: dict

    def __init__(self):
        self.fileName = ''
        self.listReadStr     = []
        self.listWordStr     = []
        self.dictLabelToWStr = {}
        self.dictWStrToLabel = {}
        self.dict_HotWordStrToLabel = {}
        self.dict_HotWordLabelToWordStr = {}
        self.dictWStrToCWord  = {}



    # function supporting reading the rawWordList.txt
    # as well as normal list of words file files
    # parsing a line containg 2 fields (wordstring: wordpronunciation str (if exist))
    # eg   
    # e.g,  Vu Ly Thy:vu lee tea
    #       Vu Ly Thy:voo ly tee
    # field 1== word string  
    # field 2== alternate pronunciation of the word
    def fn_textParseLine(self,line, hotWordFlag):
        tokenArray=line.split(':')
        wordStr = tokenArray[0].replace('\t',' ').strip('\n');
        if wordStr in self.dictWStrToLabel.keys():            
            currWord = self.dictWStrToCWord[wordStr]
            if (len(tokenArray) >= 2):
                currWord.addPron(tokenArray[1])
                # we are wary that there may be no pronString in second token! :)
                # 
        else:
            oneWord = C_OneWord(wordStr,hotWordFlag)  # second paramam == hotword Flag
            self.dictWStrToCWord[wordStr] = oneWord
            self.dictWStrToLabel[wordStr]= oneWord.wordLabel  
            self.dictLabelToWStr[oneWord.wordLabel] = wordStr
            self.listWordStr.append(wordStr)
            if (hotWordFlag == True):
                self.dict_HotWordStrToLabel[wordStr]= oneWord.wordLabel  
                self.dict_HotWordLabelToWordStr[oneWord.wordLabel] = wordStr


            # we keep the above information to ease tracking of the new hotword string
        return 0

    def add_WordList(self, setWord, hotWordFlag):
        for tokStr in setWord:
            self.listReadStr.append(tokStr)    
            self.fn_textParseLine(tokStr, hotWordFlag)



    # actual function reading the rawHotWordList.txt files
    # The caller MUST initialise hotWordFlag properly!!!
    def read_WordList(self,infilename, hotWordFlag):
        self.fileName = infilename
        infile = open(infilename,'r')
        for line in infile:
            line = line.strip()            
            self.listReadStr.append(line)
            self.fn_textParseLine(line,hotWordFlag)

        if (hotWordFlag == True):
            print('completed reading (HOTWORD):',infilename,' has ',len(self.dictWStrToLabel),' unique words\n')    
        else:
            print('completed reading (NORMAL WORD):',infilename,' has ',len(self.dictWStrToLabel),' unique words\n')    
                



    def verifyIsHOTWORD(self,testStr):
        if testStr in self.dict_HotWordStrToLabel.keys(): 
            return 1
        else:
            return 0                   

    # saving the hotword lexicon, ONLY 2 fields,
    # writeOneWordLexicon writes (__Orchard_Road __o_WB_eng r_eng ... a_eng d_WB_eng)
    # the second field , field2 == pronunciation string for kaldi in grapheme format
    def write_WordLexicon(self,opfilename):
        opfile = open(opfilename,'w')
        print('Saving lexicon of hotword')
        for oneWordStr in self.listWordStr:
            oneWord = self.dictWStrToCWord[oneWordStr]
            oneWord.writeOneWordLexicon(opfile)
        opfile.close()
        print('completed saving:',opfilename,' has ',len(self.dictWStrToLabel),' unique hotwords\n')    


    # we will now create the hotword lexicon, where field 1 == label
    # field 2 == original hotword string
    #field 3 == all pronunciation, separated by comma
    def write_WordLexicon_withWordStr(self,opfilename):
        opfile = open(opfilename,'w')
        print('Saving lexicon of word')
        for oneWordStr in self.listWordStr:
            oneWord = self.dictWStrToCWord[oneWordStr]
            oneWord.writeOneWordLexicon_withWordStr(opfile)
        opfile.close()
        print('completed saving:',opfilename,' has ',len(self.dictWStrToLabel),' unique hotwords\n')    



    # This is a hack, we will make __Tanjong_Pagar#1 to become __Tanjong_Pagar
    # inStr is a string with many tokens
    def removeLabel_multiPronDisambiguation(self,inStr):
        return(re.sub('[#][0-9]','',inStr))
        

    def convertLabelToWord(self,inStr):
        tmpStr0= self.removeLabel_multiPronDisambiguation(inStr)
        tmpStr1  = multireplace(tmpStr0, self.dict_HotWordStrToLabel, True)
        # This is a sanity check to convert everything to label first
        # this allow us to keep the case
        return( multireplace(tmpStr1, self.dictLabelToWStr, True))
    # We should change this to False (case is important in future
    # IMPORTANT: this is to ignore case when we find, BUT actually we should?


    # This function takes an inStr and convert those string that are hotwords to labels
    # e.g, if "Orchard Road" is a hotword in dictionary, then __Orchard_Road is returned
    # here the case == True is used, => we ignore case
    def convertStrToHotWordLabel(self,inStr):
        tmpStr0= self.removeLabel_multiPronDisambiguation(inStr)
        return(multireplace(tmpStr0, self.dict_HotWordStrToLabel, True))

    # This function takes an inStr and remove all words except Hotword Labels
    #
    def convertStrToHotWordLabel_ONLY(self,inStr):
        tmpStr0= self.removeLabel_multiPronDisambiguation(inStr)
        # sanity check, lets convert hotwords into hotwords label first
        tmpStr1 = multireplace(tmpStr0, self.dict_HotWordLabelToWordStr, True)
        # This is to convert labels to string first!! :) its sanity check!
        tmpStr2  = multireplace(tmpStr1, self.dict_HotWordStrToLabel, True)
        opToken = tmpStr2.split()  # lets retain only those that have __
        opStr = ''   # stores the tokens retained, MUST only be those that have __ in front
        for tok in opToken:
            if tok[0:2] == '__':        # be careful, we MUST remember all hotwords start with '__'
                opStr = opStr+ ' '+tok
        return(opStr.strip())       # because the first token added the space, this is a hack! 

    def convertHotWordLabelToWordStr(self,inStr):
        tmpStr0= self.removeLabel_multiPronDisambiguation(inStr)
        tmpStr1  = multireplace(tmpStr0, self.dict_HotWordStrToLabel, True)
        # This is a sanity check to convert everything to label first
        # this allow us to keep the case
        return( multireplace(tmpStr1, self.dict_HotWordLabelToWordStr, True))

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



def unit_test_Keyword(inRawWord_FileName,opLexicon_FileName, opLexicon_withWStr_FileName):
    listWord = C_WordList()
    listHotWord.read_WordList( inRawWord_FileName, True)  # Keyword
    listHotWord.write_WordLexicon(opLexicon_FileName)
    listHotWord.write_WordLexicon_withWordStr(opLexicon_withWStr_FileName)
 
 
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
