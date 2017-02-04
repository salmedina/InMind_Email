#!/usr/bin/env python
import requests
import json

'''
This is an example on how to call the text summarizer service
The usage is simple by using the requests package
Make sure to declare the header and that data has both fields:
    1. subject
    2. body
The service run on the server under the path <<< server/summarize >>>
'''

class TextSummarizeClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_url = 'http://{host}:{port}/summarize'.format(
            host=self.host, port=self.port)
        self.header = {'content-type': 'application/json'}

    def summarize(self, subject, body):
        data = {'body':body, 'subject':subject}
        response = requests.post(self.server_url, data=json.dumps(data), headers=self.header)
        summary = json.loads(response.text)
        return summary

# ===================================================================
# MAIN
# ===================================================================
if __name__=='__main__':
    '''This is a driver example on how to use the client'''
    subject = 'Edgar Allan Poe'
    text = '''Many people don't know that Edgar Allan Poe also wrote stories about adventure on the high seas, buried pirate treasure, and a famous balloon ride. Poe invented the detective story with tales like "Murders in the Rue Morgue" and "The Purloined Letter". Sherlock Holmes and other fictional detectives would later be based on the characters that Poe created. Poe wrote love stories and even a few strange little comedies. He attempted to explain the composition of the universe in a way that sounds a little like quantum physics. Explore this site and you'll see why I think Edgar Allan Poe deserves to be recognized as one of the most original, imaginative, and ingenious authors of our society.'''
    client = TextSummarizeClient('localhost', 5000)
    summary = client.summarize(subject, text)
    for item in summary['sentences']:
        print item['score'], item['sentence']



