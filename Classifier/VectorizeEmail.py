'''
Created on Jul 10, 2016

@author: zhongzhu
'''
from gensim.models.word2vec import Word2Vec
from nltk.tokenize import word_tokenize, sent_tokenize
import DBUtil

db = DBUtil.initDB()
all_emails = db.get_all_brushed_emails()
for email in all_emails:
#     if email.label == 1L: # skip all emails with label 1
#         continue
    try:
        raw = email.one_line
        sentences = [raw.split(" ")]
#         raw_sens = sent_tokenize(raw)
#         for raw_sen in raw_sens:
#             sentences.append(word_tokenize(raw_sen))

        model = Word2Vec(sentences, size=100, window=5, min_count=1, workers=4)
        model.save_word2vec_format("../training_data_oneline/model_" + str(email.id) + ".txt")
    except RuntimeError as e:
        print("Error processing email " + str(email.id))
        print(e)