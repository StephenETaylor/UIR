"""
A short demonstration of finding nearby words in a word-embedding.
You're not likely to have a word embedding at the path this program looks at.
but
you can download a wide variety of them from:
    http://vectors.nlpl.eu/repository/
"""
import gensim.models as gm
import numpy as np

model = gm.KeyedVectors.load_word2vec_format('../additive/English/model.bin', binary = True);

while True:
    w = input('gimme a word: ')
    neighbors = model.similar_by_word(w);
    print(neighbors)

