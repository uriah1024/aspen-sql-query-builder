import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import re
from nltk.corpus import stopwords
import csv
from nltk.probability import FreqDist
from nltk.stem.wordnet import WordNetLemmatizer
lem = WordNetLemmatizer()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.metrics import accuracy_score

from nltk.stem.porter import PorterStemmer
stem = PorterStemmer()

from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import RegexpTokenizer

print('Running program')

# data frame
pd.options.display.max_colwidth = 50
#df = pd.read_csv('/Users/[USER]/Documents/Language Process Topic Analysis - Lyrics/all_pando_data.csv',dtype=str,quoting=csv.QUOTE_ALL,quotechar='"',sep=',',names=["ID","Name","Name1","LogDate","AspenVN","Description","Summary","Status","Initials","FirstName","LastName","Module","SubModule","Priority","LogTime","CloseDate","Esc Feedback T2","Esc Feedback T3","Type","Product","SIF Error Code","RR- Confirmed","Name2","T2","T3"])
#df = pd.read_csv('/Users/[USER]/Documents/Aspen/Pando_Ticket_Data/Scheduling/bsmv_scheduling_2015_2019.csv',dtype=str,quoting=csv.QUOTE_ALL,quotechar='"',sep=',',names=["ID","Name","Name1","LogDate","AspenVN","Description","Summary","Status","Initials","FirstName","LastName","Module","SubModule","Priority","LogTime","CloseDate","Esc Feedback T2","Esc Feedback T3","Type","Product","SIF Error Code","RR- Confirmed","Name2","T2","T3","Province"])
#df = pd.read_csv('/Users/[USER]/Documents/Aspen/Pando_Ticket_Data/build_14_19.csv',dtype=str,quoting=csv.QUOTE_ALL,quotechar='"',sep=',',names=["ID", "Priority", "Due Date", "Open Date", "Open Time", "Close Date", "Close Time", "Type", "Client", "Hosted Cluster", "Contact", "Status", "Escalated", "PTE", "Re-opened", "Logger", "Logger Tier", "Province", "Module", "Sub Module", "Version", "Responsible", "Resp Tier", "T2", "T3", "Issue Description", "Activity Description"])
df = df[pd.notnull(df)]
df = df.dropna(how="all")
#df.head()

description = str(df[['Description']])
#letters_only = re.sub(r'[\W_]+', ' ', description)

letters_only = re.sub(r"[^a-zA-Z]",  # Search for all non-letters
                    " ",          # Replace all non-letters with spaces
                    description)     # Column and row to search

words = letters_only.lower().split()
stop_words = stopwords.words('english')
stop_words.extend(['phone', 'discussed', 'hi', 'would', 'doesn', 't', 'their', 'then', 'not', 'ma', 'here', 'other', 'won', 'up', 'weren', 'being', 'we', 'those', 'an', 'them', 'which', 'him', 'so', 'yourselves', 'what', 'own', 'has', 'should', 'above', 'in', 'myself', 'against', 'that', 'before', 't', 'just', 'into', 'about', 'most', 'd', 'where', 'our', 'or', 'such', 'ours', 'of', 'doesn', 'further', 'needn', 'now', 'some', 'too', 'hasn', 'more', 'the', 'yours', 'her', 'below', 'same', 'how', 'very', 'is', 'did', 'you', 'his', 'when', 'few', 'does', 'down', 'yourself', 'i', 'do', 'both', 'shan', 'have', 'itself', 'shouldn', 'through', 'themselves', 'o', 'didn', 've', 'm', 'off', 'out', 'but', 'and', 'doing', 'any', 'nor', 'over', 'had', 'because', 'himself', 'theirs', 'me', 'by', 'she', 'whom', 'hers', 're', 'hadn', 'who', 'he', 'my', 'if', 'will', 'are', 'why', 'from', 'am', 'with', 'been', 'its', 'ourselves', 'ain', 'couldn', 'a', 'aren', 'under', 'll', 'on', 'y', 'can', 'they', 'than', 'after', 'wouldn', 'each', 'once', 'mightn', 'for', 'this', 'these', 's', 'only', 'haven', 'having', 'all', 'don', 'it', 'there', 'until', 'again', 'to', 'while', 'be', 'no', 'during', 'herself', 'as', 'mustn', 'between', 'was', 'at', 'your', 'were', 'isn', 'wasn'])

for word in words:
    if word not in stop_words:
        # Lemmatization reduces words to their base word considering context.
        # We can also tell it to focus on pos, if desired.
        print("Lemmatized Word:",lem.lemmatize(word))


vectorizer = TfidfVectorizer(stop_words=stop_words)
X = vectorizer.fit_transform(words)

true_k = 5
model = KMeans(n_clusters=true_k, init='k-means++', max_iter=5000, n_init=10)
model.fit(X)

print("Top terms per cluster:")
order_centroids = model.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names()
print(terms)
for i in range(true_k):
    print("Cluster %d:" % i),
    for ind in order_centroids[i, :10]:
        print(' %s' % terms[ind]),
    print

print("\nPrediction")

Y = vectorizer.transform(words)
prediction = model.predict(Y)
print(prediction)

token = RegexpTokenizer(r'[a-zA-Z0-9]+')
cv = CountVectorizer(lowercase=True,stop_words=stop_words,ngram_range = (1,1),tokenizer = token.tokenize)
text_counts= cv.fit(words)
bow = text_counts.transform(words)
sum_words = bow.sum(axis=0)
words_freq = [(word, sum_words[0, idx]) for word, idx in     text_counts.vocabulary_.items()]
words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
print(words_freq[:20])

#print(f'Tokenized sentence: {words}')
#print(f'Filtered sentence: {filtered_sent}')


print('Program complete')