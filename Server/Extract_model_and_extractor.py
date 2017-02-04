
'''
Author: Justin Chiu
This script is made to train an e-mail classifier based on a SGD classifier
'''

#These two lines are the usually lib I called when coding
import string, sys, os, math, array, re, operator
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
#I think scipy need this
import numpy as np
from collections import defaultdict as dd
import pickle

text = dd(str)
mail_label = dd(int)
text1 = dd(str)

path = "/usr1/jchiu1/yahoo/server/December/data/Cleaned/"
files = os.listdir(path)
counter = 0
for filename in files:
    counter = counter + 1
    if counter > 60:
        break
    ifile = open(path+filename,"r")
    lines = ifile.readlines()
    ifile.close()
    line = ""
    for l in lines:
        line = line + " " + l.strip()
    start = line.find("<body>")+6
    end = line.find("</body>")
    body = line[start:end]
    text_uni = unicode(body, errors='replace')
    text[filename] = text_uni.strip()
    text1[filename] = text_uni.strip()
    mail_label[filename] = 0

path = "/usr1/jchiu1/yahoo/server/December/EricEmails/cleaned/"

files = os.listdir(path)
for filename in files:
    ifile = open(path+filename,"r")
#    print open(path+filename,"r")
    lines = ifile.readlines()
    ifile.close()
    line = ""
    for l in lines:
        line = line + " " + l.strip()
    #print line
    text_uni = unicode(line, errors='replace')
    #print text_uni 
    text[filename] = text_uni.strip()
    mail_label[filename] = 1


data1 = ["sure, lets meet tomorrow", "OK", "Yes we should meet", "Wed 2pm works fine", "I can do Thursday", "See you then", "We can meet then", "sure", "No problem", "see you", "Yes we could do that", "ok, friday this week", "alright see you then", "no problem, see you soon", "yes, let us do that", "Alright", "ok lets meet and talk", "sure, please reminds me when it get close", "will talk to you at that time", " ok see you soon" ]
label1 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
result = []
data = []
label = []
for k in text.keys():
    data.append(text[k])
    if mail_label[k] == 1:
        label.append(1)
    else:
        data1.append(text[k])
        label1.append(0)
        label.append(0)

count_vect= CountVectorizer()
X_train_counts = count_vect.fit_transform(data)
X_test_counts = count_vect.transform(["hello world"])
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
X_test_tfidf = tfidf_transformer.transform(X_test_counts)
clf =SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42).fit(X_train_tfidf, label)
#    pickle.dump( count_vect, open( target+".count_vect", "wb" ) )
#    pickle.dump( tfidf_transformer, open( target+".tfidf_transformer", "wb" ) )

X_train_counts1 = count_vect.transform(data1)
X_train_tfidf1 = tfidf_transformer.transform(X_train_counts1)
clf1 =SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42).fit(X_train_tfidf1, label1)

X_test_counts = count_vect.transform(["Can you open google chrome for me?"])
X_test_tfidf = tfidf_transformer.transform(X_test_counts)
predicted = clf.predict(X_test_tfidf)
print predicted
pickle.dump( clf, open( "model.clf", "wb" ) )
pickle.dump( clf1, open( "model1.clf", "wb" ) )
pickle.dump( count_vect, open( "count_vect", "wb" ) )
pickle.dump( tfidf_transformer, open( "tfidf_transformer", "wb" ) )

exit()

'''
#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotAmd
#fIRMID_N01F3_1997_09_09_19_48_55_R

mail_label = dd(set)
text = dd(str)

ifile = open("email-acts-all.env","r")
line = ifile.readlines()
ifile.close()
for l in line:
    token = l.split()
    mail_label[token[1]].add(token[4])



path = "/Users/justinchiu/Downloads/repository/together/Cleaned/"
files = os.listdir(path)
for filename in files:
    ifile = open(path+filename,"r")
#    print open(path+filename,"r")
    lines = ifile.readlines()
    ifile.close()
    line = ""
    for l in lines:
        line = line + " " + l.strip()
    start = line.find("<body>")+6
    end = line.find("</body>")
    body = line[start:end]
    text_uni = unicode(body, errors='replace')
    text[filename] = text_uni.strip()

#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotAmd
#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotCmt
#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotDlv
#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotDlvCmt
#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotProp
#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotReq
#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotReqAmdProp
#addToType pw_mail_2003_Aug_025_23_44_09 0 -1 NotReqProp

for target in ['Amd','Cmt','Dlv','DlvCmt','Prop','Req','ReqAmdProp','ReqProp']:
    result = []
    data = []
    label = []
    for f in files:
        data.append(text[f])
        if target in mail_label[f]:
            label.append(1)
        else:
            label.append(0)
    #print len(data)
    #print len(label)
    #exit()
    count_vect= CountVectorizer()
    X_train_counts = count_vect.fit_transform(data)
    #print X_train_counts.shape
    X_test_counts = count_vect.transform(["hello world"])
    #print X_test_counts.shape
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    X_test_tfidf = tfidf_transformer.transform(X_test_counts)
    clf =SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42).fit(X_train_tfidf, label)
    #print X_test_tfidf.shape
    #print X_train_tfidf.shape
    #print len(label)
    #predict = clf.predict(X_test_tfidf)
    #print predict
#    pickle.dump( count_vect, open( target+".count_vect", "wb" ) )
#    pickle.dump( tfidf_transformer, open( target+".tfidf_transformer", "wb" ) )
    pickle.dump( clf, open( target+".clf", "wb" ) )

pickle.dump( count_vect, open( "count_vect", "wb" ) )
pickle.dump( tfidf_transformer, open( "tfidf_transformer", "wb" ) )

c = pickle.load( open( "count_vect", "rb" ) )
t = pickle.load( open( "tfidf_transformer", "rb" ) )
Amd_clf = pickle.load( open( "Amd.clf", "rb" ) )
X_test_counts = c.transform(["test test I just want to check whether the e-mail classification is working."])
X_test_tfidf = t.transform(X_test_counts)
Amd_predicted = Amd_clf.predict(X_test_tfidf)

print Amd_predicted
#        X_test_counts = count_vect.transform(test_data)
#        X_test_tfidf = tfidf_transformer.transform(X_test_counts)
#        predicted = clf.predict(X_test_tfidf)

    for fold in range(10): #10 fold cross validation
        data = [] #classifier train text
        label = [] #classifier train label
        test_data = []
        test_label = []
        if fold == 0:
            pos = 0
            neg = 0
        counter = 0
        for f in files:
            if counter % 10 == fold:
                test_data.append(text[f])
                if target in mail_label[f]:
                    test_label.append(1)
                    if fold == 0:
                        pos = pos + 1
                else:
                    test_label.append(0)
                    if fold == 0:
                        neg = neg + 1
            else:
                data.append(text[f])
                if target in mail_label[f]:
                    label.append(1)
                    if fold == 0:
                        pos = pos + 1
                else:
                    label.append(0)
                    if fold == 0:
                        neg = neg + 1
            counter = counter + 1
#                neg = neg + 1
        #print (str(fold)+ " " + target)
        #print len(data)
        #print len(label)
        #print len(test_data)
        #print len(test_label)
#        print target
#        print pos
#        print neg
#        count_vect= CountVectorizer(ngram_range=(1, 2))
        count_vect= CountVectorizer()
        X_train_counts = count_vect.fit_transform(data)
        tfidf_transformer = TfidfTransformer()
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
        clf =SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42).fit(X_train_tfidf, label)

        X_test_counts = count_vect.transform(test_data)
        X_test_tfidf = tfidf_transformer.transform(X_test_counts)
        predicted = clf.predict(X_test_tfidf)
        result.append(np.mean(predicted == test_label))
    print target
    print np.mean(result)
    print "positive:"+ str(pos)
    print "negative:"+ str(neg)
            
'''

#data = [] #classifier text
#label = [] #classifier label

#global count_vect
#count_vect= CountVectorizer()
#X_train_counts = count_vect.fit_transform(data)
#the get the tf-idf transform
#global tfidf_transformer
#tfidf_transformer = TfidfTransformer()
#X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
#then train the classifier (clf is the libsvm classifier trained with scikit), which will be used in extract_for_crf so it's global
#global clf
#clf =SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42).fit(X_train_tfidf, label)

#print text