#!/usr/bin/env python

# maowang@ntu,2020

import sys
import re

if len(sys.argv) != 3:
  print("Usage: python replace_words_in_kaldi_text.py <kaldi-text> <transfer-word> ")
  exit(1)
else:
  text = sys.argv[1]
  transfer_word = sys.argv[2]

txt_dict = {}

def ReplaceWordsInText(transfer_word_dict):
  org_word_sortlist = []
  underscore_nums = {}
  for org,rep in transfer_word_dict.items():
    w_ = rep.split('_')
    underscore_nums[org] = len(w_)
  underscore_nums_ = sorted(underscore_nums.items(), key=lambda item:item[1], reverse=True)

  for i in range(underscore_nums_[0][1],underscore_nums_[len(underscore_nums_)-1][1] - 1,-1):
    tmp_dict = {}
    for j in range(len(underscore_nums_)):
      if i == underscore_nums_[j][1]:
        tmp_dict[underscore_nums_[j]] = len(underscore_nums_[j][0])
    tmp_dict_ = sorted(tmp_dict.items(),key=lambda item:item[1], reverse=True)

    for x in range(len(tmp_dict_)):
      org_word_sortlist.append(tmp_dict_[x][0][0])
  
  for org_word in org_word_sortlist:
    #print(org_word)
    replace_word = transfer_word_dict[org_word]
    for uttid,txt in txt_dict.items():
      if org_word in txt:
        new_txt = txt.replace(org_word,replace_word)
        txt_dict[uttid] = new_txt

def main():
  for line in open(text):
    try:
      uttid,txt = line.strip().split(' ',1)
      txt_dict[uttid] = txt
    except:
      continue;  

  transfer_word_dict = {}
  for line in open(transfer_word):
    original_word,replace_word = line.strip().split('\t',1)
    if original_word not in transfer_word_dict:
      transfer_word_dict[original_word] = replace_word

  ReplaceWordsInText(transfer_word_dict)

  for uttid,txt in txt_dict.items():
    print(uttid + ' ' + txt)

if __name__ == '__main__':
  main()
