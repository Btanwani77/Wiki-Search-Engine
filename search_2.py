from collections import defaultdict
from operator import itemgetter
import re, sys, os
from math import log10
from Stemmer import Stemmer
from bisect import bisect
import timeit

myStemmer = Stemmer("english")					#Stemmer instance

stopwords=defaultdict(int)						#Making Stopwords dictionary 	
stopfile = open('stopwords.txt','r')
for line in stopfile:
	line = line.strip()
	stopwords[line] = 1

N_doc = 17640866										#Making document_id and Doc_title mapper
mapper = {}
docfile = open("docindex1.txt", "r")
for line in docfile:
	mydocid, res = line.split('#')
	mapper[mydocid] = res
	# N_doc += 1									#Total documents in whole dump

secondary_index_list = []						#Loading secondary index in memory
with open("/Users/jayant/ire mini project/wiki_search_engine/20162073/final_index/Secondary_Index.txt", "r") as f:
	lines = f.readlines()
	for i in lines:
		secondary_index_list.append(i.split()[0])

while True:										
	query = raw_input("Please enter your query:")		#Input query
	start = timeit.default_timer()
	
	query_type = ""								#Getting type of query
	if ':' in query:
		query_type = "field"
	else:
		query_type = "normal"	

	words_in_query = query.split()				#Processing query

	if query_type == "normal":
		words_to_search = []
		for word in words_in_query:
			word = word.lower().strip()
			if word not in stopwords:
				word = myStemmer.stemWord(word)
			if word.isalpha() and len(word)>=3 and word not in stopwords:
				words_to_search.append(word)

		globalSearch = dict(list())
		for word in words_to_search:
			loc = bisect(secondary_index_list, word)
			startflag = 0
			if loc-1>=0 and secondary_index_list[loc-1] == word:
				startflag = 1
				if loc-1 != 0:
					loc = loc-1
				if loc+1 == len(secondary_index_list) and secondary_index_list[loc] == word:
					loc = loc+1

			primaryfile_to_open = "/Users/jayant/ire mini project/wiki_search_engine/20162073/final_index/index" + str(loc) + ".txt"
			file = open(primaryfile_to_open, "r")
			data = file.read()
			try:
				if startflag == 1:
					start_index = data.find(word+"=")
				else:
					start_index = data.find('\n'+word+"=")

					
				end_index = data.find('\n', start_index+1)
				req_line = data[start_index:end_index]
				pl = req_line.split('=')[1].split(',')
				num_of_doc = len(pl)
				# pl = pl[:120000]
				# for i in pl:
				# 	print i
				idf = log10(N_doc/num_of_doc)

				for i in pl:
					doc_id,entry= i.split(':')
					if doc_id in globalSearch:
						globalSearch[doc_id].append(entry + "_" + str(idf))
					else:
						globalSearch[doc_id] = [entry + "_" + str(idf)]
			except:
				pass			
		lengthFreq = dict(dict())
		regex = re.compile(r'(\d+|\s+)')

		try:
			for k in globalSearch:
				weighted_freq = 0;
				n = len(globalSearch[k])
				for x in globalSearch[k]:
					x,idf = x.split('_')
					x = x.split('#')
					for y in x:
						lis = regex.split(y)
						tag_type, frequency = lis[0], lis[1]
						if tag_type == 't':
							weighted_freq += int(frequency)*10000
						elif tag_type == 'i' or tag_type == 'e' or tag_type == 'c' or tag_type == 'r':
							weighted_freq += int(frequency)*50
						elif tag_type == 'b':
							weighted_freq += int(frequency)		
						# weighted_freq += int(re.search(r'\d+', y).group())
						
				if n in lengthFreq:
					lengthFreq[n][k] = float(log10(1+weighted_freq))*float(idf)
				else:
					lengthFreq[n] = {k : float(log10(1+weighted_freq))*float(idf)}

			count = 0
			flag = 0
			result_list = []
			K = 10
			import linecache

			for k,v in sorted(lengthFreq.items(), reverse=True):
				for k1,v1 in sorted(v.items(), key=itemgetter(1), reverse=True):
					print mapper[k1]
					count += 1
					if(count == K):
						flag = 1
						break
				if flag:
					break;	
			stop = timeit.default_timer()
			globalSearch.clear()
			print stop - start		
		except:
			pass	

	else:
		
		words_to_search = []
		field_dict = {}
		for word in words_in_query:
			tag, w = word.split(':')
			w = w.lower()
			if w not in stopwords:
				w = myStemmer.stemWord(w)
			if w.isalpha() and len(w)>=3 and w not in stopwords:
				words_to_search.append(w)
				if w in field_dict:
					field_dict[w] += tag
				else:
					field_dict[w] = tag	

		globalSearch = dict(list())
		for word in words_to_search:
			loc = bisect(secondary_index_list, word)
			startflag = 0
			if loc-1>=0 and secondary_index_list[loc-1] == word:
				startflag = 1
				if loc-1 != 0:
					loc = loc-1
				if loc+1 == len(secondary_index_list) and secondary_index_list[loc] == word:
					loc = loc+1

			primaryfile_to_open = "/Users/jayant/ire mini project/wiki_search_engine/20162073/final_index/index" + str(loc) + ".txt"
			file = open(primaryfile_to_open, "r")
			data = file.read()
			try:
				if startflag == 1:
					start_index = data.find(word+"=")
				else:
					start_index = data.find('\n'+word+"=")

					
				end_index = data.find('\n', start_index+1)
				req_line = data[start_index:end_index]
				pl = req_line.split('=')[1].split(',')
				num_of_doc = len(pl)
				# pl = pl[:120000]
				idf = log10(N_doc/num_of_doc)

				for i in pl:
					doc_id,entry= i.split(':')
					for x in field_dict[word]:
						if x in entry:
							if doc_id in globalSearch:
								globalSearch[doc_id].append(entry + "_" + str(idf))
							else:
								globalSearch[doc_id] = [entry + "_" + str(idf)]
			except:
				pass			
		lengthFreq = dict(dict())
		regex = re.compile(r'(\d+|\s+)')

		try:
			for k in globalSearch:
				weighted_freq = 0;
				n = len(globalSearch[k])
				for x in globalSearch[k]:
					x,idf = x.split('_')
					x = x.split('#')
					for y in x:
						lis = regex.split(y)
						tag_type, frequency = lis[0], lis[1]
						if tag_type == 't':
							weighted_freq += int(frequency)*10000
						elif tag_type == 'i' or tag_type == 'e' or tag_type == 'c' or tag_type == 'r':
							weighted_freq += int(frequency)*50
						elif tag_type == 'b':
							weighted_freq += int(frequency)		
						# weighted_freq += int(re.search(r'\d+', y).group())
						
				if n in lengthFreq:
					lengthFreq[n][k] = float(log10(1+weighted_freq))*float(idf)
				else:
					lengthFreq[n] = {k : float(log10(1+weighted_freq))*float(idf)}

			count = 0
			flag = 0
			result_list = []
			K = 10
			import linecache

			for k,v in sorted(lengthFreq.items(), reverse=True):
				for k1,v1 in sorted(v.items(), key=itemgetter(1), reverse=True):
					print mapper[k1]
					count += 1
					if(count == K):
						flag = 1
						break
				if flag:
					break;	
			stop = timeit.default_timer()
			globalSearch.clear()
			print stop - start		
		except:
			pass