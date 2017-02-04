'''
Created on Jul 14, 2016

@author: zhongzhu
'''
import os
from random import shuffle

from gensim import utils
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import numpy
from sklearn.linear_model import LogisticRegression
from sklearn.svm.classes import SVC

import DBUtil
from EnronDB import EnronDB


model_file = './trained_model.d2v'

class LabeledLineSentence(object):
    def __init__(self, emails):
        self.emails = emails
    
    def __iter__(self):
        for email in self.emails:
            yield TaggedDocument(utils.to_unicode(email.one_line).split(), ['email_%s' % email.id])
    
    def to_array(self):
        self.sentences = []
        for email in self.emails:
            taggedDoc = TaggedDocument(utils.to_unicode(email.one_line).split(), ['email_%s' % email.id])
            self.sentences.append(taggedDoc)
        return self.sentences

    def sentences_perm(self):
        shuffle(self.sentences)
        return self.sentences
    
def vectorize():
    db = EnronDB()
    db.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo', 'enron_experiment')
    emails = db.get_all_brushed_emails()
    sentences = LabeledLineSentence(emails)
    model = Doc2Vec(min_count=1, window=10, size=100, sample=1e-4, negative=5, workers=8)

    model.build_vocab(sentences.to_array())

    for epoch in range(10):  # @UnusedVariable
        model.train(sentences.sentences_perm())
    model.save(model_file)

if not os.path.isfile(model_file):
    print("Model doesn't exist, vectorizing...")
    vectorize()

model = Doc2Vec.load(model_file)
# print(model.docvecs['email_1'])
# print(model.docvecs.doctags)
# print('email_1' in model.docvecs.doctags.keys())
# print(len(model.docvecs.doctags.keys()))
# print(model['email_1'])

# print model.most_similar('email_id')
# print model.most_similar('you')
# print model.most_similar('get')
# print model.most_similar('enron')
# print model.most_similar('company')
# print model.most_similar('cfo')
# 
# exit(0)

db = EnronDB()
db.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo', 'enron_experiment')
emails = db.get_all_brushed_emails()

train_arrays = []
train_labels = []
test_arrays = []
test_labels = []

for email in emails:
    email_id = email.id
    prefix_train_pos = 'email_' + str(email_id)
    if email_id % 5 != 0:
        train_arrays.append(model.docvecs[prefix_train_pos])
        train_labels.append(int(email.label))
    else:
        test_arrays.append(model.docvecs[prefix_train_pos])
        test_labels.append(int(email.label))
        
classifier = LogisticRegression()
classifier.fit(numpy.array(train_arrays), numpy.array(train_labels))

print("Overall score is %f." % classifier.score(numpy.array(test_arrays), numpy.array(test_labels)))

corrects = []
wrongs = []
for email in emails:
    email_id = email.id
    prefix_train_pos = 'email_' + str(email_id)
    if email_id % 5 == 0:
        prediction = classifier.predict([model.docvecs[prefix_train_pos]])[0]
        actual = int(email.label)
        if prediction != actual:
            wrongs.append((email.id, prediction, actual))
        else:
#             print(max(classifier.predict_proba([model.docvecs[prefix_train_pos]])[0]), actual)
            corrects.append(email.id)

print("%i are wrong, %i are correct." % (len(wrongs), len(corrects)))
print(wrongs)
# print("EmailID\t\tPredicted\tActual")
# for w in wrongs:
#     print("%s\t\t%s\t\t%s" % w)
