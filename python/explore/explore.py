#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
eb = pd.read_csv("data/emobank.csv", index_col=0)

print(eb.shape)
test = eb.head()

# NLP module
import nltk
# https://www.guru99.com/tokenize-words-sentences-nltk.html
from nltk.tokenize import word_tokenize # word tokenize
# from nltk.tokenize import sent_tokenize # sentence tokenize

'''
# Tweets example https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk
'''
# To tokenise text - this is a pretrained model
nltk.download('punkt')

# text normalisation (converting a word to its canonical form - ran, runs, 
# running are forms of 'run')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer

all_text = eb['text']
sample_text = all_text[0:100]

text_tokens = []

'''
Tokenize text
'''

for i in range(0, len(all_text)):
    tokenized = word_tokenize(all_text[i])
    text_tokens.append(tokenized)

'''
Normalise text
# From: https://www.digitalocean.com/community/tutorials/how-to-perform-sentiment-analysis-in-python-3-using-the-natural-language-toolkit-nltk
'''

# tags as noun, verb whatever...
print(pos_tag(text_tokens[0]))

def lemmatize_sentence(tokens):
    '''
    The function lemmatize_sentence first gets the position tag of each token
    of a tweet. Within the if statement, if the tag starts with NN, the token
    is assigned as a noun. Similarly, if the tag starts with VB, the token is
    assigned as a verb.
    '''
    lemmatizer = WordNetLemmatizer()
    lemmatized_sentence = []
    for word, tag in pos_tag(tokens):
        if tag.startswith('NN'):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatized_sentence.append(lemmatizer.lemmatize(word, pos))
    return lemmatized_sentence

print(lemmatize_sentence(text_tokens[0]))


'''
Removing noise from the data
Hyperlinks, twitter handles, punctuation
'''

import re, string
from nltk.corpus import stopwords
stop_words = stopwords.words('english')


def remove_noise(tweet_tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

print(remove_noise(text_tokens[0], stop_words))

'''
Applying normalisation and cleaning to all text, store in object
'''

cleaned_text_tokens = []

for tokens in text_tokens:
    cleaned_text_tokens.append(remove_noise(tokens, stop_words))

# compare before with after
print(text_tokens[2510])
print(cleaned_text_tokens[2510])

'''
Determining Word Density
'''

# not sensible to do this for one entry, so lets look at all...

def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

all_pos_words = get_all_words(cleaned_text_tokens)

from nltk import FreqDist

freq_dist_pos = FreqDist(all_pos_words)
print(freq_dist_pos.most_common(10))

'''
Preparing data for the model
'''

