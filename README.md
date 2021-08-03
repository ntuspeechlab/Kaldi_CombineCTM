# Kaldi_CombineCTM
 combining Master and Hotword Decoder CTM files

### Author: Chng Eng Siong
### Date: 31st July 2021

Objective: This code is to help combine two CTM files produced by two decoders.
We will call these two decoders (Kaldi) Master and Hotword decoders.
These two decoders act on the same test files.
The hotword decoder specialises on the hotword. 
And the idea is to replace found hotwords from hotword decoder CTM
into the Master CTM.

run_combineCTM.py --master_ctm ./TestData/master.ctm --hotword_ctm ./TestData/hotword.ctm --collar_rate 0.25 --dual_ctm ./TestData/dual.ctm

