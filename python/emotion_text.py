#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
eb = pd.read_csv("data/emobank.csv", index_col=0)

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

'''
Sources:
https://www.dataquest.io/blog/natural-language-processing-with-python/
https://heartbeat.fritz.ai/guide-to-saving-hosting-your-first-machine-learning-model-cdf69729e85d
'''

import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.linear_model import Ridge

# split into train, validate and test splits
eb_train = eb.loc[(eb.split == 'train')]
eb_dev = eb.loc[(eb.split == 'dev')]
eb_test = eb.loc[(eb.split == 'test')]
eb_training = pd.concat([eb_train, eb_dev])

'''
Clean, lemmatize
'''

def clean_lemma(text):
    
    corpus = []
    
    for i in range(0, text.shape[0]):
        review = re.sub('[^a-zA-Z]', ' ', text[i])
        review = review.lower()
        review = review.split()
        lemmatizer = WordNetLemmatizer()
        review = [lemmatizer.lemmatize(word) for word in review if not word in set(stopwords.words('english'))]
        review = ' '.join(review)
        corpus.append(review)
    
    return corpus

data_training = clean_lemma(eb_training['text'])
data_test = clean_lemma(eb_test['text'])


'''
Feature Selection
'''
# From:
# https://heartbeat.fritz.ai/guide-to-saving-hosting-your-first-machine-learning-model-cdf69729e85d
from sklearn.feature_extraction.text import TfidfVectorizer
tfidfVectorizer = TfidfVectorizer(max_features=1000,
                                  lowercase=True,
                                  stop_words="english",
                                  ngram_range=(1,2))

X = tfidfVectorizer.fit_transform(data_training).toarray()
x = tfidfVectorizer.transform(data_test).toarray()

'''
Save vectorizer for online deployment
'''

from sklearn.externals import joblib
joblib.dump(tfidfVectorizer, 'vect_obj.pkl')


'''
Make Predictions
'''

# import random

# setup train and dev splits
data_train = X[:8062, :]
data_dev = X[8062:, :]
data_test = x
data_training = X


# Valence Labels
lab_train_V = eb_train['V']
lab_dev_V = eb_dev['V']
lab_training_V = eb_training['V']
lab_test_V = eb_test['V']

# Activation Labels
lab_train_A = eb_train['A']
lab_dev_A = eb_dev['A']
lab_training_A = eb_training['A']
lab_test_A = eb_test['A']

# Dominance Labels
lab_train_D = eb_train['D']
lab_dev_D = eb_dev['D']
lab_training_D = eb_training['D']
lab_test_D = eb_test['D']

data_train = np.nan_to_num(data_train)
data_dev = np.nan_to_num(data_dev)
data_test = np.nan_to_num(data_test)
data_training = np.nan_to_num(data_training)


'''
VALENCE
'''
# Run the regression and generate predictions for the dev set
reg_V = Ridge(alpha=.1)
reg_V.fit(data_train, lab_train_V)
predictions_V = reg_V.predict(data_dev)
# Print prediction error and plot distribution - dev
print_preds_errors_plots(predictions_V, lab_dev_V, "VALENCE")

# Test set
reg_V = Ridge(alpha=.1)
reg_V.fit(data_training, lab_training_V)
predictions_V = reg_V.predict(data_test)
# Print prediction error and plot distribution - test
print_preds_errors_plots(predictions_V, lab_test_V, "VALENCE")


'''
ACTIVATION
'''
# Run the regression and generate predictions for the dev set
reg_A = Ridge(alpha=.1)
reg_A.fit(data_train, lab_train_A)
predictions_A = reg_A.predict(data_dev)
# Print prediction error and plot distribution
print_preds_errors_plots(predictions_A, lab_dev_A, "ACTIVATION")

# Test set
reg_A = Ridge(alpha=.1)
reg_A.fit(data_training, lab_training_A)
predictions_A = reg_A.predict(data_test)
# Print prediction error and plot distribution - test
print_preds_errors_plots(predictions_A, lab_test_A, "ACTIVATION")


'''
DOMINANCE
'''
# Run the regression and generate predictions for the dev set
reg_D = Ridge(alpha=.1)
reg_D.fit(data_train, lab_train_D)
predictions_D = reg_D.predict(data_dev)
# Print prediction error and plot distribution
print_preds_errors_plots(predictions_D, lab_dev_D, "DOMINANCE")

# Test set
reg_D = Ridge(alpha=.1)
reg_D.fit(data_training, lab_training_D)
predictions_D = reg_D.predict(data_test)
# Print prediction error and plot distribution
print_preds_errors_plots(predictions_D, lab_test_D, "DOMINANCE")


'''
SAVE MODELS
'''

joblib.dump(reg_V, 'model_text_valence.pkl')
joblib.dump(reg_A, 'model_text_activation.pkl')
joblib.dump(reg_D, 'model_text_dominance.pkl')

# =============================================================================
# from joblib import dump, load
# dump(reg_V, 'model_text_valence.joblib')
# dump(reg_A, 'model_text_activation.joblib')
# dump(reg_D, 'model_text_dominance.joblib')
# =============================================================================

'''
LOAD MODELS
'''

# =============================================================================
# reg_V = load('model_text_valence.joblib')
# reg_A = load('model_text_activation.joblib')
# reg_D = load('model_text_dominance.joblib')
# =============================================================================

'''
Testing a random sentence
'''

testing_input = "I felt terrible and I didn't know what to do"
testing_input = "He should be ashamed of himself. I wanted to strangle him."
testing_input = pd.Series(testing_input)

'''
Load model and vectorizer
'''

new_load_cf = joblib.load('model_text_valence.pkl')
new_load_vect = joblib.load('vect_obj.pkl')

# Calculate meta features for data input
# Apply each function and put the results in a list
test_input_columns = []
for func in transform_functions:
    test_input_columns.append(testing_input.apply(func))
    
# convert the meta features into an numpy array
test_input_meta = np.asarray(test_input_columns).T

# Convert the input test to a vector
string_matrix = new_load_vect.transform(testing_input)

# Use the same set of features as learned in our model
# 'top_words' has been declared in a global scope previously
# But it may be scoped for valence and not the other two dimensions - check
chi_test_string = string_matrix[:, top_words[0]]

# collect all the features in one object
new_input_features = np.hstack([test_input_meta, chi_test_string.todense()])

print("VALENCE SCORE PREDICTION: ", reg_V.predict(new_input_features))
print("ACTIVATION SCORE PREDICTION: ", reg_A.predict(new_input_features))
print("DOMINANCE SCORE PREDICTION: ", reg_D.predict(new_input_features))

'''
NEXT STEPS:
    Implement pipeline:
    https://scikit-learn.org/dev/tutorial/text_analytics/working_with_text_data.html
    Construct 'top_words' for activation and dominance dimensions
    Implement online:
    https://towardsdatascience.com/develop-a-nlp-model-in-python-deploy-it-with-flask-step-by-step-744f3bdd7776
    Try wordtovec (Domenico)
    Try linear regression
    Try Naive Bayes
    Try SVM
    Try Random Forest Regressor
    Try different dimension reduction methods
    Find more data
    Deep Learning models
'''

# =============================================================================
# from collections import Counter
# 
# headlines = eb['text'][:10]
# 
# # find all the unique words in the subset
# unique_words = list(set(" ".join(headlines).split(" ")))
# 
# def make_matrix(hlines, vocab):
#     matrix = []
#     for headline in hlines:
#         # Count each word in the headline and make a dictionary
#         counter = Counter(headline)
#         # Turn the dictionary into a matrix row using the vocab
#         row = [counter.get(w, 0) for w in vocab]
#         matrix.append(row)
#     df = pd.DataFrame(matrix)
#     df.columns = unique_words
#     return df
# 
# print(make_matrix(headlines, unique_words))
# 
# 
# import re
# 
# # Lowercase, then replace any non-letter, space or digit character in the headlines
# #new_headlines = [re.sub(r'[^wsd]','',h.lower()) for h in headlines]
# 
# new_headlines = [re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
#                         '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', h.lower()) for h in headlines]
# new_headlines = [re.sub("(@[A-Za-z0-9_]+)","", h.lower()) for h in headlines]
# new_headlines = [re.sub(r'[,@\'?\.$%_:\-"’“”]', "", h.lower(), flags=re.I) for h in headlines]
# 
# # Replace sequences of whitespace with a space character
# new_headlines = [re.sub("\s+", " ", h) for h in new_headlines]
# 
# unique_words = list(set(" ".join(new_headlines).split(" ")))
# # We've reduced the number of columns in the matrix a little
# print(make_matrix(new_headlines, unique_words))
# =============================================================================

# =============================================================================
# # Create a version of Valence to binary so we can use chi-squared
# val_binary = eb_training['V'].copy(deep=True)
# val_mean = val_binary.mean()
# val_binary[val_binary < val_mean] = 0
# val_binary[(val_mean > 0) & (val_binary > val_mean)] = 1
# 
# # applying matrix to all training instances
# training_matrix = vectorizer.fit_transform(eb_training['text'])
# print(training_matrix.shape)
# 
# # Find the 1000 most informative columns
# selector = SelectKBest(chi2, k=1000)
# selector.fit(training_matrix, val_binary)
# top_words = selector.get_support().nonzero()
# 
# # Pick only the most informative columns in the data
# chi_matrix = training_matrix[:, top_words[0]]
# 
# 
# 
# # collect all the features in one object
# features = np.hstack([meta, chi_matrix.todense()])
# =============================================================================

from scipy.stats import pearsonr, spearmanr

def print_preds_errors_plots(preds, labels, plot_title):
    '''
    Calculate errors and correlations. Run a plot.
    '''
    # comparing predicted with actual
    print('Prediction error: ', sum(abs(preds - labels)) / len(preds))
    
    # average of all Valence ratings
    average_all_measure = sum(labels)/len(labels)
    print('Mean error: ', sum(abs(average_all_measure - labels)) / len(preds))
    
    # calculate pearson's correlation
    corr, _ = pearsonr(preds, labels)
    print('Pearsons correlation: %.3f' % corr)
    
    # calculate spearman's correlation
    corr, _ = spearmanr(preds, labels)
    print('Spearmans correlation: %.3f' % corr)
    
    #sns.distplot(preds)
    sns.set_style("whitegrid")
    plt.figure(figsize=(12,12))
    fig = sns.regplot(x=preds, y=labels, label=plot_title)
    #fig.set_axis_labels(xlabel='Predictions', ylabel='Actual')
    
    plt.title(plot_title)
    plt.xlabel('Predictions')
    plt.ylabel('Actual')
    plt.xlim((0.5, 4.5))
    plt.ylim((0.5, 4.5))
    plt.show(fig)
