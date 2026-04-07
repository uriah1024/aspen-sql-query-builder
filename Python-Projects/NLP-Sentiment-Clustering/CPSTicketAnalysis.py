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
df = pd.read_csv('/Users/[USER]/Documents/Aspen/Chicago_Public_Schools/CPS_Administration_Health.csv', dtype=str)
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
stop_words.extend(['view', 'validation', 'trying', 'student', 'issue', 'see', 'one', 'aspen', 'need', 'middle', 'high'])
vectorizer = TfidfVectorizer(preprocessor=None, stop_words=stop_words, lowercase=True)
tfidf = vectorizer.fit_transform(df['Description'])

nmf = NMF(n_components=5)
topic_values = nmf.fit_transform(tfidf)

with open("cps_ticket_topics.txt", "w") as topics_file:
   for topic_num, topic in enumerate(nmf.components_): 
      message = "Topic #{}: ".format(topic_num + 1) 
      message += " ".join([vectorizer.get_feature_names()[i] 
         for i in topic.argsort()[:-16 :-1]])
      print(message, file=topics_file)


topic_labels = ['1','2','3','4','5']
df_topics = pd.DataFrame(topic_values, columns = topic_labels)
#print(df_topics)

report = df.groupby(['Assignment group']).count().reset_index()
report = report.join(df_topics)
#print(report.head(n=5))

for label in topic_labels:
   report.loc[report[label] >= .01, label] = 1
   report.loc[report[label] < .01, label] = 0

report_topics = report.groupby(['Assignment group']).sum().reset_index()
#print(report_topics)

#plt.figure(figsize=(20,10))
#for label in topic_labels:
#   plt.plot(report_topics['Module'],report_topics[label])
#   plt.legend()
#plt.show()

report_topics.to_csv(path_or_buf='cpsTickets.csv')