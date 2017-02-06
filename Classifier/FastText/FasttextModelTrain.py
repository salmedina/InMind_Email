import fasttext

'''
This script trains four different embedding models with skipgram and with cbow for lengths 100 and 300 each.
'''

model = fasttext.skipgram('../processed_data/all_jokes_clean_unique.txt', 'ft_skipgram_model_100', dim=100)
model = fasttext.skipgram('../processed_data/all_jokes_clean_unique.txt', 'ft_skipgram_model_300', dim=300)
model = fasttext.cbow('../processed_data/all_jokes_clean_unique.txt', 'ft_cbow_model_100', dim=100)
model = fasttext.cbow('../processed_data/all_jokes_clean_unique.txt', 'ft_cbow_model_300', dim=300)