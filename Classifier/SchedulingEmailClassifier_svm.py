'''
Created on Jul 22, 2016

@author: zhongzhu
'''
import os
from random import shuffle

from gensim import utils
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
import numpy
from sklearn.grid_search import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm.classes import SVC

import DBUtil


model_file = './trained_model.d2v'

class LabeledLineSentence(object):
    def __init__(self, emails):
        self.emails = emails
    
    def __iter__(self):
        for email in self.emails:
#             yield TaggedDocument(utils.to_unicode(email.subject + ' ' + email.one_line).split(), ['email_%s' % email.id])
            yield TaggedDocument(utils.to_unicode(email.subject).split(), ['email_%s' % email.id])
    
    def to_array(self):
        self.sentences = []
        for email in self.emails:
#             taggedDoc = TaggedDocument(utils.to_unicode(email.subject + ' ' + email.one_line).split(), ['email_%s' % email.id])
            taggedDoc = TaggedDocument(utils.to_unicode(email.subject).split(), ['email_%s' % email.id])
            self.sentences.append(taggedDoc)
        return self.sentences

    def sentences_perm(self):
        shuffle(self.sentences)
        return self.sentences
    
def vectorize():
    db = DBUtil.initDB()
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

db = DBUtil.initDB()
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
        train_labels.append(int(email.is_scheduling))
    else:
        test_arrays.append(model.docvecs[prefix_train_pos])
        test_labels.append(int(email.is_scheduling))
        
param_grid = [{'C': [1e-4, 1e-3, 1e-2, 1e-1, 1], 'kernel': ['linear']},
              {'C': [1e-4, 1e-3, 1e-2, 1e-1, 1], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']}
             ]
svc = SVC(probability=True);
classifier = GridSearchCV(svc, param_grid)
classifier.fit(numpy.array(train_arrays), numpy.array(train_labels))

print("Overall score is %f." % classifier.score(numpy.array(test_arrays), numpy.array(test_labels)))

corrects = []
wrongs = []
predictions = []
schedulings = []
for email in emails:
    email_id = email.id
    prefix_train_pos = 'email_' + str(email_id)
    if email_id % 5 == 0:
        prediction = classifier.predict([model.docvecs[prefix_train_pos]])[0]
        actual = int(email.is_scheduling)
        if actual == 1:
            schedulings.append(email_id)
        if prediction != actual:
            wrongs.append((email.id, prediction, actual))
        else:
#             print(max(classifier.predict_proba([model.docvecs[prefix_train_pos]])[0]), actual)
            corrects.append((email.id, prediction, actual))
        predictions.append((email.id, prediction, actual))
        
if len([x for x in predictions if x[1] == 1]) == 0:  # no prediction for 1
    print("Recall: %f, Precision: NA" % (len([x for x in wrongs if x[1] == 1]) / 7))
else:
    print("Recall: %f, Precision: %f" % (len([x for x in wrongs if x[1] == 1]) / 7,
                                         len([x for x in corrects if x[1] == 1]) / len([x for x in predictions if x[1] == 1])))
print("%i are wrong, %i are correct." % (len(wrongs), len(corrects)))
print("%i are scheduling emails." % len(schedulings))
print("EmailID\t\tPredicted\tActual")
for w in wrongs:
    print("%s\t\t%s\t\t%s" % w)
