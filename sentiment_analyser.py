import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.tokenize import word_tokenize
import pickle
 
def word_feats(words):
    return dict([(word, True) for word in words])



def find_features(document):
	words = word_tokenize(document)
	features = {}
	for w in word_feats(words):
		features[w] = (w in words)
	return features

 
negids = movie_reviews.fileids('neg')
posids = movie_reviews.fileids('pos')
 
negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
 

 
# trainfeats = negfeats[:950] + posfeats[:950]
testfeats = negfeats[50:] + posfeats[50:]
# print("train on "+str(1900)+" instances, test on "+str(100)+" instances")
 
# classifier = NaiveBayesClassifier.train(trainfeats)
# print("accuracy:", nltk.classify.util.accuracy(classifier, testfeats)*100)
# classifier.show_most_informative_features(50)

# classifier_save = open("nbclassifier_stream_hacker.pickle", "wb")
# pickle.dump(classifier, classifier_save)
# classifier_save.close()

classifier_f = open("naive_bayes_sentiment.pickle", "rb")
classifier = pickle.load(classifier_f)
classifier_f.close()
print("accuracy:", nltk.classify.util.accuracy(classifier, testfeats)*100)


def sentiment_analysis(text):
	feats = find_features(text)
	return classifier.classify(feats)