'''
Created on Jun 4, 2016

@author: zhongzhu
'''
import operator
import pickle

from DBUtil import initDB
from EnronDB import EnronDB


def get_top_words(num, doc):
    word_freq = {}
    total_count = 0
    for word in doc.split():
        word = word.lower()
        if not word.isalnum():
            continue
        if word not in word_freq:
            word_freq[word] = 1
            continue
        word_freq[word] += 1
        total_count += 1
    sorted_word_freq = sorted(word_freq.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_word_freq[:num]
#     return sorted_word_freq[-num:]

def get_email_top_10000_words():
    db = initDB()
    top_words = get_top_words(10000, db.get_all_content())
    return top_words

def get_number_of_different_words():
    db = initDB()
    doc = db.get_all_content()
    word_freq = {}
    total_count = 0
    for word in doc.split():
        word = word.lower()
        if not word.isalnum():
            continue
        if word not in word_freq:
            word_freq[word] = 1
            continue
        word_freq[word] += 1
        total_count += 1
    return (len(word_freq), total_count)

def dump_all_dates():
    db = initDB()
    all_dates = db.get_all_dates()
    with open("all_dates.pickle", "w+") as f:
        pickle.dump(all_dates, f)

def dump_word_frequencies():
    db = initDB()
    doc = db.get_all_content()
    word_freq = {}
    for word in doc.split():
        word = word.lower()
        if not word.isalnum():
            continue
        if word not in word_freq:
            word_freq[word] = 1
            continue
        word_freq[word] += 1
    with open("word_frequencies.pickle", "w+") as f:
        pickle.dump(word_freq.values(), f)


print(get_number_of_different_words())