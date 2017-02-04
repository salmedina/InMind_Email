#!/usr/bin/env python
import json
import argparse
from flask import Flask
from flask import request
from TextSummarizer import TextSummarizer

# ===================================================================
# GLOBALS
# ===================================================================
# Load the text summarizer once for the service
summarizer = TextSummarizer()

# ===================================================================
# FLASK APP
# ===================================================================
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    message='''The e-mail summarizer service is located at localhost:5000/summarize\n'''
    return message

@app.route('/summarize', methods = ['GET', 'POST'])
def summarize():
    '''
    The request must be done in JSON format with the fields:
    1. subject
    2. body
    the request header must be of type 'application/json'
    :return:
    '''
    print request.data
    print len(request.data)
    data = json.loads(request.data)
    
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

# ===================================================================
# MAIN
# ===================================================================

if __name__ == '__main__':
    # Load the arguments of the program
    # Host and port where the service will be running
    parser = argparse.ArgumentParser(description='Text summarizer server')
    parser.add_argument('-ip', '--ip', help='Host where the service will be running', required=True)
    parser.add_argument('-p', '--port', help='Port where the service will be running', required=True)
    args = vars(parser.parse_args())

    #This allows us to see the server output on console
    #disable if you want to run it in silence mode
    app.debug = True

    #Go baby! Go!
    app.run(host=args['ip'], port=int(args['port']))