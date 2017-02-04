import EnronDB
import math
from textblob import TextBlob as tb

def tf(word, blob):
    return float(blob.words.count(word)) / float(len(blob.words))

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(float(len(bloblist)) / float(1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

def flatten_list(inList):
    return [item for sublist in inList for item in sublist]

def get_verbs_from_db():
    '''Gets a list of verbs from the database'''
    edb = EnronDB.EnronDB()
    edb.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo','enron_experiment')
    verbs_list = edb.get_all_brushed_verbs_with_id()
    return verbs_list

def get_verbs_per_label(label):
    '''Gets a list of verbs from the database per class'''
    edb = EnronDB.EnronDB()
    edb.init('holbox.lti.cs.cmu.edu', 'inmind', 'yahoo','enron_experiment')
    verbs_list = edb.get_all_brushed_verbs_per_label(label)
    return verbs_list

def calc_tfidf():
    bloblist = []
    for label in range(1,15):
        verbs_list = get_verbs_per_label(label)
        verbs_str = ''
        for email_id, verbs in verbs_list:
            verbs_str += verbs + ' '
        verbs_str = verbs_str.lower()
        verbs_str.replace('be', '')
        verbs_str.replace('have', '')
        verbs_str.replace("'s", '')
        verbs_str.replace("weblink", '')
        bloblist.append(tb(verbs_str))
        
    for i, blob in enumerate(bloblist):
        print("Top words in document {}".format(i + 1))
        scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
        sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for word, score in sorted_words[:10]:
            print("\tWord: {}\tTF-IDF: {}".format(word, round(score, 5)))
    
if __name__=='__main__':
    calc_tfidf()