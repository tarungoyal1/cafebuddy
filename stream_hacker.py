import nltk.classify
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.tokenize import word_tokenize
import pickle
from nltk.corpus import stopwords
# SklearnClassifier is the wrapper to include scikitlearn algos within nltk classifier itself
from nltk.classify.scikitlearn import SklearnClassifier
from sklearn.linear_model import LogisticRegression
 
def word_feats(words):
	stpwords = set(stopwords.words("english"))
	return dict([(word, True) for word in words if word not in stpwords])



def find_features(document):
	words = word_tokenize(document)
	stpwords = set(stopwords.words("english"))
	words = [word for word in words if word not in stpwords]
	features = {}
	for w in word_feats(words):
		features[w] = (w in words)
	return features

 
negids = movie_reviews.fileids('neg')
posids = movie_reviews.fileids('pos')
 
negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
 

 
trainfeats = negfeats[:950] + posfeats[:950]
testfeats = negfeats[50:] + posfeats[50:]
# print("train on "+str(1900)+" instances, test on "+str(100)+" instances")
 
# classifier = NaiveBayesClassifier.train(trainfeats)
# print("accuracy:", nltk.classify.util.accuracy(classifier, testfeats)*100)
# classifier.show_most_informative_features(50)

# classifier = SklearnClassifier(LogisticRegression())
# classifier.train(trainfeats)
# print("LogisticRegression_classifier algo accuracy percent:", (nltk.classify.accuracy(classifier, testfeats))*100)


classifier_f = open("logregclassifier_stream_hacker.pickle", "rb")
classifier = pickle.load(classifier_f)
classifier_f.close()
print("LogisticRegression_classifier algo accuracy percent:", (nltk.classify.accuracy(classifier, testfeats))*100)


# classifier_save = open("logregclassifier_stream_hacker.pickle", "wb")
# pickle.dump(classifier, classifier_save)
# classifier_save.close()

# print("accuracy:", nltk.classify.util.accuracy(classifier, testfeats)*100)
# classifier.show_most_informative_features(50)


# classifier_save = open("nbclassifier_stream_hacker.pickle", "wb")
# pickle.dump(classifier, classifier_save)
# classifier_save.close()

# classifier_f = open("naive_bayes_sentiment.pickle", "rb")
# classifier = pickle.load(classifier_f)
# classifier_f.close()
# print("accuracy:", nltk.classify.util.accuracy(classifier, testfeats)*100)


def sentiment_analysis(text):
	feats = find_features(text)
	return classifier.classify(feats)