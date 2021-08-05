#!/bin/bash

# Mao Tingzhi, 2020

dir=$(cd "$(dirname "$0")";pwd)

set -e

echo -e "\n$0 $@\n"

stage=0


. path.sh || exit 1
. parse_options.sh || exit 1



hotwordlist=$1
ground_truth=$2
hyp_master=$3
hyp_hotword=$4
hyp_dual=$5
odir=$6

[ -d $odir ] || mkdir -p $odir
cp $ground_truth $odir/text
ground_truth=$odir/text

cp $hotwordlist $odir/hotword.list
hotwordlist=$odir/hotword.list

if [ $stage -le 1 ]; then
  sort ${ground_truth} -o ${ground_truth}
  sort ${hyp_master} -o ${hyp_master}
  sort ${hyp_hotword} -o ${hyp_hotword}
  sort ${hyp_dual} -o ${hyp_dual}
fi

if [ $stage -le 2 ]; then
  cat $hotwordlist | perl -ane 'use utf8; use open qw(:std :utf8); chomp; @words = split(/_/,$_); @new_words = ();foreach $word (@words) {if($word =~ m/[a-z]+/g) {push(@new_words,$word)} else {@chars = split(//,$word); foreach $char (@chars) {push(@new_words,$char);}}} $new_str1 = join(" ",@new_words); @words = split(/ /,$_); $new_str2 = join("_",@words); print("$new_str1\t$new_str2\n");' > ${hotwordlist}.transfer
  cat ${hotwordlist}.transfer | awk '{print $NF}' > ${hotwordlist}.new
fi

hotword_transfer_list=${hotwordlist}.transfer
if [ $stage -le 3 ]; then
  python $dir/replace_words_in_kaldi_text.py ${ground_truth} $hotword_transfer_list > $odir/text_groundtruth.transfer
  python $dir/replace_words_in_kaldi_text.py ${hyp_master} $hotword_transfer_list > $odir/hyp_master.transfer
  
  $dir/groundtruth_onlyhotword_and_normal_text.sh \
        $hotwordlist $hyp_master $hyp_hotword $hyp_dual $odir

fi

if [ $stage -le 4 ]; then
  compute-wer --text --mode=present ark:$odir/text_groundtruth.transfer ark:$odir/hyp_master.transfer > $odir/result.master || exit 1;

  compute-wer --text --mode=present ark:$odir/text_groundtruth.transfer ark:${hyp_hotword} > $odir/result.hotword || exit 1;

  compute-wer --text --mode=present ark:$odir/text_groundtruth.transfer ark:${hyp_dual} > $odir/result.dual || exit 1;

  ## Modify Start ##

  compute-wer --text --mode=present ark:$odir/ground_truth_only_hotword ark:$odir/hyp_master_only_hotword > $odir/result.master_only_hotword || exit 1;

  compute-wer --text --mode=present ark:$odir/ground_truth_normal ark:$odir/hyp_master_normal > $odir/result.master_noraml || exit 1;

  compute-wer --text --mode=present ark:$odir/ground_truth_only_hotword ark:$odir/hyp_hotword_only_hotword > $odir/result.hotword_only_hotword || exit 1;

  compute-wer --text --mode=present ark:$odir/ground_truth_normal ark:$odir/hyp_hotword_normal > $odir/result.hotword_normal || exit 1;

  compute-wer --text --mode=present ark:$odir/ground_truth_only_hotword ark:$odir/hyp_dual_only_hotword > $odir/result.dual_only_hotword || exit 1;

  compute-wer --text --mode=present ark:$odir/ground_truth_normal ark:$odir/hyp_dual_normal > $odir/result.dual_normal || exit 1;

  ## Modify End ##

fi

if [ $stage -le 5 ]; then
  align-text --special-symbol="'***'" ark:$odir/text_groundtruth.transfer ark:$odir/hyp_master.transfer ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_master 2>/dev/null
  align-text --special-symbol="'***'" ark:$odir/text_groundtruth.transfer ark:${hyp_hotword} ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_hotword 2>/dev/null
  align-text --special-symbol="'***'" ark:$odir/text_groundtruth.transfer ark:${hyp_dual} ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_dual 2>/dev/null

  ## Modify Start ##

  align-text --special-symbol="'***'" ark:$odir/ground_truth_only_hotword ark:$odir/hyp_master_only_hotword ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_master_only_hotword 2>/dev/null

  align-text --special-symbol="'***'" ark:$odir/ground_truth_normal ark:$odir/hyp_master_normal ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_master_normal 2>/dev/null

  align-text --special-symbol="'***'" ark:$odir/ground_truth_only_hotword ark:$odir/hyp_hotword_only_hotword ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_hotword_only_hotword 2>/dev/null

  align-text --special-symbol="'***'" ark:$odir/ground_truth_normal ark:$odir/hyp_hotword_normal ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_hotword_normal 2>/dev/null

  align-text --special-symbol="'***'" ark:$odir/ground_truth_only_hotword ark:$odir/hyp_dual_only_hotword ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_dual_only_hotword 2>/dev/null

  align-text --special-symbol="'***'" ark:$odir/ground_truth_normal ark:$odir/hyp_dual_normal ark,t:- | utils/scoring/wer_per_utt_details.pl --special-symbol "'***'" | tee > $odir/per_utt_dual_normal 2>/dev/null

  ## Modify End ##

fi

if [ $stage -le 6 ]; then
   python $dir/count_hotwordlist_freq.py $odir/text_groundtruth.transfer ${hotwordlist}.new > ${hotwordlist}.freq
fi

hotword_freq_list=${hotwordlist}.freq
if [ $stage -le 7 ]; then
  python $dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_master >> $odir/result.master
  python $dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_hotword >> $odir/result.hotword
  python $dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_dual >> $odir/result.dual
<<!
  ## Modify Start ##
  
  python $script_dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_master_only_hotword >> $odir/result.master_only_hotword
  python $script_dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_master_normal >> $odir/result.master_noraml
  
  python $script_dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_hotword_only_hotword >> $odir/result.hotword_only_hotword
  python $script_dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_hotword_normal >> $odir/result.hotword_normal

  python $script_dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_dual_only_hotword >> $odir/result.dual_only_hotword
  python $script_dir/compute_NE-WER.py $hotword_freq_list $odir/per_utt_dual_normal >> $odir/result.dual_normal

  ## Modify End ##
!
fi

if [ $stage -le 8 ]; then
  echo "***master asr***"
  cat $odir/result.master | grep -P "WER|NE-WER"
  echo "***hotword asr***"
  cat $odir/result.hotword | grep -P "WER|NE-WER"
  echo "***dual asr engine***"
  cat $odir/result.dual | grep -P "WER|NE-WER"

  ## Modify Start ##
  
  echo "########################################"
  echo "***master only hotword asr***"
  cat $odir/result.master_only_hotword | grep -P "WER|NE-WER"
  echo "***hotword only hotword asr***"
  cat $odir/result.hotword_only_hotword | grep -P "WER|NE-WER"
  echo "***dual asr only hotword engine***"
  cat $odir/result.dual_only_hotword | grep -P "WER|NE-WER"

  echo "########################################"
  echo "***master normal asr***"
  cat $odir/result.master_noraml | grep -P "WER|NE-WER"
  echo "***hotword normal asr***"
  cat $odir/result.hotword_normal | grep -P "WER|NE-WER"
  echo "***dual asr normal engine***"
  cat $odir/result.dual_normal | grep -P "WER|NE-WER"
  
  ## Modify End ##


fi
