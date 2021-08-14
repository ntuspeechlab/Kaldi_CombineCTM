# Folder Name: TestData_Clean


This folder allows you to 

	1) generate the hotword decoder lexicon from the hotwordlist
	2) experimental output to combine hotword and master decoder ctm file.
	3) generate different types of sentence level ctm files (with no time information)
		for WER scoring for (wordOnly->typical), (word_hotword), and (hotwordONLY)
		types of transformed output
			a) wordOnly
			b) word_hotword
			c) hotWordOnly


#Description of the files in the folder:


#1) hotwordRawList.txt: 
This is provided BY the user of the system to create the hotword
for the hotword decoder.
The user CAN create multiple pronunciation.
The first entry is the hotword (upper/lower case sensitive)
the second entry (optional), is separated from the first field, by a colon.
the second entry casing is lower case only (case insensitive)
the second entry spells (grapheme lexicon assumed) the pronunication
and all our lexicon phones are lower case only.

Example: The following Hotword_RawList.txt has 5 entries.
In each row, there are two fields separated by :
field1 == the hotword, can be in capital, and will remember
field2 == right side of :,  this is the alternate pronunciation
if ONLY field 1, then the pronunciation is as field 1

Vu Ly Tee
Vu Ly Tee:vu lee tea
Vu Ly Tee:voo lee tea
Abraham Solomon
Admiralty Greens





#2) groundTruth_WordOnly.txt, master and hotword.ctm

groundTruth_WordOnly.txt is a file containing the ground truth of the utterance.
the first field is the name of the utterance.
the second field -> end contains words separated by space.
Example of 2 sentences in groundTruth_textOnly.txt
nsc-part2-chn0-spk00002671maf-026710134 spring singapore keck seng tower and jupiter road
nsc-part2-chn0-spk00002671maf-026710136 compassvale drive the chevrons and aljunied avenue five


hotword.ctm is a file containing the output of the hotword decoder.
Note that the hotword decoder contains words and hotword labels as possible output.
Here, hotword labels mean e.g, __keck_seng , __cheang_hong_lim_street, ...
The above are created from Hotword_RawList.txt, and the L.fst and G.fst has
words as well as hotword labels.

Example of 2 sentences in hotword.ctm
hotword.ctm file has 5 fields
field0  = filename, field 1= 1 (fixed),  field 2 = startTime. field3 = duration
field 4 = decoder word (can be normal word, or __hotword_label)

nsc-part2-chn0-spk00002671maf-026710134 1 0.00 1.05 spring 
nsc-part2-chn0-spk00002671maf-026710134 1 1.05 0.72 singapore 
nsc-part2-chn0-spk00002671maf-026710134 1 1.80 0.60 __keck_seng 
nsc-part2-chn0-spk00002671maf-026710134 1 2.40 0.45 tower 
nsc-part2-chn0-spk00002671maf-026710134 1 3.09 0.78 __jupiter_road 
nsc-part2-chn0-spk00002671maf-026710136 1 0.51 1.14 __compassvale_drive 
nsc-part2-chn0-spk00002671maf-026710136 1 1.71 0.78 <unk> 
nsc-part2-chn0-spk00002671maf-026710136 1 2.52 1.08 __aljunied_avenue 
nsc-part2-chn0-spk00002671maf-026710136 1 3.60 0.60 five 


master.ctm is a file containing output from master decoder.
It can only output words!
Example of 2 sentences in corresponding master.ctm
The master.ctm file has 5 fields
field0  = filename, field 1= 1 (fixed),  field 2 = startTime. field3 = duration
field 4 = decoder word (ONLY normal word), you can see the time, and words
between the two text files and figure out the substituion

nsc-part2-chn0-spk00002671maf-026710134 1 1.05 0.72 singapore 
nsc-part2-chn0-spk00002671maf-026710134 1 1.80 0.27 cake 
nsc-part2-chn0-spk00002671maf-026710134 1 2.10 0.75 singtel 
nsc-part2-chn0-spk00002671maf-026710134 1 2.88 0.21 and 
nsc-part2-chn0-spk00002671maf-026710134 1 3.12 0.39 twitter 
nsc-part2-chn0-spk00002671maf-026710134 1 3.51 0.36 rude 
nsc-part2-chn0-spk00002671maf-026710136 1 0.51 0.75 compassvale 
nsc-part2-chn0-spk00002671maf-026710136 1 1.26 0.39 drive 
nsc-part2-chn0-spk00002671maf-026710136 1 1.68 0.18 they 
nsc-part2-chn0-spk00002671maf-026710136 1 1.86 0.21 share 
nsc-part2-chn0-spk00002671maf-026710136 1 2.07 0.42 brands 
nsc-part2-chn0-spk00002671maf-026710136 1 2.52 0.24 and 
nsc-part2-chn0-spk00002671maf-026710136 1 2.76 0.48 arjuna 
nsc-part2-chn0-spk00002671maf-026710136 1 3.27 0.33 avenue 
nsc-part2-chn0-spk00002671maf-026710136 1 3.60 0.60 five 



#3) unigram.count
This is a count file produced by SRILM from a text file.
It has two entries, separated by a space. On the left is the word
(should be case sensitive, but ours is not? BUG?)
and right entry is count. The lexicon DOES not look very consistent!
p_b_s bs choa-chu-kang

you		432934
okay	229929
..
g_s_t	63
choa-chu-kang	267
marine-parade	45
...
p_b_s	2
i_b_m	2

and unigram_en.count_sq -->
the counts are sqrt, and ONLY the english is retained

you		657
okay	479
...
g_s_t	7
choa-chu-kang	16
marine-parade	6
...
p_b_s	1
i_b_m	1
