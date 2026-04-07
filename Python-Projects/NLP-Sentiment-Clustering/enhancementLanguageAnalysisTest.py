import pandas as pd
import nltk
import matplotlib.pyplot as plt
import numpy as np
from nltk.corpus import stopwords
from os.path import abspath
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import re


# data frame
df = pd.read_csv('/Users/[USER]/Documents/Language Process Topic Analysis - Lyrics/8_2018_4_2019_pando_data_reports_only.csv', dtype=str)
df = df[pd.notnull(df)]
df.head(n=5)
pd.options.display.max_colwidth = 50

n_features = 1000
n_top_words = 10

letters_only = re.sub("[^a-zA-Z0-9]",  # Search for all non-letters
                     " ",          # Replace all non-letters with spaces
                     str(df[['Summary']]))     # Column and row to search  

words = letters_only.lower().split()
stop_words = stopwords.words('english')
stop_words.extend(['view', 'validation', 'trying', 'student', 'issue', 'see', 'one', 'aspen', 'need', 'middle', 'high'])
vectorizer = TfidfVectorizer(preprocessor=None, stop_words=stop_words, lowercase=True)
tfidf = vectorizer.fit_transform(df['Summary'])

nmf = NMF(n_components=10)
topic_values = nmf.fit_transform(tfidf)

with open("fy19_topics.txt", "w") as topics_file:
   for topic_num, topic in enumerate(nmf.components_): 
      message = "Topic #{}: ".format(topic_num + 1) 
      message += " ".join([vectorizer.get_feature_names()[i] 
         for i in topic.argsort()[:-11 :-1]])
      print(message, file=topics_file)


topic_labels = ['Grade Reports','Cluster 5 Performance','Daily Attendance','Tool Exceptions','Sync Performance','Build Issues', 'Grade Posting Errors', 'Staff Assignment Errors', 'OST', 'Staff-User issues']
df_topics = pd.DataFrame(topic_values, columns = topic_labels)
#print(df_topics)

report = df.groupby(['SubModule']).count().reset_index()
report = report.join(df_topics)
#print(report.head(n=5))

for label in topic_labels:
   report.loc[report[label] >= .01, label] = 1
   report.loc[report[label] < .01, label] = 0

report_topics = report.groupby(['SubModule']).sum().reset_index()
#print(report_topics)

#plt.figure(figsize=(20,10))
#for label in topic_labels:
#   plt.plot(report_topics['Module'],report_topics[label])
#   plt.legend()
#plt.show()

report_topics.to_csv(path_or_buf='fy19.csv')