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
from sklearn.grid_search import GridSearchCV


model_file = './trained_model_ova.d2v'

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


def to_binary(label1, label2):
    if int(label1) == int(label2):
        return 1
    else:
        return -1

indi_predictions = []
actual_labels = []

for each_label in range(1, 15):  # for all categories
    train_arrays = []
    train_labels = []
    test_arrays = []
    test_labels = []
    for email in emails:
        email_id = email.id
        prefix_train_pos = 'email_' + str(email_id)
        if email_id % 5 != 0:
            train_arrays.append(model.docvecs[prefix_train_pos])
            train_labels.append(to_binary(each_label, email.label))
        else:
            test_arrays.append(model.docvecs[prefix_train_pos])
            test_labels.append(to_binary(each_label, email.label))
    
    param_grid = [{'C': [1e-4, 1e-3, 1e-2, 1e-1, 1], 'kernel': ['linear']},
                  {'C': [1e-4, 1e-3, 1e-2, 1e-1, 1], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']}
                 ]
    svc = SVC(probability=True);
    classifier = GridSearchCV(svc, param_grid)
    classifier.fit(numpy.array(train_arrays), numpy.array(train_labels))
#     print(classifier)
#     print(classifier.get_params())

#     print(each_label, "score", classifier.score(test_arrays, test_labels))

    predictions = []
    for email in emails:
        email_id = email.id
        prefix_train_pos = 'email_' + str(email_id)
        if email_id % 5 == 0:
#             prediction = classifier.predict([model.docvecs[prefix_train_pos]])[0]
            prediction = classifier.predict_proba([model.docvecs[prefix_train_pos]])[0]
            predictions.append(prediction[1])
            actual_labels.append(int(email.label))

    indi_predictions.append(predictions)

def softmax(w, t=1.0):
    e = numpy.exp(numpy.array(w) / t)
    dist = e / numpy.sum(e)
    return dist
 
labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
 
right = []
wrong = []
for i in range(len(indi_predictions[0])):
    all_pred = []
    for p in indi_predictions:
        all_pred.append(p[i])
    sm = softmax(all_pred).tolist()
    prediction_softmax = labels[sm.index(max(sm))]
#     print(sm)
    if prediction_softmax == actual_labels[i]:
        right.append(actual_labels[i])
    else:
        wrong.append((prediction_softmax, actual_labels[i]))


print(len(right) * 1.0 / (len(right) + len(wrong)))
print(wrong)
