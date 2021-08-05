#!/bin/bash

# Yachao Guo, 2021

set -e

echo -e "\n$0 $@\n"

stage=0
script_dir=$(cd "$(dirname "$0")";pwd)

. path.sh || exit 1
. parse_options.sh || exit 1

if [ $# -ne 5 ]; then
  echo "Usage: ($0) <hotword_list> <ground_truth> <hyp_master> <hyp_hotword> <hyp_dual> <odir>"
  exit 1;
fi

hotwordlist=$1
hyp_master=$2
hyp_hotword=$3
hyp_dual=$4
odir=$5

ground_truth=$odir/text

# cp $hotwordlist $odir/hotword.list
hotwordlist=$odir/hotword.list

if [ $stage -le 1 ]; then
  sort ${ground_truth} -o ${ground_truth}
  sort ${hyp_master} -o ${hyp_master}
  sort ${hyp_hotword} -o ${hyp_hotword}
  sort ${hyp_dual} -o ${hyp_dual}
fi

if [ $stage -le 20 ]; then
  cat $hotwordlist | perl -ane 'use utf8; use open qw(:std :utf8); chomp; @words = split(/_/,$_); @new_words = ();foreach $word (@words) {if($word =~ m/[a-z]+/g) {push(@new_words,$word)} else {@chars = split(//,$word); foreach $char (@chars) {push(@new_words,$char);}}} $new_str1 = join(" ",@new_words); @words = split(/ /,$_); $new_str2 = join("_",@words); print("$new_str1\t$new_str2\n");' > ${hotwordlist}.transfer
  cat ${hotwordlist}.transfer | awk '{print $NF}' > ${hotwordlist}.new
fi

hotword_transfer_list=${hotwordlist}.transfer

if [ $stage -le 3 ]; then
  # python $script_dir/replace_words_in_kaldi_text.py ${ground_truth} $hotword_transfer_list > $odir/text_groundtruth.transfer
  # python $script_dir/replace_words_in_kaldi_text.py ${ground_truth} $hotword_transfer_list > $odir/text_groundtruth.transfer
  # python $script_dir/replace_words_in_kaldi_text.py ${hyp_master} $hotword_transfer_list > $odir/hyp_master.transfer
  python $script_dir/text_ground2only_hotword-test.py $odir/text_groundtruth.transfer $odir/ground_truth_only_hotword
  python $script_dir/text_ground2only_hotword-test.py $odir/hyp_master.transfer $odir/hyp_master_only_hotword
  python $script_dir/text_ground2only_hotword-test.py $hyp_hotword $odir/hyp_hotword_only_hotword
  python $script_dir/text_ground2only_hotword-test.py $hyp_dual $odir/hyp_dual_only_hotword
fi

if [ $stage -le 4 ]; then 
  sed "s/__//g" $odir/text_groundtruth.transfer > $odir/ground_truth_normal_tmp
  sed "s/_/ /g" $odir/ground_truth_normal_tmp > $odir/ground_truth_normal

  sed "s/__//g" $odir/hyp_master.transfer > $odir/hyp_master_normal_tmp
  sed "s/_/ /g" $odir/hyp_master_normal_tmp > $odir/hyp_master_normal

  sed "s/__//g" $hyp_hotword > $odir/hyp_hotword_normal_tmp
  sed "s/_/ /g" $odir/hyp_hotword_normal_tmp > $odir/hyp_hotword_normal

  sed "s/__//g" $hyp_dual > $odir/hyp_dual_normal_tmp
  sed "s/_/ /g" $odir/hyp_dual_normal_tmp > $odir/hyp_dual_normal
  
  rm -rf $odir/ground_truth_normal_tmp $odir/hyp_master_normal_tmp $odir/hyp_hotword_normal_tmp $odir/hyp_dual_normal_tmp
fi



