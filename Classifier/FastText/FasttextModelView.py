import fasttext
import numpy as np
from sklearn.neighbors import NearestNeighbors

class FastTextModel:
    def __init__(self, kNearest):
        self.model = None
        self.knn_model = None
        self.words = []
        self.word_vecs = []
        self.distances = []
        self.nearest_indices = []
        self.K = kNearest
        self.loaded_or_trained = False

    def calc_nearest(self):
        self.words, self.word_vecs = zip(*[[w_i, self.model[w_i]] for w_i in self.model.words])
        self.words = list(self.words)
        self.word_vecs = list(self.word_vecs)
        self.knn_model = NearestNeighbors(n_neighbors=self.K, algorithm='brute', metric='cosine').fit(self.word_vecs)
        self.distances, self.nearest_indices = self.knn_model.kneighbors(self.word_vecs)

    def train(self, data, output, dim):
        self.model = fasttext.skipgram(data, output, dim=dim)
        self.calc_nearest()
        self.loaded_or_trained = True

    def load(self, model_file):
        self.model = fasttext.load_model(model_file)
        self.calc_nearest()
        self.loaded_or_trained = True

    def get_nearest(self, word):
        if not self.loaded_or_trained:
            print 'ERROR: need to load or train a model'
            return []

        word = word.lower()
        if word not in self.words:
            print 'ERROR: Could not find word in vocabulary'
            return []

        word_index = self.words.index(word)
        return [self.words[i] for i in self.nearest_indices[word_index]]

    def print_nearest(self, word):
        if not self.loaded_or_trained:
            print 'ERROR: need to load or train a model'
            return

        word = word.lower()
        if word not in self.words:
            print 'ERROR: Could not find word in vocabulary'
            return

        word_index = self.words.index(word)
        nearest_tuples = [ (self.words[i], self.distances[i]) for i in self.nearest_indices[word_index]]
        for item in nearest_tuples:
            print item

    def get_nearest_words_to(self, vec):
        if self.knn_model is None:
            print 'ERROR: need to load or train a model'
            return

        nearest_dist, nearest_indices = self.knn_model.kneighbors(vec)
        return [self.words[i] for i in nearest_indices[0]]


    def get_vect(self, word):
        if self.model is None:
            print 'ERROR: need to load or train a model'
            return

        if word not in self.words:
            print 'ERROR: out of vocabularly'
            return

        return self.model[word]


if __name__=='__main__':
    model_file = '/Users/zal/CMU/openai/jokes/models/ft_skipgram_model_300.bin'

    print 'Creating model'
    model = FastTextModel(15)

    print 'Loading model'
    model.load(model_file)

    print 'Getting nearest neighbors to China'
    nearest = model.get_nearest('China')
    model.print_nearest('China')

    print 'Calculating vector analogy'
    # Calc for the next joke:
    fat         = np.array(model.get_vect('fat'))
    stanky      = np.array(model.get_vect('stanky'))
    nasty       = np.array(model.get_vect('nasty'))

    elephants   = np.array(model.get_vect('elephant'))
    peanuts     = np.array(model.get_vect('peanuts'))
    crocodile   = np.array(model.get_vect('crocodile'))

    delta       = nasty - fat

    print "ELEPHANTS"
    nearest_words = model.get_nearest_words_to(elephants)
    for word in nearest_words:
        print word

    print ''
    print "ELEPHANTS + DELTA"
    nearest_words = model.get_nearest_words_to(elephants+nasty)
    for word in nearest_words:
        print word




