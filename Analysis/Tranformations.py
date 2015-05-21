from gensim import corpora, models, similarities
import logging
from Preprocess.py import MyCorpus

processed_dir = 'Users/mlinegar/Data/LDA/BoW'
_num_topics = 10

dictionary = corpora.Dictionary.load(processed_dir + "firsttry.dict")
corpus = corpora.MmCorpus(processed_dir + "firsttry.mm")

tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf(corpus)

lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=_num_topics)