'''
Created on Jul 12, 2016

@author: zhongzhu
'''
import os

from sklearn.grid_search import GridSearchCV
from sklearn.svm.classes import SVC

import DBUtil
import numpy as np


def get_doc_vector(filename):
    with open(filename) as f:
        f.readline()  # skip the first line
        raw_content = f.read()

        word_vectors = []
        for line in raw_content.split("\n"):
            if not line:
                continue
            v = []
            for x in line.split(" ")[1:]:
                v.append(float(x))
            word_vectors.append(v)
            
        doc_vector = np.array([0] * len(word_vectors[0]))
        for vector in word_vectors:
#             doc_vector = np.multiply(doc_vector, np.array(vector))
            doc_vector = np.add(doc_vector, np.array(vector))
#         doc_vector = np.power(doc_vector, 1./len(word_vectors))
        doc_vector = np.divide(doc_vector, len(word_vectors))
    return doc_vector

# training_data_folder = "../training_data/"
training_data_folder = "../training_data_oneline/"

training_set = []
categories = []
db = DBUtil.initDB()
for filename in os.listdir(training_data_folder): 
    if filename == ".DS_Store":
        continue
    email_id = int(filename[6:-4])
    if email_id % 5 == 0:  # use 4 in every 5 emails as training set
        continue
    email = db.get_brushed_email(email_id)
    label = int(email.label)
    v = get_doc_vector(training_data_folder + filename)
    training_set.append(v)
    categories.append(label)

# clf = svm.SVC(decision_function_shape='ovo')
print("Training with dataset of " + str(len(training_set)) + " and categories are " + str(categories))
tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
# tuned_parameters = [{'kernel': ['linear'], 'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}]
clf = GridSearchCV(SVC(C=1), tuned_parameters, cv=5, scoring='precision_weighted')
clf.fit(training_set, categories)
for params, mean_score, scores in clf.grid_scores_:
    print("%0.3f (+/-%0.03f) for %r"
          % (mean_score, scores.std() * 2, params))

correct = []
wrong = []
for filename in os.listdir(training_data_folder): 
    email_id = int(filename[6:-4])
    if email_id % 5 != 0:  # use the rest as test set
        continue
    email = db.get_brushed_email(email_id)
    label = int(email.label)
    v = get_doc_vector(training_data_folder + filename)
    prediction = clf.predict([v])[0]
#     print("email " + str(email_id) + ": predicting " + str(prediction) + " and actual is " + str(label))
    if prediction == label:
        correct.append((email_id, prediction, label))
    else:
        wrong.append((email_id, prediction, label))
    
print(str(len(correct)) + " are correct, " + str(len(wrong)) + " are wrong.")
# print(correct)
print(wrong)