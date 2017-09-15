
#!/usr/bin/python
import xml.sax
import nltk,sys,time
import timeit
from nltk.stem import PorterStemmer
from collections import defaultdict
from operator import itemgetter
#nltk.download('corpus')
#from nltk.corpus import wordnet
import re
import json
from itertools import izip
from heapq import heapify, heappush, heappop
import os


start = timeit.default_timer()
folder = "final_index/"
indexFileCount = 0
secondaryIndex = dict()
chunksize = 100000

def writeToPrimary():
    global folder
    global globalDict
    global indexFileCount
    offset = []
    firstWord = True
    indexFileCount += 1
    filename = folder+"index"+str(indexFileCount)+".txt"
    fp = open(filename,'wb')
    for i in sorted(globalDict):
        if firstWord:
            secondaryIndex[i] = indexFileCount
            firstWord = False
        toWrite = str(i)+"="+globalDict[i]+"\n"
        fp.write(toWrite)

def writeToSecondary():
    global secondaryIndex
    filename = folder+"Secondary_Index.txt"
    fp = open(filename,'wb')
    for i in sorted(secondaryIndex):
        tmp = str(i)+" "+str(secondaryIndex[i])+"\n"
        fp.write(tmp)


import glob
files = glob.glob('/Users/jayant/ire mini project/wiki_search_engine/20162073/created_files/*')
primary_index = open('/Users/jayant/ire mini project/wiki_search_engine/20162073/primary_index.txt','a')


completedFile = [0]*len(files)
filePointers = dict()
currentRowOfFile = dict()
percolator = list()
words = dict()
total = 0
globalDict = defaultdict()

for i in range(len(files)):
    completedFile[i] = 1;
    filePointers[i] = open(files[i],'r')
    currentRowOfFile[i] = filePointers[i].readline()
    words[i] = currentRowOfFile[i].strip().split('=')
    if words[i][0] not in percolator:
        heappush(percolator,words[i][0])

while True:
    if completedFile.count(0) == len(files):
        break;
    else:
        total += 1
        word = heappop(percolator)
        for i in range(len(files)):
            if completedFile[i] and words[i][0] == word:
                if word in globalDict:
                    globalDict[word] += ','+words[i][1]
                else:
                    globalDict[word] = words[i][1]

                if total == chunksize:
                    total = 0;
                    writeToPrimary()
                    globalDict.clear()

                currentRowOfFile[i] = filePointers[i].readline()
                currentRowOfFile[i] = currentRowOfFile[i].strip()

                if currentRowOfFile[i]:
                    words[i] = currentRowOfFile[i].split('=')
                    if words[i][0] not in percolator:
                        heappush(percolator,words[i][0])
                else:
                    completedFile[i] = 0
                    filePointers[i].close()
                    os.remove(files[i])

writeToPrimary()
writeToSecondary()
stop = timeit.default_timer()
print (stop - start)
