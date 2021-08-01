# Kaldi_CombineCTM
 combining Master and Hotword Decoder CTM files

## Author: CHng Eng Siong
##Created: 31st July 2021
Last modified: 1st Aug 2021

Objective:

    1) develop code to combine CTM of master decoder and hotword decoder (kaldi format)
    2) Assume we have run 2 decoders ON THE SAME Test set.
    3) This directory will execute a code test_combineCTM.py (see main function)
        to combine the master and hotword decoder's CTM
    4) You can see the TestData directory (3 utterance as an example)

    # I have not figured the correct parameter 'collar' to use yet, now set to 0.25 (of duration of word)


To Run the code:
python3 test_combineCTM.py --master_ctm ./TestData/master.ctm --hotword_ctm ./TestData/hotword.ctm --collar_rate 0.25 --dual_ctm ./TestData/dual.ctm

See the output in ./TestData
you can compare it to dualcheck.ctm
