#!/usr/bin/env python3

# Mao Tingzhi, 2020

import sys

if len(sys.argv) != 3:
  print("python count_hotwordlist_freq.py <kaldi-text> <hotwordlist>",file=sys.stderr)
  exit(1)
else:
  kalditext = sys.argv[1]
  hotwordlist = sys.argv[2]

word_count = {}

def main():
  for line in open(kalditext):
    uttid,txt = line.strip().split(" ",1)
    words = txt.split(" ")
    for word in words:
      if word not in word_count:
        word_count[word] = 1
      else:
        word_count[word] += 1    

  for hotword in open(hotwordlist):
    hotword= hotword.strip()
    if hotword in word_count:
      print(hotword + " " + str(word_count[hotword]))

if __name__ == '__main__':
  main()
