#!/bin/bash

# Source this file, and then check ./TestDataOp
# The output should be self-explanatory
#
# Step 1: creating the lexicon for hotword decoder from rawList of hotword!
#
hotwordlist=./TestData_Clean/hotwordRawList.txt 
opLexicon=./TestDataOp/opLexicon.txt
opLexiconWithHWR=./TestDataOp/opLexicon_withHWStr.txt

python3 run_createHotWordLexicon.py --hotwordRawList $hotwordlist \
                                    --opLexicon $opLexicon \
                                    --opLexicon_withHWStr  $opLexiconWithHWR
# The above can be skipped as below Step1B will generate the lexicon needed as well

#
# Step 1B, creating the hotword decoder's lexicon AND language model count
#
python3 run_createhotWordLexiconUnigram.py --unigram_countFile ./TestData_Clean/unigram.count --topNunigram 5000 --hotwordRawList   ./TestData_Clean/hotwordRawList.txt  --opHotDecoderLexicon ./TestDataOp/hotwordDecoderLex.txt   --opHotDecoderUnigram ./TestDataOp/hotwordDecoderUnigram.txt  --fixHotWord_position 300

# we will take the top (above example) 5000 words.
# we will use the top300's count to initialize for ALL hotwords in hotword list

#
# you should NOW build your hotword decoder and score
# if you are successful, you will get 2 files,
# the hotword.ctm and the master.ctm



# We will now wish to combine master.ctm and hotword.ctm
# Step 2)  combine hotword and master decoder ctm file.
# The following command generates the dual ctm file from master and hotword ctm
#

masterCTM=./TestData_Clean/master.ctm
hotwordCTM=./TestData_Clean/hotword.ctm
dualCTM=./TestDataOp/dual.ctm
python3 run_combineCTM.py   --master_ctm  $masterCTM \
                            --hotword_ctm $hotwordCTM \
                            --collar_rate 0.25 \
                            --dual_ctm    $dualCTM \
                            --hotwordRawList $hotwordlist 



# We will generate the files for scoring
# this is the sentence level CTM withput time information, 2 fields, uttID and uttString
# 3 types of uttString
#  a) HotWordONLY       -> all none hotword removed, e.g __Orchard_Road
#  b) WordandHotWord    -> words mixed with hotword labels i visited __Orchard_Road today   (hotword labels == __hotword_label)
#  c) WordONLY       -> words only, e.g  i visited Orchard Road today


outHotWord=./TestDataOp/hotword
outMaster=./TestDataOp/master
outDual=./TestDataOp/dual
python3 run_convertCTM_toWERscoringText.py  --ctm $hotwordCTM --hotwordRawList $hotwordlist --opFileName $outHotWord
python3 run_convertCTM_toWERscoringText.py  --ctm $masterCTM  --hotwordRawList $hotwordlist --opFileName $outMaster
python3 run_convertCTM_toWERscoringText.py  --ctm $dualCTM    --hotwordRawList $hotwordlist --opFileName $outDual
