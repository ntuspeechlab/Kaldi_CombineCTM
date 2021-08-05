THIS SCRIPT IS TO DESCRIBE THE SCORING FOLDER'S FILE'S FUNCTION

# Modify By Yachao Guo,2021


FILENAME                --FUNCTION 

ground_truth_normal     --groundtruth-text without endscop
ground_truth_only_hotword   --groundtruth-text only contain hotword

hotword.list    --hotword list
hotword.list.freq   --hotword with frequency list
hotword.list.transfer    --hotword list with hotword without endscop

hyp_dual_normal     --dual_asr_hypothesis without endscop
hyp_dual_only_hotword     --dual_asr_hypothesis only contain hotword

hyp_hotword_normal      --hotword_asr_hypothesis without endscop
hyp_hotword_only_hotword    --hotword_asr_hypothesis only contain hotword

hyp_master.transfer     --hyp_master_asr hypothesis with endscop hotword
hyp_master_normal       --hyp_master_asr hypothesis without endscop
hyp_master_only_hotword     --hyp_master_asr hypothesis only contain hotword

per_utt_dual    --per_uttence decode log use dual asr system
per_utt_dual_normal     --per_uttence decode log use dual asr system,hypothesis without endscop
per_utt_dual_only_hotword    --per_uttence decode log use dual asr system,hypothesis only contain hotword

per_utt_hotword     --per_uttence decode log use hotword asr system 
per_utt_hotword_normal      --per_uttence decode log use hotword asr system,hypothesis without endscop
per_utt_hotword_only_hotword    --per_uttence decode log use hotword asr system,hypothesis only contain hotword

per_utt_master     --per_uttence decode log use master asr system 
per_utt_master_normal      --per_uttence decode log use master asr system,hypothesis without endscop
per_utt_master_only_hotword    --per_uttence decode log use master asr system,hypothesis only contain hotword

result.dual       --dual asr system word error rate result
result.dual_normal      --dual asr system word error rate result with dual asr normal transciption
result.dual_only_hotword      --dual asr system word error rate result with dual asr hotword transciption

result.hotword       --hotword asr system word error rate result
result.hotword_normal     --hotword asr system word error rate result with hotword asr normal transciption
result.hotword_only_hotword      --hotword asr system word error rate result with hotword asr hotword transciption

result.master       --master asr system word error rate result
result.master_normal     --master asr system word error rate result with master asr normal transciption
result.master_only_hotword      --master asr system word error rate result with master asr hotword transciption

text    --groundtruth text
text_groundtruth.transfer     --groundtruth text's hotword with endscop