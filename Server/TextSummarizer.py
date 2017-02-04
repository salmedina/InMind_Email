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
        sentences =[]
        for sentence,score in summary:
            sentences.append({'sentence':sentence, 'score':score})
                                                
        output_summary = {'sentences':sentences}
        return json.dumps(output_summary)
