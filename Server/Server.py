#!/usr/bin/env python
import string, sys, os, math, array, re, operator, argparse
from collections import defaultdict as dd
from flask import Flask, url_for
from flask import request
import time
import json
import sys
import re
import os
import pprint
import json
import jsonrpc
import jsonrpclib
from TextSummarizer import TextSummarizer
from simplejson import loads
from dateutil.parser import parse as dt_parse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
import numpy as np
import pickle

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
    
@app.route('/parse', methods = ['GET', 'POST'])
def distract():
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
    
    #TODO: Add logger
    #TODO: VAlidate request type
    print request.data
    print len(request.data)
    print request.form['data']
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
    X_test_counts = count_vect.transform([body])
    X_test_tfidf = tfidf_transformer.transform(X_test_counts)
    predicted = clf.predict(X_test_tfidf)
    predicted1 = clf1.predict(X_test_tfidf)

    if predicted[0] == 1 or foundTimeEntity:
        # Timed event e-mail class
        output["type"] = 1
    elif predicted1[0] == 1:
        # Meeting event but non-timed
        output["type"] = 2
    else:
        # Any other e-mail class
        output['type'] = 0
        
    if output['type'] == 1:
        print 'Timed-event e-mail class found'
        result = loads(server.parse(body))
        time_str = ''
        extra_time_str = ''
        print 'Looking for event detail entities within body'
        for s in result['sentences']:
            for w in s['words']:
                print w
                if 'NamedEntityTag' in w[1].keys():
                    if w[0].lower() in ["today", "tonight"]:
                        time_str = time_str + " " + time.strftime("%x")
                        time_str = dt_parse(time_str)
                        continue
                    if w[0].lower() in ["tomorrow"]:
                        time_str = time_str+ " " + str(int(time.strftime("%d"))+1) + " " + time.strftime("%b")
                        time_str = dt_parse(time_str)
                        continue
                    if w[0].lower() in ["yesterday"]:
                        time_str = time_str+ " " + str(int(time.strftime("%d"))-1) + " " + time.strftime("%b")
                        time_str = dt_parse(time_str)
                        continue
                    if w[1]['NamedEntityTag'] == "ORGANIZATION":
                        output['where'] = output['where'] + " " + w[0]
                    if w[1]['NamedEntityTag'] == "NUMBER":
                        time_str = time_str+ " " + w[0]
                if 'Timex' in w[1].keys():
                    if not time_match(w[0]):
                        if w[0].lower == 'midnight':
                            time_str += ' 0:00'
                        elif w[0].lower == 'noon':
                            time_str += ' 12:00'
                            extra_time_str = extra_time_str + ' ' + w[0]
                    else:
                        time_str = time_str + " " + w[0]
                        time_str = dt_parse(time_str)

        print 'Formatting time and place'
        output["when"] = str(time_str) + ' ' + extra_time_str
    
    print 'Ready to deploy answer'
    # Format output to JSON format
    return json.dumps(output)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)