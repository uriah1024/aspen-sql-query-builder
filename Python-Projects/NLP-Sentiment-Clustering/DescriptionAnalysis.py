import pandas as pd
import nltk
import csv
import sys
import matplotlib.pyplot as plt
import numpy as np
from nltk.corpus import stopwords
from os.path import abspath
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import re


# data frame
#df = pd.read_csv('/Users/[USER]/Documents/Language Process Topic Analysis - Lyrics/all_pando_data.csv',dtype=str,quoting=csv.QUOTE_ALL,quotechar='"',sep=',',names=["ID","Name","Name1","LogDate","AspenVN","Description","Summary","Status","Initials","FirstName","LastName","Module","SubModule","Priority","LogTime","CloseDate","Esc Feedback T2","Esc Feedback T3","Type","Product","SIF Error Code","RR- Confirmed","Name2","T2","T3"])
df = pd.read_csv('/Users/[USER]/Documents/Aspen/Pando_Ticket_Data/Scheduling/boston_scheduling.csv',dtype=str,quoting=csv.QUOTE_ALL,quotechar='"',sep=',',names=["ID","Name","Name1","LogDate","AspenVN","Description","Summary","Status","Initials","FirstName","LastName","Module","SubModule","Priority","LogTime","CloseDate","Esc Feedback T2","Esc Feedback T3","Type","Product","SIF Error Code","RR- Confirmed","Name2","T2","T3","Province"])
df = df[pd.notnull(df)]
df.head(n=5)
pd.options.display.max_colwidth = 50

n_features = 1000
n_top_words = 10

letters_only = re.sub("[^a-zA-Z0-9]",  # Search for all non-letters
                     " ",          # Replace all non-letters with spaces
                     str(df[['Description']]))     # Column and row to search  

words = letters_only.lower().split()
stop_words = stopwords.words('english')
stop_words.extend(['the','have','like','with','would','need','view','do','how','all','in','to','is','for','not','add','a','of','an','by','when', 'and', 'are', '', 'when', 'where', 'why', 'who', 'on', 'up', 'from', 'can', 'that', 'be', 'does', 'cannot'])
vectorizer = TfidfVectorizer(preprocessor=None, stop_words=stop_words, max_features=n_features, lowercase=False)
tfidf = vectorizer.fit_transform(df['Description'])

nmf = NMF(n_components=10)
topic_values = nmf.fit_transform(tfidf)

for topic_num, topic in enumerate(nmf.components_): 
    message = "Topic #{}: ".format(topic_num + 1) 
    message += " ".join([vectorizer.get_feature_names()[i] 
      for i in topic.argsort()[:-11 :-1]])
    print(message)

topic_labels = ['Scheduling','Report Cards','SIMS Error 1','Validations','Cross Validations','Printing', 'SIF Exceptions', 'SIF School Days', 'Daily Attendance', 'IEP Form']
df_topics = pd.DataFrame(topic_values, columns = topic_labels)
print(df_topics)

report = df.groupby(['Type', 'Module']).count().reset_index()
report = report.join(df_topics)
print(report.head(n=5))

for label in topic_labels:
   report.loc[report[label] >= .01, label] = 1
   report.loc[report[label] < .01, label] = 0

report_topics = report.groupby(['Type']).sum().reset_index()
print(report_topics)

#plt.figure(figsize=(20,10))
#for label in topic_labels:
#   plt.plot(report_topics['Module'],report_topics[label])
#   plt.legend()
#plt.show()

#report_topics.to_csv(path_or_buf='type.csv')