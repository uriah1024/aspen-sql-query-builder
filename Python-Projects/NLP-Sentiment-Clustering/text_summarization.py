from tika import parser
import re
import nltk
import heapq

# Get the text data from the pdf data source.
raw = parser.from_file('C:/Users/[USER]/Downloads/Having Tough Conversations 110519.pdf')
# print(raw['content'])

article_text = raw['content']

# Removing Square Brackets and Extra Spaces
"""
The first preprocessing step is to remove references from the article. 
The following script removes the square brackets and replaces the resulting multiple spaces by a single space.
The article_text object contains text without brackets. However, we do not want to remove anything else from 
the article since this is the original article. We will not remove other numbers, punctuation marks and 
special characters from this text since we will use this text to create summaries and weighted word frequencies 
will be replaced.
"""
article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
article_text = re.sub(r'\s+', ' ', article_text)

# Removing special characters and digits
"""
To clean the text and calculate weighted frequences, we will create another object.
Now we have two objects article_text, which contains the original article and formatted_article_text 
which contains the formatted article. We will use formatted_article_text to create weighted frequency 
histograms for the words and will replace these weighted frequencies with the words in the article_text object.
"""
formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

# print(article_text)
# print(formatted_article_text)

# Perform sentence tokenization
"""
At this point we have preprocessed the data. Next, we need to tokenize the article into sentences. 
We will use the 'article_text' object for tokenizing the article to sentence since it contains full stops. 
The 'formatted_article_text' does not contain any punctuation and therefore cannot be converted into 
sentences using the full stop as a parameter.
"""
sentence_list = nltk.sent_tokenize(article_text)
# print(sentence_list)

# Find Weighted Frequency of Occurrence
"""
To find the frequency of occurrence of each word, we use the 'formatted_article_text' variable. 
We used this variable to find the frequency of occurrence since it doesn't contain punctuation, 
digits, or other special characters.

We first store all the English stop words from the nltk library into a stopwords variable. 
Next, we loop through all the sentences and then corresponding words to first check if they 
are stop words. If not, we proceed to check whether the words exist in word_frequency dictionary 
i.e. word_frequencies, or not. If the word is encountered for the first time, it is added to the 
dictionary as a key and its value is set to 1. Otherwise, if the word previously exists in the 
dictionary, its value is simply updated by 1.
"""
stopwords = nltk.corpus.stopwords.words('english')

word_frequencies = {}
for word in nltk.word_tokenize(formatted_article_text):
    if word not in stopwords:
        if word not in word_frequencies.keys():
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1

# print(word_frequencies)

"""
Finally, to find the weighted frequency, we can simply divide the number of occurences of all the 
words by the frequency of the most occurring word, as shown below:
"""
maximum_frequency = max(word_frequencies.values())
# print (maximum_frequency)

for word in word_frequencies.keys():
    word_frequencies[word] = (word_frequencies[word]/maximum_frequency)
    # print(word_frequencies)


# Calculating Sentence Scores
"""
We have now calculated the weighted frequencies for all the words. Now is the time to calculate the 
scores for each sentence by adding weighted frequencies of the words that occur in that particular sentence.

We first create an empty 'sentence_scores' dictionary. The keys of this dictionary will be the sentences 
themselves and the values will be the corresponding scores of the sentences. Next, we loop through each 
sentence in the 'sentence_list' and tokenize the sentence into words.

We then check if the word exists in the 'word_frequencies' dictionary. This check is performed since we created 
the 'sentence_list' list from the 'article_text' object; on the other hand, the word frequencies were calculated 
using the 'formatted_article_text' object, which doesn't contain any stop words, numbers, etc.

We do not want very long sentences in the summary, therefore, we calculate the score for only sentences with 
less than 30 words (although you can tweak this parameter for your own use-case). Next, we check whether the 
sentence exists in the 'sentence_scores' dictionary or not. If the sentence doesn't exist, we add it to the 
'sentence_scores' dictionary as a key and assign it the weighted frequency of the first word in the sentence, 
as its value. On the contrary, if the sentence exists in the dictionary, we simply add the weighted frequency 
of the word to the existing value.
"""
sentence_scores = {}
for sent in sentence_list:
    for word in nltk.word_tokenize(sent.lower()):
        if word in word_frequencies.keys():
            #if len(sent.split(' ')) < 30:
            if sent not in sentence_scores.keys():
                sentence_scores[sent] = word_frequencies[word]
            else:
                sentence_scores[sent] += word_frequencies[word]

summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
summary_sentences = sorted(summary_sentences, key=lambda word: word[1])
summary_sentences = sorted(summary_sentences, key=lambda word: word[0])

print(sentence_scores)

summary = ' '.join(summary_sentences.sort())
print(summary)