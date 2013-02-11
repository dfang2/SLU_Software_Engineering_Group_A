
"""Sentiment analyzer that uses the Naive Bayes Classifier algorithm for classification along with the nltk movie_review corpora. 

In its current state, it searches through a certain directory, analyzes all the text files in that directory and sends it to the zmq database with a dictionary value of its type and the sentiment rating."""


import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk import word_tokenize, wordpunct_tokenize
from nltk.corpus.reader import WordListCorpusReader
import yql
import json
import zmq
import os
import pprint
import urllib
import simplejson
import csv
import time
import sqlite3
import getyql


# Foundation code to incorporate our unique set of corpora, used to train the Naive Bayes Classifier on usefulness of a tweet and the sentiment of the tweet. This code will not be used until we begin to create are own data set for the trainer."""
os.chdir("/Users/DJiang/nltk_data/corpora/movie_reviews/neg")
tweet_review = nltk.corpus.reader.CategorizedPlaintextCorpusReader('.','.*\.txt', cat_pattern='(\w+)/*')

# Feature set function that builds a dictionary from the reviews, with a value of either positive or negative, followed by the corresponding tweet.
def review_features(review):
    return dict([(review, True) for review in review])
 
# Acquires the IDs of the reviews by its sentiment and stores them into negID and posIDs. 
negIDs = movie_reviews.fileids('neg')
posIDs = movie_reviews.fileids('pos')

#Creates a large dictionary based on review_features of negative and positive reviews
negReview = [(review_features(movie_reviews.words(fileids=[id])), 'neg') for id in negIDs]
posReview = [(review_features(movie_reviews.words(fileids=[id])), 'pos') for id in posIDs]

# Tvhe populated training set of all positive and negative reviews in the movie_review corpora.
trainSet = negReview[:len(negReview)] + posReview[:len(posReview)]
print "Training on ", len(trainSet), "individual files..."

#The Naive Bayes Classifer, using the trainSet to train.
sentimentClassifier = NaiveBayesClassifier.train(trainSet)
print "Training complete."

# Connect to the zmq server.
contextIN = zmq.Context()
contextOUT = zmq.Context()
socketIN = contextIN.socket(zmq.REP)
socketOUT = contextOUT.socket(zmq.REQ)

socketIN.bind("tcp://*:5556")
socketOUT.connect("tcp://localhost:5555")

# Have the server run forever.
while True:
	
    # Wait for the next request from the client and load the message.
    messageIN = socketIN.recv()
    rcvd = json.loads(messageIN)
    print len(rcvd)
    # Handler for tweet_push type.

    for tweet in rcvd:
        if tweet['type'] == "tweet_send":
            tweets = list()
            
            temp_tweet = tweet["id"], tweet["text"], tweet["created_at"]
            tweets.append(temp_tweet)
                
#            for twee in tweets: 
 #               tweet_data = {'type': "tweet_send", 'id':tweet[0], 'text':tweet[1], 'date':tweet[2]}
            
        
            tokens = word_tokenize(tweet["text"])
            features = review_features(tokens)
            print tweet["text"]
            print sentimentClassifier.classify(features), "\n"
            data_set = {'type': "tweet_push", 'id':tweet["id"] , 'date':tweet["created_at"], 'sentiment' : sentimentClassifier.classify(features)}

            messageOUT = json.dumps(data_set)
            pprint.pprint(data_set)
            socketOUT.send(messageOUT)

            messageOUT = socketOUT.recv()     
   

        else:
            # Send reply back to client that the query is unspecified.
            print "received unknown query, ignoring"
            socketIN.send("Ack")
    socketIN.send("Ack")

# Analyzes all tweets in the specified directory and sends the data to the zmq server through port 5555. Sends a dictionary value of its type and the corresponding sentiment rating.
"""
for files in os.listdir("."):
    if (files != '.DS_Store'):
        path = ('corpora/movie_reviews/neg/'+files)
        load = nltk.data.load(path, format='raw')
        tokens = word_tokenize(load)
        features = review_features(tokens)
        
        t = files, sentimentClassifier.classify(features)
        data_set = { 'sentiment' : sentimentClassifier.classify(features), 'type':"tweet_push"}
        message = json.dumps(data_set)
        
        pprint.pprint(data_set)
        socket.send(message)
        message = socket.recv()
"""



