

def read_HotWordDictionary(infilename):
    hotword_KeyToPron = {}
    hotword_PronToKey = {}
    arrayPron = []
    infile = open(infilename)
    for line in infile:
        (key, pron) = line.split(':')
        hotword_KeyToPron[key] = pron.strip()
        hotword_PronToKey[pron.strip()] = key
        arrayPron.append(pron.strip())

    return(hotword_KeyToPron, hotword_PronToKey,arrayPron)


dictName = "./TestData1/LookupKeywordList.txt"
(myDict_KeyToPron, myDict_PronToKey, arrayPron) = read_HotWordDictionary(dictName)
print(myDict_KeyToPron)
print(myDict_PronToKey)
print(arrayPron)
arrayPron.sort()
print(arrayPron)

fileName = './TestData1/KeywordRawList.txt'
opfile = open(fileName,"w",encoding='utf8')
for eachRawHotWord in arrayPron:
    opfile.write("{0}\n".format(eachRawHotWord))
opfile.close()
