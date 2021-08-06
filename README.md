# Kaldi_CombineCTM
 combining Master and Hotword Decoder CTM files

### Author: Chng Eng Siong
### Date: 31st July 2021

Objective: 

The code in the  folder allows you to 

    1) generate the hotword decoder lexicon from the hotwordlist
    2) experimental output to combine hotword and master decoder ctm file.
    3) generate different types of sentence level ctm files (with no time information)
        for WER scoring for (wordOnly->typical), (word_hotword), and (hotwordONLY)
        types of transformed output
            a) wordOnly
            b) word_hotword
            c) hotwordOnly


1) generate the hotword decoder lexicon from the hotwordlist:
# The following command generates the hotword lexicon from hotwordlist
python3 run_createHotWordLexicon.py --hotwordRawList ./TestData_Clean/hotwordRawList.txt --opLexicon ./TestDataOp/opLexicon.txt --opLexicon_withHWStr  ./TestData_Op/opLexicon_withHWStr.txt
ex:
    hotwordRawList      = './TestData_Clean/hotwordRawList.txt' -> a list of hotwords
    opLexicon           = './TestData_Op/hotword_Lexicon.txt'   -> ready for ASR use
    opLexicon_withHWStr = './TestData_Op/hotwordRaw_Lexicon_withHWStr.txt'  -> this is for debugging purposes,
                you can see the multiple pronunciation here, example below:
                    field 1 == label (case sensitive!)
                    field 2 == original hotword string found in hotwordRawList.txt (case sensitive!)
                    field 3 == pronunciation string separated by comma ','. since phones id, ONLY lower case allowed.

                __Vu_Ly_Tee:Vu Ly Tee:vu ly tee,vu lee tea,voo lee tea
                __Abraham_Solomon:Abraham Solomon:abraham solomon_



2) experimental output to combine hotword and master decoder ctm file.
# The following command generates the dual ctm file from master and hotword ctm
python3 run_combineCTM.py --master_ctm ./TestData_Clean/master.ctm --hotword_ctm ./TestData_Clean/hotword.ctm --collar_rate 0.25 --dual_ctm ./TestDataOp/dual_WordwithHotWord.ctm



3) To score WER, We wish to generate the raw text file from the ctm file
# we will convert INTO 3 formats, filename_WordONLY.txt, filename_WordAndHotWordLabel.txt,  and  filename_HOTWordONLY.txt
python3 run_convertCTM_toWERscoringText.py  --hotwordRawList ./TestData_Clean/hotwordRawList.txt --ctm ./TestDataOp/yourCTMfile.ctm  --opfile ./TestDataOp/yourfilename_
    -> it takes in the hotword list so it knows HOW to convert to __hotword_label, to break into hotword label and to combine
        hotword label -> __hotword_label

    -> it will generate 3 types of outputfiles:
        a) yourfilename_HotwordOnly.txt
        b) yourfilename_WordAndHotWordLabel.txt
        b) yourfilename_WordONLY.txt


        




