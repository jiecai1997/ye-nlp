#!/usr/bin/python

#import packages
import csv
import json
import re
import numpy as np
from textblob import TextBlob
from textblob import Blobber
import nltk
tb = Blobber()

nltk.data.path.append('./nltk_data/')

# global variables
reviews = []
dictionaries = []
categories = ['Food', 'Ambiance', 'Price', 'Service']

##### LOADING IN FILES #####
for i, file in enumerate(['dict/food.csv', 'dict/ambiance.csv', 'dict/price.csv', 'dict/service.csv']):
	with open(file, 'r') as csvfile:
		rows = csv.reader(csvfile)
		dictionaries.append([row[0] for row in rows])
##########

##### USER REVIEWS SENTIMENTS #####
def os_single(review):
	review_str = review#.encode('ascii', 'ignore')
	overall_sentiments=[]
	overall_sentiment=cs_single(review_str)
	overall_sentiment_first = [i for i in overall_sentiment[0] if i!='N/A']
	#print(overall_sentiment_first)
	if (len(overall_sentiment_first) != 0):
		return float(round_average(sum(overall_sentiment_first, 0.0)/len(overall_sentiment_first)))
	else:
		return 'N/A'

def cs_single(review):
	category_sentiments=[]
	review_str=review#.encode('ascii', 'ignore')
	words = [sentence.words.lower().lemmatize() for sentence in tb(review_str).sentences]
	sentence_sentiments = [sentence.sentiment.polarity for sentence in tb(review_str).sentences]
	category_sentiments.append(categories_sentiments(dictionaries, sentence_sentiments, words))
	return category_sentiments
##########

##### OVERALL SENTIMENTS #####
def overall_sentiments_list(reviews):
	overall_sentiments=[]
	for i, entry in enumerate(reviews):
		# review_str - string version of review entry
		# review_tb - textblob version of review entry
		review_str = entry["text"]#.encode('ascii', 'ignore')
		review_tb = tb(review_str)
		overall_sentiments.append(sentiment_value_to_star(review_tb.polarity,0))
	return overall_sentiments

def overall_sentiments_ave(reviews):
	overall_sentiments=category_sentiments_list(reviews)
	overall_sentiments = [item for sublist in overall_sentiments for item in sublist]
	overall_sentiments = [sentiment for sentiment in overall_sentiments if sentiment != 'N/A']
	#print(overall_sentiments)
	return sum(overall_sentiments, 0.0)/len(overall_sentiments)
	#return round_average(np.mean(np.array(overall_sentiments), dtype=np.float64))

def overall_sentiments_std(reviews):
	overall_sentiments=overall_sentiments_list(reviews)
	#return 4
	return round(np.std(np.array(overall_sentiments), dtype=np.float64),3)
##########

##### CATEGORY SENTIMENTS #####
def category_sentiments_list(reviews):
	category_sentiments=[]
	for i, entry in enumerate(reviews[:5]):
		review_str = entry["text"]#.encode('ascii', 'ignore').decode('utf-8')
		review_tb = tb(review_str)
		words = [sentence.words.lower().lemmatize() for sentence in tb(review_str).sentences]
		sentence_sentiments = [sentence.sentiment.polarity for sentence in tb(review_str).sentences]
		category_sentiments.append(categories_sentiments(dictionaries, sentence_sentiments, words))
	return category_sentiments

def category_sentiments_ave(reviews):
	category_sentiments=category_sentiments_list(reviews)
	category_ave=[]
	for i, category in enumerate(categories):
		category_ave.append(np.mean(np.array([cat[i] for cat in category_sentiments if cat[i] !="N/A"]), dtype=np.float64))
	return category_ave

def category_sentiments_std(reviews):
	category_sentiments=category_sentiments_list(reviews)
	category_std=[]
	for i, category in enumerate(categories):
		category_std.append(round(np.std(np.array([cat[i] for cat in category_sentiments if cat[i] !="N/A"]), dtype=np.float64),3))
	return category_std
##########

##### SENTIMENT ANALYSIS HELPER FUNCTIONS #####
def categories_sentiments(dictionaries, sentiments, words):
	# create my list of sentiment values specific to each category
	my_sentiments_ave = []
	my_sentiments_std = []
	my_sentiment_stars = []
	# loop through each category
	for j, w in enumerate(dictionaries):
		# add list of all sentiment values for each sentence that contains words in that category
		#temp_sent = [sent for k,sent in enumerate(sentiments) if set(words[k]) & set(dictionaries[j])]
		temp_sent = []
		for k,sent in enumerate(sentiments):
			if(set(words[k]) & set(dictionaries[j])):
				if (abs(sent) > 0.5):
					sent = sent*2
				temp_sent.append(sent)
		# return average value of sentence sentiments if sentiment values exist
		#temp_sent = filter(lambda a: a != 0.0, temp_sent)
		temp_sent = [a for a in temp_sent if abs(a)>0.05]
		# remove very neutral values (-0.05, 0.05)
		#temp_sent = filter(lambda a: abs(a > 0.05), temp_sent)
		#print "Filtered",categories[j],"Sentiment Values", temp_sent

		# return average value of sentence sentiments if sentiment values exist
		if temp_sent:
			# my_sentiments_ave.append(round(sum(temp_sent)/len(temp_sent),2))
			#my_sentiments_ave.append(round(np.mean(np.array(temp_sent), dtype=np.float64),3))
			#my_sentiments_std.append(round(np.std(np.array(temp_sent), dtype=np.float64),3))
			my_sentiments_ave.append(round(float(sum(temp_sent))/len(temp_sent),2))
			my_sentiments_std.append(0)
		# if not applicable, return N/A indicating there were no sentences containing words of category, therefore nothing to analyze.
		else:
			my_sentiments_ave.append("N/A")
			my_sentiments_std.append("N/A")
	# loop though sentiments of all categories

	for k, sent in enumerate(my_sentiments_ave):
		# print out sentiment value of each category
		#print categories[k],"Sentiment (Value Mean):",my_sentiments_ave[k]
		#print categories[k],"Sentiment (Value Std):",my_sentiments_std[k]
		#print "Sentiment (Stars):", sentiment_value_to_star(my_sentiments_ave[k], my_sentiments_std[k])
		my_sentiment_stars.append(sentiment_value_to_star(my_sentiments_ave[k], my_sentiments_std[k]))
	return my_sentiment_stars

#round to nearest 0.5
def round_average(average):
	return(round(average*2)/2)

# converts [-1, 1] sentiment values to [1, 5] star scale
def sentiment_value_to_star(value_mean, value_std):
	# no mean
	if value_mean == "N/A":
		return "N/A"
	# TO DO: DETERMINE STANDARD DEVIATION CUTOFF
	# standard deviation too large, we can't determine a star
	elif value_std > 0.5:
		return "N/A"
	elif value_mean > 0.5:
		return 5
	elif value_mean >0.4:
		return 4.5
	elif value_mean > 0.3:
		return 4
	elif value_mean > 0.2:
		return 3.5
	elif value_mean > 0.1:
		return 3
	elif value_mean > 0:
		return 2.5
	elif value_mean > -0.1:
		return 2
	elif value_mean > -0.2:
		return 1.5
	else:
		return 1
##########
