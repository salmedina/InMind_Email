'''
Created on Jul 22, 2016

@author: zhongzhu
'''
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

import DBUtil
from sklearn.grid_search import GridSearchCV


db = DBUtil.initDB()
emails = db.get_all_brushed_emails()
raw_documents = []
targets = []
test_email_ids = []
test_documents = []
test_targets = []
for email in emails:
    if email.id % 5 != 0:
        raw_documents.append(email.subject + ' ' + email.one_line)
        targets.append(email.is_scheduling)
    else:
        test_documents.append(email.subject + ' ' + email.one_line)
        test_targets.append(email.is_scheduling)
        test_email_ids.append(str(email.id))
count_vect = CountVectorizer()

text_clf = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), ('clf', MultinomialNB()), ])

parameters = {'vect__ngram_range': [(1, 1), (1, 2)],
              'tfidf__use_idf': (True, False),
              'clf__alpha': (1e-2, 1e-3, 1e-4)}
gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
gs_clf = gs_clf.fit(raw_documents, targets)

print gs_clf.best_params_

predicted = gs_clf.predict(test_documents)
print(metrics.classification_report(test_targets, predicted))
# for actual, pre in zip(test_targets, predicted):
#     print('actual %r => predicted %s' % (actual, pre))