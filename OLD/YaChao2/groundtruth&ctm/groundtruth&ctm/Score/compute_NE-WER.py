#!/usr/bin/env python3

# maowang@ntu,20191212

from __future__ import division
from collections import defaultdict
import sys
import re

if len(sys.argv) !=3:
    print("python3 {} <wordfreq_file> <per_utt_file>".format(sys.argv[0]),file=sys.stderr)
    exit(1)
else:
    wordfreq_file = sys.argv[1]
    per_utt_file = sys.argv[2]

def LoadWords(wordfreq_file):
    wordfreq_dict = {}
    for line in open(wordfreq_file):
        word,freq = line.strip().split(' ')
        if word not in wordfreq_dict:
            wordfreq_dict[word] = freq
        else:
            print("those words are not unique",file=sys.stderr)
            exit(1)

    return wordfreq_dict

"""
egs:
  mml_14_feb_2018_a_session4_1-0001857-0001998 ref  okay  anytime
  mml_14_feb_2018_a_session4_1-0001857-0001998 hyp  okay  anytime
  mml_14_feb_2018_a_session4_1-0001857-0001998 op     C      C
  mml_14_feb_2018_a_session4_1-0001857-0001998 #csid 2 0 0 0
"""
def LoadPerUtt(per_utt_file):
    recognition_dict = {}
    for line in open(per_utt_file):
        uttid,text = line.strip().split(' ',1)
        hyp = uttid + ' hyp'
        csid = uttid + ' #csid'
        if line.find(hyp) == -1 and line.find(csid) == -1:
            key,txt = line.strip().split('  ',1)
            recognition_dict[key] = txt

    return recognition_dict

def ConvertMultiWhiteSpaceIntoSingleWhiteSpace(text):
    text_new = re.sub(r'\s+', ' ', text).strip()
    return text_new

def ComputeNE_WER(recognition_dict,wordfreq_dict):
    ref_op_dict = {}
    for key,txt in recognition_dict.items():
        txt_new = ConvertMultiWhiteSpaceIntoSingleWhiteSpace(txt)
        ref_op_dict[key] = txt_new

    error_ne_nums = 0
    total_ne_nums = 0
    for key,txt in ref_op_dict.items():
        uttid,flag = key.strip().split(' ',1)
        if flag == 'ref':
            ref = txt
            ref_words = ref.strip().split(' ')
            uttid_op = uttid + ' op'
            ops = ref_op_dict[uttid_op].split(' ')
            ref_word_index = -1

            for ref_word in ref_words:
                ref_word_index += 1
                if ref_word in wordfreq_dict:
                    op_token = ops[ref_word_index]
                    if op_token == 'S' or op_token == 'I' or op_token == 'D':
                        error_ne_nums += 1
                        total_ne_nums += 1
                    elif op_token == 'C':
                        total_ne_nums += 1

    total_ne_in_wordfreq = 0
    for word,freq in wordfreq_dict.items():
        total_ne_in_wordfreq += int(freq)

    #print(total_ne_nums)
    #print(total_ne_in_wordfreq)
    if total_ne_nums == total_ne_in_wordfreq:
        ne_wer = error_ne_nums / total_ne_nums * 100
        print("The Number of Named-Entities: {}".format(total_ne_nums))
        print("NE-WER: %.2f" %ne_wer)

def main():
    wordfreq_dict = LoadWords(wordfreq_file)
    recognition_dict = LoadPerUtt(per_utt_file)
    ComputeNE_WER(recognition_dict,wordfreq_dict)

if __name__ == '__main__':
    main()
