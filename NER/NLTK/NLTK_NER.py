
import nltk
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from nltk import pos_tag
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk.chunk import conlltags2tree
from nltk.tree import Tree

def process_text(raw_text):
    token_text = word_tokenize(raw_text)
    return token_text

# NLTK POS and NER taggers   
def nltk_tagger(token_text):
    tagged_words = nltk.pos_tag(token_text)
    ne_tagged = nltk.ne_chunk(tagged_words)
    return(ne_tagged)

def structure_ne(ne_tree):
    ne = []
    for subtree in ne_tree:
        if type(subtree) == Tree: # If subtree is a noun chunk, i.e. NE != "O"
            ne_label = subtree.label()
            ne_string = " ".join([token for token, pos in subtree.leaves()])
            ne.append((ne_string, ne_label))
    return ne

def nltk_main():
    raw_text = """Erik, Bob and Amos will meet in my office tomorrow morning. Please confirm if you would be able to go."""
    print(structure_ne(nltk_tagger(process_text(raw_text))))
    
if __name__ == '__main__':
    nltk_main()