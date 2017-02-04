'''
This script is an extractive text summarizer that ranks the sentences in terms of their centrality
with respect to the rest of the text.

'''

import textblob as tb
import networkx as nx
import json
from textblob import TextBlob
from nltk.tokenize import sent_tokenize
from math import log
from operator import itemgetter

class TextSummarizer:
    def extract_sentences(self, text):
        sentences = []
        text_blob = TextBlob(text)
        for sentence in text_blob.sentences:
            sentences.append(str(sentence).replace('\n',' '))
        return sentences
    
    def sentences(self, text):
        sents = []
        for sentence in sent_tokenize(text):
            sents.append(sentence.replace('\n', ' '))
        return sents
    
    def calc_sent_similarity(self, sent1, sent2):
        tb1 = TextBlob(sent1)
        tb2 = TextBlob(sent2)
        common_words = list(set(tb1.words) & set(tb2.words))
        
        if len(common_words) == 0:
            return 0
        
        return log(len(common_words)) / (log(len(tb1.words)) + log(len(tb2.words)))
    
    def connect(self, nodes):
        return [(start, end, self.calc_sent_similarity(start, end))
                for start in nodes
                for end in nodes
                if start is not end]
    
    def rank(self, nodes, edges):
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        graph.add_weighted_edges_from(edges)
        return nx.pagerank(graph)
    
    def summarize(self, text, num_summaries = 3):
        nodes = self.sentences(text)
        edges = self.connect(nodes)
        scores = self.rank(nodes, edges)
        return sorted(scores.items(), key=itemgetter(1), reverse=True)[:num_summaries]
    
    def summary_to_json(self, summary):
        '''JSON output format:
        sentences
            - list of:
                - score
                - sentence
        '''
        sentences =[]
        for sentence,score in summary:
            sentences.append({'sentence':sentence, 'score':score})
            
        output_summary = {'sentences':sentences}
        return json.dumps(output_summary)


def usage_example():
    ''' The usage of the summarizer is as follows:
    1. Create a TextSummarizer instance
    2. call the summarize method with the text and how many top sentences to return
        this function returns a list of tuples (score,sentence)
    3. the TextSummarizer class can also convert the list of tuples to json format for the service
    '''

    summarizer = TextSummarizer()
    email_text = '''
The InMind retreat isthis Thursdayand we are very excited to see the demos and to have a fruitful discussion on the future of InMind. I am attaching the booklet for the retreat which contains the agenda for the day. Please note a few things: we allocated approximately 5 minutes of demo-time + 3 minutes questions/laptop switch overhead per PI, so demos with more PIs will be longer. Please prepare your demo to be no longer than 5 minutes. To finish on time and to be respectful of everyone's time, we will be draconian in keeping each person to 5 minutes and ensuring there is time to change computers and take questions.
  
'''
    email_summary = summarizer.summarize(email_text, 5)

    for sentence, score in email_summary:
        print '(%0.4f) %s'%(score, sentence)
        
    print summarizer.summary_to_json(email_summary)
    
if __name__=='__main__':
    usage_example()