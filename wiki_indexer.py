import re
import json
import sys
import timeit
import operator
from collections import defaultdict
from operator import itemgetter
# from nltk.stem import PorterStemmer
from xml.sax import parse, SAXParseException, ContentHandler
from sortedcontainers import  SortedDict
from Stemmer import Stemmer

stemmer = Stemmer("english");
# globalDict = SortedDict(SortedDict(defaultdict(int)));
globalDict = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
docIndex=open('docindex.txt','a')
folder = "created_files/"
# globalDict = SortedDict(SortedDict());
re1 = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
re2 = re.compile('{\|(.*?)\|}',re.DOTALL)
re3 = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)
re4 = re.compile(r'{{v?cite(.*?)}}',re.DOTALL)
re5 = re.compile(r'<(.*?)>',re.DOTALL)
re6 = re.compile(r'[.,;_()"/\']',re.DOTALL)
re7 = re.compile("[~`!@#$%-^*+{\[}\]\|\\<>/?]",re.DOTALL)
re8 = re.compile( '{{infobox(.*?)}}',re.DOTALL)
re9 = re.compile(r'== ?references ?==(.*?)==',re.DOTALL)
re10 = re.compile(r'{{(.*?)}}',re.DOTALL)
re11 = re.compile("[~`!@#$%-^*+{\[}\]\|\\<>/?]",re.DOTALL)

stopwords=defaultdict(int)
with open('stopwords.txt','r') as f:
    for line in f:
        line= line.strip()
        stopwords[line]=1
def stopWords(listOfWords):
    temp=[key for key in listOfWords if stopwords[key]!=1]
    return temp

def tokenise(ch):
    global re1
    global re2
    global re3
    global re4
    global re5
    global re6
    ch = re1.sub('',ch )
    ch = re2.sub('', ch )
    ch = re3.sub('',ch )
    ch = re4.sub('',ch )
    ch = re5.sub('',ch )
    ch = re6.sub(' ',ch )
    return ch;

def makeStem(data,docID,typ):
    global globalDict
    global stemmer
    for x in data:
        x = x.strip().encode('utf-8')
        if x.isalpha() and len(x)>3 and x not in stopwords:
            stemmed = stemmer.stemWord(x)
            # if stemmed not in stopwords:
            #     if typ in globalDict[stemmed]:
            #         if docID in globalDict[stemmed][typ]:
            #             globalDict[stemmed][typ][docID]=globalDict[stemmed][typ][docID]+1
            #         else:
            #             globalDict[stemmed][typ].update({docID:1})
            #     else:
            #         globalDict[stemmed].update({typ:{docID:1}})
            if stemmed not in stopwords:
                if stemmed in globalDict:
                    if docID in globalDict[stemmed]:
                        if typ in globalDict[stemmed][docID]:
                            globalDict[stemmed][docID][typ] += 1
                        else:
                            globalDict[stemmed][docID][typ] = 1;
                    else:
                        globalDict[stemmed][docID] = {typ:1}
                else:
                    globalDict[stemmed] = dict({docID:{typ:1}})

            # if stemmed in globalDict:
            #     if docID in globalDict[stemmed]:
            #         globalDict[stemmed][docID] += 1
            #     else:
            #         globalDict[stemmed][docID] = 1
            # else:
            #     globalDict[stemmed] = SortedDict({docID:1})


def processchar(ch,title,text,docID):
    ch=ch.lower()
    ch2=[]
    ch = tokenise(ch)
    if title == 1:
        word = ch.split()
        word = [re7.sub(' ',i) for i in word if i.isalpha() and i not in stopwords]
        makeStem(word,docID,'t')
    elif text == 1:
        tokens=[]
        ref = []
        et = []
        cat = []
        info = []
        etind = 0
        refind = 0
        catind = len(ch)
        cat=re.findall(r'\[\[category:(.*?)\]\]',ch,flags=re.MULTILINE)
        info=re.findall ( '{{infobox(.*?)}}', ch,re.DOTALL)
        ch=re8.sub('', ch )
        try:
            etind = ch.index('=external links=')+20
        except:
            pass
        try:
            catind = ch.index('[[category:')+20
        except:
            pass
        if etind:
            et=ch[etind:catind]
            et=re.findall(r'\[(.*?)\]',et,flags=re.MULTILINE)
        ref=re.findall(r'== ?references ?==(.*?)==',ch,flags=re.DOTALL)
        ch=re9.sub('',ch)
        ch=re10.sub('',ch)
        if etind:
            ch = ch[0:etind]

        ch=re11.sub(' ',ch )
        ch2=ch.split()
        makeStem(ch2,docID,'b')

        et = ' '.join(et)
        et=re11.sub(' ',et )
        et = et.split()
        makeStem(et,docID,'e')


        cat = ' '.join(cat)
        cat = re11.sub(' ',cat)
        cat = cat.split()
        makeStem(cat,docID,'c')

        ref = ' '.join(ref)
        ref = re11.sub(' ',ref)
        ref = ref.split()
        makeStem(ref,docID,'r')




        for token in info:
            s = []
            s=re.findall(r'=(.*?)\|',token,re.DOTALL)
            s = ' '.join(s)
            s = re11.sub(' ',s)
            s = s.split()
            makeStem(cat,docID,'i')

        if docID%5000 == 0:
            f = open(folder+str(docID)+".txt",'a')
            for key,val in sorted(globalDict.items()):
                s = str(key.encode('utf-8'))+"="
                for k,v in sorted(val.items()):
                    s += str(k)+":"
                    for k1,v1 in v.items():
                        s = s+ str(k1)+str(v1)+"#"
                    s = s[:-1]+','
                f.write(s[:-1]+'\n')

            # for word in sorted(globalDict.keys()):
            #     x = json.dumps(globalDict[word])
            #     f.write('{"'+word+'":'+x+'}\n')
            f.close()
            globalDict.clear()



class wikiSE( ContentHandler ):
    globalFlag = 0
    def __init__( self):
        ContentHandler.__init__( self )
        self.text = 0;
        self.doc_id = 1;
        self.title = 0;
        self.redirect = 0;
        self.buffer = "";
        self.flag = 0;
        self.tit = "";

    def startElement( self, name, attributes ):

        if name == "title":
            self.buffer = "";
            self.title = 1;
            self.flag=1
        if name == "text":
            self.buffer = "";
            self.text = 1;
        if name == "page":
            self.doc_id=self.doc_id+1
        if name=="redirect":
            self.redirect=1
        if name == "id" and self.flag==1:
            self.buffer = "";

    def endElement( self, name ):
        if name == "title":
            processchar(self.buffer,1,0,self.doc_id)
            self.title = 0
            self.tit=self.buffer
            self.buffer = "";

        elif name == "text":
            processchar(self.buffer,0,1,self.doc_id)
            self.text = 0
            self.buffer = "";
        elif name == "redirect":
            self.redirect = 0
        elif name == "id" and self.flag == 1:
            try:
                docIndex.write(str(self.doc_id)+":"+self.tit+":"+self.buffer+'\n')
            except:
                docIndex.write(str(self.doc_id)+':'+(self.tit).encode('utf-8')+':'+(self.buffer).encode('utf-8')+'\n')
            self.flag = 0;
            self.buffer = ""
    def characters(self,content):
        self.buffer = self.buffer+content

def main():
    if len(sys.argv)!=3:
        print("Usage: python wiki.py sample.xml ./")
        sys.exit(0);
    file = sys.argv[1]
    parse( file, wikiSE())
    file1 = open(sys.argv[2],"w")
    s = ""
    global globalDict
    print len(globalDict)
    if len(globalDict) > 0:
        f = open(folder+str(len(globalDict))+".txt",'a')
        for key,val in sorted(globalDict.items()):
            s = str(key.encode('utf-8'))+"="
            for k,v in sorted(val.items()):
                s += str(k)+":"
                for k1,v1 in v.items():
                    s = s+ str(k1)+str(v1)+"#"
                s = s[:-1]+','
            f.write(s[:-1]+'\n')
        # for word in sorted(globalDict.keys()):
        #     x = json.dumps(globalDict[word])
        #     f.write('{"'+word+'":'+x+'}\n')
        f.close()
        globalDict.clear()


if __name__ == "__main__":
    start = timeit.default_timer()
    main()


    stop = timeit.default_timer()
    print (stop - start)




    
