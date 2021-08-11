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
in_hotwordlist=./TestData_Clean/hotwordRawList_with#.txt 
in_hotwordCTM=./TestData_Clean/hotword_with#.ctm

#in_hotwordlist=./TestData_Clean/hotwordRawList.txt 
#in_hotwordCTM=./TestData_Clean/hotword.ctm
in_masterCTM=./TestData_Clean/master.ctm
threshold_collar_rate=0.25
out_dualCTM=./TestDataOp/dual.ctm


#Parameters for step2.2
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
#  a) HotWordONLY       -> all none hotword removed, e.g __Orchard_Road
#  b) WordandHotWord    -> words mixed with hotword labels i visited __Orchard_Road today   (hotword labels == __hotword_label)
#  c) WordONLY       -> words only, e.g  i visited Orchard Road today


#step2.2 : generating the WER for the CTM files
python3 run_convertCTM_toWERscoringText.py  --ctm $in_hotwordCTM --hotwordRawList $in_hotwordlist --opFileName $outHotWord
python3 run_convertCTM_toWERscoringText.py  --ctm $in_masterCTM  --hotwordRawList $in_hotwordlist --opFileName $outMaster
python3 run_convertCTM_toWERscoringText.py  --ctm $in_dualCTM   --hotwordRawList $in_hotwordlist --opFileName $outDual

#  --ctm ./TestData_Clean/hotword.ctm  --hotwordRawList ./TestData_Clean/hotwordRawList.txt  --opFileName ./TestDataOp/hotword
