#!/usr/bin/env python
import string, sys, os, math, array, re, operator, argparse
from collections import defaultdict as dd
from flask import Flask, url_for
from flask import request
#thread_extractor
from extractor import Extractor
from spacyNER import SpaCyNER


import time
import json
import sys
import re
import os
import pprint
import json
import jsonrpc
import jsonrpclib
import argparse
import nltk
import spacy
from TextSummarizer import TextSummarizer
from simplejson import loads
from dateutil.parser import parse as dt_parse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from practnlptools.tools import Annotator

import numpy as np
import pickle
import fasttext

ner = SpaCyNER(modelPath)            #modelPath  : need to modify

nlp = spacy.load('en')

annotator=Annotator()

# Load summarization globals
summarizer = TextSummarizer()

# Load classifier globals
count_vect = pickle.load( open( "count_vect", "rb" ) )
tfidf_transformer = pickle.load( open( "tfidf_transformer", "rb" ) )
clf = pickle.load( open( "model.clf", "rb" ) )
clf1 = pickle.load( open( "model1.clf", "rb" ) )

# Establish connection with the SCNLP server
server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(), jsonrpc.TransportTcpIp(addr=("holbox.lti.cs.cmu.edu", 9000)))
#server = jsonrpclib.Server("http://localhost:9000")
# Test connection with the SCNLP server
result = loads(server.parse("This is the hello world testing text for standord nlp"))
if result != '':
    print 'Established connection to SCNLP service'

# ===================================================================
# AUXILIARY FUNCTIONS
# ===================================================================

def time_match(strg, search=re.compile(r'[^0-9.:;\'\"]').search):
    return not bool(search(strg))

# ===================================================================
# FLASK APP
# ===================================================================
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    message='''The e-mail classifier service is located at :5000/parse through POST info as JSON\n
    The text summarizer service is located at :5000/summarize\n
    The Stanford Core NLP server is running at :9000'''
    return message

@app.route('/summarize', methods = ['GET', 'POST'])
def summarize():
    print request.data
    print len(request.data)
    data = json.loads(request.form['data'])
    
    print 'Normalizing request fields'
    for key in data.keys():
        data[key.lower()] = data.pop(key)
    keys = data.keys()
    
    print 'Validating request fields'
    if "body" in keys:
        print 'Found Body in the request'
        body = data["body"]
    else:
        return "NO BODY!"
    
    if "subject" in keys:
        print 'Found Subject in the request'
    
    email_summary = summarizer.summarize(body)
    json_response = summarizer.summary_to_json(email_summary)
    return json_response
    
def solve_email_corref(text, i_replacement, you_replacement):
    global nlp
    tokens = nlp(unicode(text))
    rst = ""
    lenList = []
    idxList = []
    for token in tokens:
        lenList.append(len(token.text))
        idxList.append(token.idx)
    for i in range(len(tokens)-1):
        if tokens[i].text.lower()==unicode('i') and tokens[i].pos==93:
            rst = rst + i_replacement + ' '*(idxList[i+1]-idxList[i]-lenList[i])
        elif tokens[i].text.lower()==unicode('you') and tokens[i].pos==93:
            rst = rst + you_replacement + ' '*(idxList[i+1]-idxList[i]-lenList[i])
        else:
            rst = rst + tokens[i].text + ' '*(idxList[i+1]-idxList[i]-lenList[i])
    if len(tokens)==0:
        return rst
    if tokens[-1].text.lower()==unicode('i'):
        rst = rst + i_replacement
    elif tokens[-1].text.lower()==unicode('you'):
        rst = rst + you_replacement
    else:
        rst = rst + tokens[-1].text
    return rst
    
def preprocess_email(text, i_replacement, you_replacemnt):
    #extract thread here
    latestEmailBody = Extractor.extract(text)[0][0]
    
    processed_text = solve_email_corref(latestEmailBody, i_replacement,you_replacemnt)
    return processed_text

    
@app.route('/parse', methods = ['GET', 'POST'])
def distract():
    global ner
    global annotator
    
    print 'Initializing'
    output = dd()
    # Fields to be discovered within the e-mail
    output['who'] = ''
    output['what'] = ''
    output['when'] = ''
    output['where'] = ''
    output['type'] = -1
    output['sender'] = ''
    
    print 'Processing request'
    print 'Loading request'

    print request.data
    print len(request.data)
    print request.form['data']
    data = json.loads(request.form['data'])
    #data  fields:   subject  body   sender  user_name
    print 'Normalizing request fields'
    for key in data.keys():
        data[key.lower()] = data.pop(key)
    keys = data.keys()
    
    print 'Validating request fields'
    if "body" in keys:
        print 'Found Body in the request'
        body = data["body"]
    else:
        return "NO BODY!"
    
    if "sender" in keys:
        print 'Found Sender in the request'
        output["who"] = data["sender"]
        
    if "subject" in keys:
        print 'Found Subject in the request'
        output["what"] = data["subject"]
    
    print 'Parsing body through SCNLP'
    result = loads(server.parse(body))

    print 'Looking for time-entity within sentences'
    foundTimeEntity = False
    for s in result['sentences']:
        for w in s['words']:
            if 'Timex' in w[1].keys():
                print 'Found time-entity within a sentence.'
                foundTimeEntity = True
    
    print 'Classifying e-mail'
    #X_test_counts = count_vect.transform([body])
    #X_test_tfidf = tfidf_transformer.transform(X_test_counts)
    #predicted = clf.predict(X_test_tfidf)
    #predicted1 = clf1.predict(X_test_tfidf)

    #if predicted[0] == 1 or foundTimeEntity:
        # Timed event e-mail class
    #    output["type"] = 1
    #elif predicted1[0] == 1:
        # Meeting event but non-timed
    #   output["type"] = 2
    #else:
        # Any other e-mail class
    #    output['type'] = 0
    #we first need to do body extraction by the thread extractor
    #and then get the body = string 
    
    body = preprocess_email(body, data["sender"], data["user_name"])
    fastTextClassifier = fasttext.load_model('model_bin')
    #text = [body]
    label = int(fastTextClassifier.predict([body])[0][0][-1])
    
    #label==1: sche
    #label==0: non-sch

    if label==0:
        output['scheduling'] = 0
        output['what'] = None
        output['where'] = None
        output['when'] = None
        output['who'] = None
        return json.dumps(output)
        
    #label==1
    #body-----string
    #assume one of the inputs is : ner
    
    nerRst = ner.test(body)
    
    searchDict = {'TIME':[],'DATE':[],'LOCATION':[],'NAME':[],'ORGANIZATION':[]}
    rstDict = {'TIME':[],'DATE':[],'LOCATION':[],'NAME':[],'ORGANIZATION':[]}
    preIdx ={'TIME':-2,'DATE':-2,'LOCATION':-2,'NAME':-2,'ORGANIZATION':-2}
    for i in range(len(nerRst)):
        if nerRst[i][1] in searchDict:
            if i==(preIdx[nerRst[i][1]]+1):
                searchDict[nerRst[i][1]].append(preIdx[nerRst[i][0])
            else:
                if len(searchDict[item[1]])!=0:
                    rstDict[nerRst[i][1]].append(' '.join(searchDict[item[1]]))
                searchDict[item[1]] = [preIdx[nerRst[i][0]]
            preIdx[nerRst[i][1]] = i
    
    for k,v in searchDict.items():
        if len(v)!=0:
            rstDict[k].append(' '.join(v))
            
    output['what'] = ','.join(rstDict['ORGANIZATION'])
    output['who'] = ','.join(rstDict['NAME'])
    output['where'] = ',' join(rstDict['LOCATION'])
    output['when'] = ','.join(rstDict['TIME']) + '\t' + ','.join(rstDict['DATE'])
    

    # Format output to JSON format
    return json.dumps(output)

if __name__ == '__main__':
    # Load the arguments of the program
    # Host and port where the service will be running
    parser = argparse.ArgumentParser(description='Text summarizer server')
    parser.add_argument('-ip', '--ip', help='Host where the service will be running', required=False, default='0.0.0.0')
    parser.add_argument('-p', '--port', help='Port where the service will be running', required=False, default=5000)
    args = vars(parser.parse_args())

    app.debug = True
    app.run(host=args['ip'], port=int(args['port']))