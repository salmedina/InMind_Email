import os
import re
import nltk
import collections
from nltk.stem.wordnet import WordNetLemmatizer
import multiprocessing as mp
import cPickle as pickle


def mp_process_iterable(func, iterable):
    '''
    This function launches into N-1 threads the current action, where N is the number of cores
    '''
    numThreads = mp.cpu_count()-1
    pool = mp.Pool(numThreads)
    
    res = pool.map(func, iterable)
    
    pool.close()
    pool.join()
    
    return res

def multiply_by_two(x):
    return x*2

def mp_multiply_by_two(numbers):
    return mp_process_iterable(multiply_by_two, numbers)

if __name__=='__main__':
	x = range(100000)
	print mp_multiply_by_two(x)

