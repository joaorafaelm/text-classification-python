# -*- coding: utf8 -*-
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_val_predict
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import wordpunct_tokenize
from nltk.corpus import wordnet as wn
from functools import lru_cache
from nltk.tag.perceptron import PerceptronTagger
import matplotlib.pyplot as plt
import seaborn as sn

# Load data
dataset = json.load(open('products.json', encoding='utf-8'))

# Initiate lemmatizer
wnl = WordNetLemmatizer()

# Load tagger pickle
tagger = PerceptronTagger()

# Lookup if tag is noun, verb, adverb or an adjective
tags = {'N': wn.NOUN, 'V': wn.VERB, 'R': wn.ADV, 'J': wn.ADJ}

# Memoization of POS tagging and Lemmatizer
lemmatize_mem = lru_cache(maxsize=10000)(wnl.lemmatize)
tagger_mem = lru_cache(maxsize=10000)(tagger.tag)


# POS tag sentences and lemmatize each word
def tokenizer(text):
    for token in wordpunct_tokenize(text):
        if token not in ENGLISH_STOP_WORDS:
            tag = tagger_mem(frozenset({token}))
            yield lemmatize_mem(token, tags.get(tag[0][1],  wn.NOUN))

# Pipeline definition
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(
        tokenizer=tokenizer,
        ngram_range=(1, 2),
        stop_words=ENGLISH_STOP_WORDS,
        sublinear_tf=True,
        min_df=0.00009
    )),
    ('classifier', SGDClassifier(
        alpha=1e-4, n_jobs=-1
    )),
])

# Cross validate using k-fold
y_pred = cross_val_predict(
    pipeline, dataset.get('data'),
    y=dataset.get('target'),
    cv=10, n_jobs=-1, verbose=20
)

# Compute precison, recall and f1 scode.
cr = classification_report(
    dataset.get('target'), y_pred,
    target_names=dataset.get('target_names'),
    digits=3
)

# Confusion matrix
cm = confusion_matrix(dataset.get('target'), y_pred)

# Get max length of category names for printing
label_length = len(
    sorted(dataset['target_names'], key=len, reverse=True)[0]
)

# Make shortened labels for plotting
short_labels = []
for i in dataset['target_names']:
    short_labels.append(
        ' '.join(map(lambda x: x[:3].strip(), i.split(' > ')))
    )

# Printing Classification Report
print('{label:>{length}}'.format(
    label='Classification Report',
    length=label_length
), cr, sep='\n')

# Pretty printing confusion matrix
print('{label:>{length}}\n'.format(
    label='Confusion Matrix',
    length=abs(label_length - 50)
))
for index, val in enumerate(cm):
    print(
        '{label:>{length}} {prediction}'.format(
            length=abs(label_length - 50),
            label=short_labels[index],
            prediction=''.join(map(lambda x: '{:>5}'.format(x), val))
        )
    )

# Plot confusion matrix in a separate window
#
# sn.set(font_scale=.7)
# sn.heatmap(
#     cm,
#     cmap="YlGnBu", linewidths=.5, fmt='g',
#     vmax=150,
#     annot=True, annot_kws={"size": 9},
#     xticklabels=short_labels,
#     yticklabels=short_labels
# )
#
# plt.yticks(rotation=45)
# plt.xticks(rotation=45)
#
# plt.show()
