#!/bin/bash

dir=$(cd "$(dirname "$0")";pwd)

hotwordlist=keywordlist
text=text
hyp_master=hyp-master
hyp_hotword=hyp-hotword
hyp_dual=hyp_dual
odir=scoring

$dir/scoring_unigram_underscore.sh \
    $hotwordlist $text $hyp_master $hyp_hotword $hyp_dual $odir/scoring

