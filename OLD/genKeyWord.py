# This function takes a file
#__bukit_timah
#__bukit_batok
#__lim_chong_pang
# to produce
# __bukit_timah:Bukit Timah
#__bukit_batok:Bukit Batok
#__lim_chong_pang:Lim Chong Pang

basically create a dictionary lookalike between the key (with __xxx_yy) to xxx yy


import os
opFile = open('tempOp.txt','w')
with open('keywordList.txt','r') as f:
    for index, line in enumerate(f):
        print("Line {}: {}".format(index, line.strip()))
        hotword = line.replace('__','').replace('_',' ');
        opStr = line.strip()+':'+hotword.title()

        opFile.write(opStr)
f.close()
opFile.close()