from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from sqlalchemy import *
from gensim import corpora, models
import re
import gensim
import EnronDB

url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
email_regex = '[\w\.-]+@[\w\.-]+'

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def get_emails(s):
    """Returns an iterator of matched emails found in string s."""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    return (email[0] for email in re.findall(regex, s) if not email[0].startswith('//'))

def get_body_from_db():
    '''Gets a list of the email body from the database'''
    edb = EnronDB.EnronDB()
    edb.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo','enron_experiment')
    body_list = edb.get_all_subjects()
    return body_list
    

tokenizer = RegexpTokenizer(r'\w+')

# create English stop words list
en_stop = get_stop_words('en')

# Create p_stemmer of class PorterStemmer
p_stemmer = PorterStemmer()

# Obtain the docs    
doc_set = get_body_from_db()

# list for tokenized documents in loop
texts = []

# loop through document list
for i in doc_set:
    
    # clean and tokenize document string
    raw = i.lower()
    
    # replace the weblinks with WEBLINK token
    urls = re.findall(url_regex, raw)
    for url in urls:
        raw = raw.replace(url, 'WEBLINK')
        
    # replace the email addresses with EMAIL token
    emails = re.findall(email_regex, raw)
    for email in emails:
        raw = raw.replace(email, 'EMAIL')
    
    tokens = tokenizer.tokenize(raw)
    
    # replace numeric tokens with NUMBER token
    #num_tokens = ['NUMBER' if is_number(i) else i for i in tokens]
    num_tokens = [i for i in tokens if not is_number(i) ]

    # remove stop words from tokens
    stopped_tokens = [i for i in num_tokens if not i in en_stop]
    
    # stem tokens
    stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
    
    # add tokens to list
    texts.append(stemmed_tokens)

# turn our tokenized documents into a id <-> term dictionary
dictionary = corpora.Dictionary(texts)
    
# convert tokenized documents into a document-term matrix
corpus = [dictionary.doc2bow(text) for text in texts]


num_topics = [15, 20]
num_words = [2, 5]

for nTopic in num_topics:    
    # generate LDA model
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=nTopic, id2word = dictionary, passes=20)
    for nWords in num_words:
        topics = ldamodel.print_topics(num_topics=nTopic, num_words=nWords)
        
        print '\n\n****** NUM TOPICS: %d  - NUM WORDS: %d ********************'%(nTopic, nWords)
        for topic in topics:
            print topic