#!/bin/bash
test="Hello wordl bash"
echo $test
#ngram-count -text corpus.txt -order 1 -sort -tolower -write corpus.count
#sort -k 2 -n -r unigram.count > sorted_unigram.ngram-count

#step 1:
#we assume we are given unigramcount
#field 1 == token, and field 2 == count
#they can be any words from text, chinese, english, malay, etc
#our job is to extract the english words and counts to form the lexicon
#

python3 run_createhotWordLexiconUnigram.py --unigram_countFile ./TestData_Clean/unigram.count --topNunigram 1000 --hotwordRawList   ./TestData_Clean/hotwordRawList.tx
t  --opHotDecoderLexicon ./TestDataOp/hotwordDecoderLex.txt   --opHotDecoderUnigram ./TestDataOp/hotwordDecoderUnigram
--fixHotWord_position 300