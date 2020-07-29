import sys
from porterStemmer import PorterStemmer
from collections import defaultdict
import os
import gc
import re
import time
import math
from array import array
from queryindex import QueryIndex
porter = PorterStemmer()
path=''

class CreateIndex:

	def __init__(self):
		self.index = defaultdict(list)
		self.stopwordsFile = 'stopwords.dat'
		self.sw = {}
		self.indexOut = 'index.txt'
		self.numDocuments = 0
		self.tf=defaultdict(list)
		self.df=defaultdict(int)
		self.filewords=defaultdict(int)
		self.totalwords = 0

	def getparameters(self):
		param = sys.argv
		self.stopwordsFile = param[1]
		self.indexOut = param[2]
		self.filenameword = param[3]

	def getstopwords(self):
		f = open(self.stopwordsFile, 'r')
		stopwords = [line.rstrip() for line in f]
		self.sw = dict.fromkeys(stopwords)
		f.close()

	def writeIndexToFile(self):
		'''write the inverted index to the file'''
		f = open(self.indexOut, 'w')
		# print >> f,self.numDocuments
		for term in self.index.iterkeys():
			postinglist = []
			for p in self.index[term]:
				# print p,term
				docID = p[0]
				wordnum = p[1]
				linenum = p[2]
				postinglist.append(':'.join([str(docID), ','.join(map(str, wordnum)), '#'.join(map(str, linenum))]))
			tfData=','.join(map(str,self.tf[term]))
			# idfData=str(math.log((self.numDocuments-(self.df[term])+0.5)/((self.df[term])+0.5)))
			idfData='%.4f' % (self.numDocuments/self.df[term])
			print >> f, '|'.join((term, ';'.join(postinglist),tfData,idfData))
		f.close()
		# print self.totalwords, self.numDocuments
		f = open(self.filenameword, 'w')
		# print >> f,self.totalwords
		for filename, noofwords in self.filewords.iteritems():
			# print noofwords
			lenbyaveragefilelen = float((noofwords*self.numDocuments))/float(self.totalwords) # |D|/avgdl
			print >> f, filename, lenbyaveragefilelen
		f.close()


	def createindex(self):
		global path
		path = raw_input("Give Path of folder having files to be indexed: ")
		print "Indexing..."
		self.getparameters()
		self.getstopwords()
		# bug in python garbage collector!
		# appending to list becomes O(N) instead of O(1) as the size grows if gc is enabled.
		gc.disable()
		start_time = time.time()
		for files in os.listdir(path):
			self.filewords[files]=0
			self.numDocuments += 1
			with open(path+'/'+files, 'r') as file:
				singlefiledict = {}
				singlefilelist = []
				
			   # for line in file:
					# linenumber = linenumber+1
				for linenumber, line in enumerate(file):
					
					line = line.lower()
					line = re.sub(r'[^a-z0-9 ]', ' ', line)
					for word in line.split():
						if word not in self.sw:
							singlefilelist.append([porter.stem(word, 0, len(word)-1),linenumber+1])
				for position, term in enumerate(singlefilelist):
					try:
						singlefiledict[term[0]][1].append(position)
						singlefiledict[term[0]][2].append(term[1])
					except:
						singlefiledict[term[0]]=[files, array('I',[position]), array('I',[term[1]])]

				#normalize the document vector
				norm=0
				for term, posting in singlefiledict.iteritems():
					self.filewords[files]+=len(posting[1])
					norm+=len(posting[1])**2
				norm=math.sqrt(norm)
				
				#calculate the tf and df weights
				for term, posting in singlefiledict.iteritems():
					self.tf[term].append('%.4f' % (len(posting[1])/norm))
					self.df[term]+=1

				#merge the current page index with the main index
				for termPage, postingPage in singlefiledict.iteritems():
					self.index[termPage].append(postingPage)
			self.totalwords += self.filewords[files]
			file.close()

		gc.enable()
		end_time = time.time()
		# print end_time-start_time
		self.writeIndexToFile()
		print "Indexing Completed.\n"


if __name__ == "__main__":
	c = CreateIndex()
	c.createindex()
	q = QueryIndex()
	q.queryIndex(path)

