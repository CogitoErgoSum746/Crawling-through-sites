import numpy as np
import pandas as pd
from google.colab import drive
drive.mount('/content/drive/')

Path='drive/MyDrive/Assignment1_Blackcoffer/INPUT/'
data=pd.read_csv(Path+'Book1.csv') 
dataset=data.drop(columns='ID',index=[7,20,107]) # As these 3 links had no content(404 error)

datalinks=dataset['URL'].tolist()

# !pip install scrapy
# !pip install pyphen
# !pip install nltk

# import nltk
# nltk.download('stopwords')
# nltk.download('punkt')

import scrapy
from scrapy.crawler import CrawlerProcess
titleCollection=[]
pCollection=[]

class Pagination(scrapy.Spider):
    name = 'Pagination'
    start_urls = datalinks
    
    custom_settings={
        'DOWNLOAD_DELAY': 0.25,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1
    }

    def parse(self, response):
        global titleCollection,pCollection
        
        if response.status == 200:
            killo=response.css('title::text').get()
            killo2=response.css('p::text').getall()
            pCollection.append(killo2)
            titleCollection.append(killo)
        
#         if response.status == 404:
#             pCollection.append([""])
#             titleCollection.append("")

process=CrawlerProcess({
    'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
})
process.crawl(Pagination)
process.start()

import nltk
from nltk import word_tokenize,sent_tokenize
from nltk.corpus import stopwords
sw=stopwords.words('english')

with open(Path+'StopWords/StopWords_Auditor.txt') as f:
    StopWords_Auditor = [line.rstrip('\n') for line in f]
with open(Path+'StopWords/StopWords_Currencies.txt',encoding='latin-1') as f:
    StopWords_Currencies=[]
    for x in f:
       temp= x.split(' |',1)
       StopWords_Currencies.append(temp[0])
with open(Path+'StopWords/StopWords_DatesandNumbers.txt') as f:
    StopWords_DatesandNumbers = [line.rstrip('\n') for line in f]
with open(Path+'StopWords/StopWords_Generic.txt') as f:
    StopWords_Generic = [line.rstrip('\n') for line in f]
with open(Path+'StopWords/StopWords_GenericLong.txt') as f:
    StopWords_GenericLong = [line.rstrip('\n') for line in f]
with open(Path+'StopWords/StopWords_Geographic.txt') as f:
    StopWords_Geographic = [line.rstrip('\n') for line in f]
with open(Path+'StopWords/StopWords_Names.txt') as f:
    StopWords_Names = [line.rstrip('\n') for line in f]
with open(Path+'MasterDictionary/negative_words.txt','r') as f:
    negative_words = [line.rstrip('\n') for line in f]
with open(Path+'MasterDictionary/positive-words.txt') as f:
    positive_words = [line.rstrip('\n') for line in f]

import string
punc=string.punctuation

def listConcat(list):
        mila=""
        for x in list:
            mila=mila+x+' '
        return mila

def bucketTokenize(record1):
        record2=word_tokenize(record1)
        unique_list=list(set(record2))
        punc_removed=[i for i in unique_list if i not in punc]
        return punc_removed

def checkStopWords(list):
    filter1=[i for i in list if i not in StopWords_Auditor]
    filter2=[i for i in filter1 if i not in StopWords_Currencies]
    filter3=[i for i in filter2 if i not in StopWords_DatesandNumbers]
    filter4=[i for i in filter3 if i not in StopWords_Generic]
    filter5=[i for i in filter4 if i not in StopWords_GenericLong]
    filter6=[i for i in filter5 if i not in StopWords_Geographic]
    filter7=[i for i in filter6 if i not in StopWords_Names]
    return filter7

pCollectionAppended=[]
text_body_tokens=[]
final_text=[]

for x in pCollection:
    pCollectionAppended.append(listConcat(x))
    
text_body_extract=[a + '. ' + b for a, b in zip(titleCollection, pCollectionAppended)] #--this is a list of strings

for x in text_body_extract:
    text_body_tokens.append(bucketTokenize(x)) #--this is a list of lists, each element corresponds to respective URL
    
for x in text_body_tokens:
    final_text.append(checkStopWords(x)) #--this is a list of lists after stopwords


POSITIVE_VALUE=[]
NEGATIVE_VALUE=[]

for x in final_text:
    POSITIVE_VALUE.append(len([i for i in x if i in positive_words]))
    NEGATIVE_VALUE.append(len([i for i in x if i in negative_words]))

print(len(POSITIVE_VALUE))
print(len(NEGATIVE_VALUE))

POLARITY_SCORE=[]
SUBJECTIVITY_SCORE=[]

for i in range(len(POSITIVE_VALUE)):
    pol_score=(POSITIVE_VALUE[i]-NEGATIVE_VALUE[i])/(POSITIVE_VALUE[i]+NEGATIVE_VALUE[i] + 0.000001)
    POLARITY_SCORE.append(pol_score)

for i in range(len(POSITIVE_VALUE)):
    sub_score=(POSITIVE_VALUE[i]+NEGATIVE_VALUE[i])/(len(final_text) + 0.000001)
    SUBJECTIVITY_SCORE.append(sub_score)

# import sys
# !{sys.executable} -m pip install pyphen

from pyphen import Pyphen
p = Pyphen(lang='en_US')

COMPLEX_WORD_COUNT=[]

for x in final_text:
    count=0
    for i in x:
        if len(p.positions(i))+1>2:
            count+=1
    COMPLEX_WORD_COUNT.append(count)
SYLLABLE_COUNT_PER_WORD=COMPLEX_WORD_COUNT

AVERAGE_SENTENCE_LENGTH=[]

for x in text_body_extract:
    kim2=sent_tokenize(x)
    kim3=bucketTokenize(x)
    AVERAGE_SENTENCE_LENGTH.append(len(kim3)/len(kim2))
AVG_NUMBER_OF_WORDS_PER_SENTENCE=AVERAGE_SENTENCE_LENGTH

PERCENTAGE_OF_COMPLEX_WORDS=[]

for x in range(len(COMPLEX_WORD_COUNT)):
    PERCENTAGE_OF_COMPLEX_WORDS.append(COMPLEX_WORD_COUNT[x]/len(text_body_tokens[x]))

FOG_INDEX=[]

for x in range(len(COMPLEX_WORD_COUNT)):
    FOG_INDEX.append(0.4*(AVERAGE_SENTENCE_LENGTH[x] + PERCENTAGE_OF_COMPLEX_WORDS[x]))

WORD_COUNT=[]

for x in final_text:
    filtered_text=[i for i in x if i not in sw]
    WORD_COUNT.append(len(filtered_text))

# POLARITY_SCORE
# SUBJECTIVITY_SCORE
# COMPLEX_WORD_COUNT
# AVERAGE_SENTENCE_LENGTH
# PERCENTAGE_OF_COMPLEX_WORDS
# FOG_INDEX
# AVG_NUMBER_OF_WORDS_PER_SENTENCE
# WORD_COUNT

PERSONAL_PRONOUNS=[]

import re

for x in text_body_extract:
    res=re.findall('I|we|my|ours|us',x)
    res2=re.findall('US',x)
    PERSONAL_PRONOUNS.append(len(res)-len(res2))

AVG_WORD_LENGTH=[]

for x in text_body_extract:
    char_count=len(x) 
    words_count=len(x.strip().split(" "))
    AVG_WORD_LENGTH.append(char_count/words_count)

url_id=dataset['URL_ID'].tolist()   # 'URL_ID':url_id[:111],'URL':datalinks[:111] - used on original Input when blank urls are included
final_dataset=pd.DataFrame({'URL_ID':url_id,'URL':datalinks,'POSITIVE VALUE':POSITIVE_VALUE,'NEGATIVE VALUE':NEGATIVE_VALUE,'POLARITY SCORE':POLARITY_SCORE,'SUBJECTIVITY SCORE':SUBJECTIVITY_SCORE,'AVERAGE SENTENCE LENGTH':AVERAGE_SENTENCE_LENGTH,'PERCENTAGE OF COMPLEX WORDS':PERCENTAGE_OF_COMPLEX_WORDS,'FOG INDEX':FOG_INDEX,'AVG NUMBER OF WORDS PER SENTENCE':AVG_NUMBER_OF_WORDS_PER_SENTENCE,'COMPLEX WORD COUNT':COMPLEX_WORD_COUNT,'WORD COUNT':WORD_COUNT,'SYLLABLE PER WORD':SYLLABLE_COUNT_PER_WORD,'PERSONAL PRONOUNS':PERSONAL_PRONOUNS,'AVG WORD LENGTH':AVG_WORD_LENGTH})
final_dataset.head()

# final_dataset.to_csv('final_output_2.csv',index=False)

