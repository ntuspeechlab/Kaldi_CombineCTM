

def read_HotWordDictionary(infilename):
    hotword_KeyToPron = {}
    hotword_PronToKey = {}
    infile = open(infilename)
    for line in infile:
        (key, pron) = line.split(':')
        hotword_KeyToPron[key] = pron.strip()
        hotword_PronToKey[pron.strip()] = key

    return(hotword_KeyToPron, hotword_PronToKey)


dictName = "./TestData1/LookupKeywordList.txt"
(myDict_KeyToPron, myDict_PronToKey) = read_HotWordDictionary(dictName)
print(myDict_KeyToPron)
print(myDict_PronToKey)
