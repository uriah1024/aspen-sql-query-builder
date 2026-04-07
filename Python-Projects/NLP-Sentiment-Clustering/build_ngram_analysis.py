import string
from string import digits
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer

import nltk
from nltk import sent_tokenize, word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords

print('Running program')

testText = ['"Same scenarios except for rotation. Not rotated; AX 052714 UnrotateRotated; AY 052714 w/ X CoursesBuild View\, AY 052714 w/ X Courses > Workspace > Feedback21 fatal errorsFirst 20 errors are;  	Field Schedule > student is not a valid StudentLast one; Similar validation for schedule data has happened for more than 20 times. The message is: Field Schedule > student is not a valid Student (record 1234\, G(M-T\,R-F)).. Please check all records in schedule data for the similar issue."'
            ,'School; Maria Weston Chapman Middle SchoolScenario; 2014-2015 Chapman Scenario1 Build View\, Workspace > Feedback1 fatal errorField Schedule > student is not a valid Student (record FY\, E(1-6)).'
            ,'"""Field Schedule > student is not a valid Student 4A-4B(G)"" in load validation:George ran his load validation\, but received a few fatal errors: Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 1\, 3A-3B(B)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 2\, 4A-4B(G)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 2\, 4A-4B(B)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 1\, 3A-3B(G)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 1\, 4A-4B(B-G)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 2\, 1A-1B(B-G)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 1\, 2A-2B(B-G)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 1\, 1A-1B(B-G)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 2\, 3A-3B(B-G)). 	6/15/2015 9:32 PM 	N		Load 	Schedule 	Fatal 	Field Schedule > student is not a valid Student (record 2\, 2A-2B(B-G)). 	6/15/2015 9:32 PM 	N"'
            ]


# data frame
pd.options.display.max_colwidth = 50
#df = pd.read_csv('/Users/[USER]/Documents/Language Process Topic Analysis - Lyrics/all_pando_data.csv',dtype=str,quoting=csv.QUOTE_ALL,quotechar='"',sep=',',names=["ID","Name","Name1","LogDate","AspenVN","Description","Summary","Status","Initials","FirstName","LastName","Module","SubModule","Priority","LogTime","CloseDate","Esc Feedback T2","Esc Feedback T3","Type","Product","SIF Error Code","RR- Confirmed","Name2","T2","T3"])
#df = pd.read_csv('/Users/[USER]]/Documents/Aspen/Pando_Ticket_Data/Scheduling/bsmv_scheduling_2015_2019.csv',dtype=str,quoting=csv.QUOTE_ALL,quotechar='"',sep=',',names=["ID","Name","Name1","LogDate","AspenVN","Description","Summary","Status","Initials","FirstName","LastName","Module","SubModule","Priority","LogTime","CloseDate","Esc Feedback T2","Esc Feedback T3","Type","Product","SIF Error Code","RR- Confirmed","Name2","T2","T3","Province"])
df = pd.read_csv('/Users/[USER]/Documents/Aspen/Pando_Ticket_Data/Build_14_19.csv',
                 dtype=str, encoding='utf-8')
#df = df[pd.notnull(df)]
#df = df.dropna()
# df.astype(str)
description = df['Issue Description']

stop_words = nltk.corpus.stopwords.words('english')
"""stop_words.extend(['would', 'doesn', 't', 'their', 'then', 'ma', 'here', 'other', 'won', 'up', 'weren', 'being', 
    'we', 'those', 'an', 'them', 'which', 'him', 'so', 'yourselves', 'what', 'own', 'has', 'should', 'above', 'in', 'myself', 
    'against', 'that', 'before', 't', 'just', 'into', 'about', 'most', 'd', 'where', 'our', 'or', 'such', 'ours', 'of', 
    'doesn', 'further', 'needn', 'now', 'some', 'too', 'hasn', 'more', 'the', 'yours', 'her', 'below', 'same', 'how', 'very', 
    'is', 'did', 'you', 'his', 'when', 'few', 'does', 'down', 'yourself', 'do', 'both', 'shan', 'have', 'itself', 'shouldn', 
    'through', 'themselves', 'o', 'didn', 've', 'm', 'off', 'out', 'but', 'and', 'doing', 'any', 'nor', 'over', 'had', 'because', 
    'himself', 'theirs', 'me', 'by', 'she', 'whom', 'hers', 're', 'hadn', 'who', 'he', 'my', 'if', 'will', 'are', 'why', 'from', 
    'am', 'with', 'been', 'its', 'ourselves', 'ain', 'couldn', 'a', 'aren', 'under', 'll', 'on', 'can', 'they', 'than', 
    'after', 'wouldn', 'each', 'once', 'mightn', 'for', 'this', 'these', 's', 'only', 'haven', 'having', 'all', 'don', 'it', 
    'there', 'until', 'again', 'to', 'while', 'be', 'no', 'during', 'herself', 'as', 'mustn', 'between', 'was', 'at', 'your', 
    'were', 'isn', 'wasn'])"""


def removeDigits(list):
    remove_digits = str.maketrans('', '', digits)
    list = [i.translate(remove_digits) for i in list]
    return list


preprocess = True
tokenizeSentences = False
if preprocess:
    clean_data = []
    #text = str(text)
    print(f"Raw input: {testText}")
    for x in testText:
        # split into words by white space
        # Preprocess stopwords
        useStops = True
        if useStops:
            words = [word for word in str(x).split() if word not in stop_words]
        else:
            words = str(x).split()
        
        if tokenizeSentences:
            softProcess = re.sub(r'\[[.a-zA-Z]*\]', ' ', str(words))
            #softProcess = re.sub(r'\s+', ' ', softProcess)
            sent_token_text = sent_tokenize(str(softProcess))
            words = sent_token_text
        else:
            # remove punctuation from each word
            hardProcess = [w.translate(str.maketrans('', '', string.punctuation)) for w in words]
            word_token_text = word_tokenize(str(clean_data))
            words = hardProcess
            
        new_text = removeDigits(words)
        # remove empty strings created by digit removal
        # lowercase is included
        new_text = [x.lower() for x in new_text if x]
        if new_text:
            new_text = ' '.join(new_text)
        clean_data.append(new_text)
    print(clean_data)


"""if tokenizeSentences:
    sent_tokenize(str(clean_data))
    s_new = []
    for sent in (clean_data[:][0]):
        s_token = sent_tokenize(str(sent))
        if s_token:
            s_new.append(s_token)"""


"""if tokenizeWords:
    word_tokenize(str(clean_data))
    w_new = []
    for w in (clean_data):
        w_token = word_tokenize(str(w))
        if w_token != '':
            w_new.append(w_token)"""


snowball = SnowballStemmer(language='english')


stemData = False
if stemData:
    stem_new = []
    stem_words = [snowball.stem(str(clean_data).lower()) for word in words]
    stem_new.append(stem_words)


lemmatizer = WordNetLemmatizer()


lemData = False
if lemData:
    lem_new = []
    lem_words = [lemmatizer.lemmatize(clean_data) for word in words]
    lem_new.append(lem_words)


print(clean_data)


#test = description
#clean_test = preprocess(test)  # removes punctuation, see above
#df[['Clean_Description']] = description.apply(preprocess)
#print(df['Clean_Description'])
#clean_words = tokenization_w(df['Clean_Description']) # word tokenization
#clean_words = pd.DataFrame(df[['Clean_Description']]).apply(tokenization_w)
#clean_sent = tokenization_s(df['Clean_Description'])
#stem_test = stemming(clean_words) # stemming similar words
#print("Preprocessed Text: \n")
#print(clean_words)
#print("Preprocessed Sentences: \n")
#print(clean_sent)

#lemtest = lemmatization(clean_words)
# print(lemtest)