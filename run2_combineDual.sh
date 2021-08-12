#!/bin/bash
#source pathDesktop.sh
source pathLaptop.hotwordlist

# After you have run this file, and then check ./TestDataOp
# The output should be self-explanatory
#

# This script combines the output of master and hotword decoder
# Step 2.1)  combine hotword and master decoder ctm file.
# The following command generates the dual ctm file from master and hotword ctm
#

#Parameters for step2.1
in_hotwordlist=./TestData_Clean/hotwordRawList.txt   
in_refText=./TestData_Clean/groundTruth_WordOnly.txt   # the filename of the reference file MUST end with .txt
in_hotwordCTM=./TestData_Clean/hotword.ctm
in_masterCTM=./TestData_Clean/master.ctm
threshold_collar_rate=0.25
out_dualCTM=./TestDataOp/dual.ctm


#Parameters for step2.2
outRefWord=./TestDataOp/WER_refword
outHotWord=./TestDataOp/WER_hotword
outMaster=./TestDataOp/WER_master
outDual=./TestDataOp/WER_dual
in_dualCTM=$out_dualCTM    # THIS is generated from the combine

#step2.1 : combinining the CTM files
python3 run_combineCTM.py   --hotwordRawList $in_hotwordlist \
                            --master_ctm  $in_masterCTM \
                            --hotword_ctm $in_hotwordCTM \
                            --collar_rate $threshold_collar_rate \
                            --dual_ctm    $out_dualCTM 
                            



# We will generate the files for scoring
# this is the sentence level CTM withput time information, 2 fields, uttID and uttString
# 3 types of uttString
#  1) Reference         -> this is a text version of ctm file, left most field == file ID followed by text string
#  2) HotWordONLY       -> all none hotword removed, e.g __Orchard_Road
#  3) WordandHotWord    -> words mixed with hotword labels i visited __Orchard_Road today   (hotword labels == __hotword_label)
#  4) WordONLY       -> words only, e.g  i visited Orchard Road today


#step2.2 : generating the WER for the CTM files
python3 run_convertCTM_toWERscoringText.py  --ctm $in_refText     --hotwordRawList $in_hotwordlist --opFileName $outRefWord
python3 run_convertCTM_toWERscoringText.py  --ctm $in_hotwordCTM --hotwordRawList $in_hotwordlist --opFileName $outHotWord
python3 run_convertCTM_toWERscoringText.py  --ctm $in_masterCTM  --hotwordRawList $in_hotwordlist --opFileName $outMaster
python3 run_convertCTM_toWERscoringText.py  --ctm $in_dualCTM    --hotwordRawList $in_hotwordlist --opFileName $outDual

