import string
from os.path import abspath

file = open(abspath('/Users/[USER]/Documents/Language Process Topic Analysis - Lyrics/updated_ticket_data.csv'))
summaries = file.read()

def tokenize():
    if summaries is not None:
        words = summaries.lower().split()
        return words
    else:
        return None
        

def map_summaries(tokens):
    hash_map = {}

    if tokens is not None:
        for element in tokens:
            # Remove Punctuation
            word = element.replace(",","")
            word = word.replace(".","")
            word = word.replace("\\","")
            word = word.replace("/","")
            word = word.replace("-","")
            word = word.replace("?","")
            word = word.replace("(","")
            word = word.replace(")","")
            word = word.replace("'","")
            word = word.replace(":","")
            word = word.replace("!","")
            word = word.replace("\"","")

            # Word Exist?
            if word in hash_map:
                hash_map[word] = hash_map[word] + 1
            else:
                hash_map[word] = 1

        return hash_map
    else:
        return None


# Tokenize the summaries
words = tokenize()
word_list = ['the','have','like','with','would','need','view','do','how','all','in','to','is','for','not','add','a','of','an','by','when', 'and', 'are', '', 'when', 'where', 'why', 'who', 'on', 'up', 'from', 'can', 'that', 'be', 'does', 'cannot']

# Create a Hash Map (Dictionary)
map = map_summaries(words)

# Show Word Information
for word in map:
    # filter words
    if not word in word_list:
        if int(map[word]) > 199:
            result = '#: ' + str(map[word]) + '  Count for: [' + word + ']'
            print(result)
