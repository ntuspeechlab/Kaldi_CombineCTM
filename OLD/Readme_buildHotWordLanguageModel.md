# Folder Name: TestData_Clean


This folder allows you to 

	1) build the hotword language model
	2) the hotword language model vocabulary contains the unigram of the Master decoder
		+ the list of hotword.
	3) the count of the hotword (unigram) is experimental.
			- we will  take the unigram of the master decoder (english only)
			- the above count is sqrt root (to flatten the count)
			- and then we experimented with differnt values of hotword count (typicall 100?) 


python3 run_createhotWordLexiconUnigram.py --unigram_countFile ./TestData_Clean/unigram.count --topNunigram 5000 --hotwordRawList   ./TestData_Clean/hotwordRawList.txt  --opHotDecoderLexicon ./TestDataOp/hotwordDecoderLex.txt   --opHotDecoderUnigram ./TestDataOp/hotwordDecoderUnigram.txt  --fixHotWord_position 300

# we will take the top (above example) 5000 words.
# we will use the top300's count to initialize for ALL hotwords in hotword list