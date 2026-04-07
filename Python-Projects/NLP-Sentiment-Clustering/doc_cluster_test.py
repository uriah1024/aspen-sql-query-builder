import string
import collections
import pandas as pd
import csv
import re
 
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
lem = WordNetLemmatizer()
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from pprint import pprint
 
 
def process_text(text, stem=True):
    """ Tokenize text and stem words removing punctuation """
    stop_words = stopwords.words('english')
    stop_words.extend(['would', 'doesn', 't', 'their', 'then', 'not', 'ma', 'here', 'other', 'won', 'up', 'weren', 'being', 'we', 'those', 'an', 'them', 'which', 'him', 'so', 'yourselves', 'what', 'own', 'has', 'should', 'above', 'in', 'myself', 'against', 'that', 'before', 't', 'just', 'into', 'about', 'most', 'd', 'where', 'our', 'or', 'such', 'ours', 'of', 'doesn', 'further', 'needn', 'now', 'some', 'too', 'hasn', 'more', 'the', 'yours', 'her', 'below', 'same', 'how', 'very', 'is', 'did', 'you', 'his', 'when', 'few', 'does', 'down', 'yourself', 'i', 'do', 'both', 'shan', 'have', 'itself', 'shouldn', 'through', 'themselves', 'o', 'didn', 've', 'm', 'off', 'out', 'but', 'and', 'doing', 'any', 'nor', 'over', 'had', 'because', 'himself', 'theirs', 'me', 'by', 'she', 'whom', 'hers', 're', 'hadn', 'who', 'he', 'my', 'if', 'will', 'are', 'why', 'from', 'am', 'with', 'been', 'its', 'ourselves', 'ain', 'couldn', 'a', 'aren', 'under', 'll', 'on', 'y', 'can', 'they', 'than', 'after', 'wouldn', 'each', 'once', 'mightn', 'for', 'this', 'these', 's', 'only', 'haven', 'having', 'all', 'don', 'it', 'there', 'until', 'again', 'to', 'while', 'be', 'no', 'during', 'herself', 'as', 'mustn', 'between', 'was', 'at', 'your', 'were', 'isn', 'wasn'])

    for word in words:
        if word not in stop_words:
            # Lemmatization reduces words to their base word considering context.
            # We can also tell it to focus on pos, if desired.
            text = lem.lemmatize(word)
    #text = text.translate(None, string.punctuation)
    tokens = word_tokenize(text)
    """
    if stem:
        stemmer = PorterStemmer()
        tokens = [stemmer.stem(t) for t in tokens]"""
 
    return tokens
 
 
def cluster_texts(texts, clusters=3):
    """ Transform texts to Tf-Idf coordinates and cluster texts using K-Means """
    stop_words = stopwords.words('english')
    stop_words.extend(['would', 'doesn', 't', 'their', 'then', 'not', 'ma', 'here', 'other', 'won', 'up', 'weren', 'being', 
    'we', 'those', 'an', 'them', 'which', 'him', 'so', 'yourselves', 'what', 'own', 'has', 'should', 'above', 'in', 'myself', 
    'against', 'that', 'before', 't', 'just', 'into', 'about', 'most', 'd', 'where', 'our', 'or', 'such', 'ours', 'of', 
    'doesn', 'further', 'needn', 'now', 'some', 'too', 'hasn', 'more', 'the', 'yours', 'her', 'below', 'same', 'how', 'very', 
    'is', 'did', 'you', 'his', 'when', 'few', 'does', 'down', 'yourself', 'i', 'do', 'both', 'shan', 'have', 'itself', 'shouldn', 
    'through', 'themselves', 'o', 'didn', 've', 'm', 'off', 'out', 'but', 'and', 'doing', 'any', 'nor', 'over', 'had', 'because', 
    'himself', 'theirs', 'me', 'by', 'she', 'whom', 'hers', 're', 'hadn', 'who', 'he', 'my', 'if', 'will', 'are', 'why', 'from', 
    'am', 'with', 'been', 'its', 'ourselves', 'ain', 'couldn', 'a', 'aren', 'under', 'll', 'on', 'y', 'can', 'they', 'than', 
    'after', 'wouldn', 'each', 'once', 'mightn', 'for', 'this', 'these', 's', 'only', 'haven', 'having', 'all', 'don', 'it', 
    'there', 'until', 'again', 'to', 'while', 'be', 'no', 'during', 'herself', 'as', 'mustn', 'between', 'was', 'at', 'your', 
    'were', 'isn', 'wasn'])

    vectorizer = TfidfVectorizer(tokenizer=process_text,
                                 stop_words=None,
                                 max_df=1.0,
                                 min_df=1,
                                 lowercase=True)
 
    tfidf_model = vectorizer.fit_transform(texts)
    km_model = KMeans(n_clusters=clusters)
    km_model.fit(tfidf_model)
 
    clustering = collections.defaultdict(list)
 
    for idx, label in enumerate(km_model.labels_):
        clustering[label].append(idx)
 
    return clustering
 
 
if __name__ == "__main__":
    # data frame
    pd.options.display.max_colwidth = 50
    df = pd.read_csv('/Users/[USER]/Documents/Language Process Topic Analysis - Lyrics/all_pando_data.csv',dtype=str,quoting=csv.QUOTE_ALL,quotechar='"',sep=',',names=["ID","Name","Name1","LogDate","AspenVN","Description","Summary","Status","Initials","FirstName","LastName","Module","SubModule","Priority","LogTime","CloseDate","Esc Feedback T2","Esc Feedback T3","Type","Product","SIF Error Code","RR- Confirmed","Name2","T2","T3"])
    df = df[pd.notnull(df)]
    #df = df.dropna()

    description = str(df[['Description']])

    letters_only = re.sub(r"[^a-zA-Z]",  # Search for all non-letters
                        " ",          # Replace all non-letters with spaces
                        description)     # Column and row to search

    words = letters_only.lower().split()

    articles = words
    clusters = cluster_texts(articles, 1)
    print(dict(clusters))
    print(articles)