#!/bin/bash
#source pathDesktop.sh
source pathLaptop.sh

# After you have run this file, and then check ./TestDataOp
# The output should be self-explanatory
#

# This script scores the WER of the master, hotword, and dual decoder's output
#


#Parameters for step3.1
inRefWord=./TestDataOp/WER_refword
inDual=./TestDataOp/WER_dual
inMaster=./TestDataOp/WER_master
inHotWord=./TestDataOp/WER_hotword

outWERDualResult=./TestDataOp/WER_result
outWERMasterResult=./TestDataOp/WER_result
outWERHotWordResult=./TestDataOp/WER_result

python3 run_scoreWER.py --ref $inRefWord --hyp $inDual --opFileName $outWERDualResult --remarkStr "DualDecoder Result"
python3 run_scoreWER.py --ref $inRefWord --hyp $inMaster --opFileName $outWERMasterResult --remarkStr "MasterDecoder Result"
python3 run_scoreWER.py --ref $inRefWord --hyp $inHotWord --opFileName $outWERHotWordResult --remarkStr "HotWordDecoder Result"



  

