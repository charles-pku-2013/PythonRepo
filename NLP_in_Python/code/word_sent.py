#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!! 分词 && 断句

import nltk

raw = open( '1BOON10.TXT', 'r' ).read()
print type(raw), len(raw)

words = nltk.word_tokenize(raw)
print type(words), len(words)
print words[:100]
wordpunct = nltk.wordpunct_tokenize(raw) #不能识别U.S.A.
print type(wordpunct), len(wordpunct)
print wordpunct[:100]

sentences = nltk.sent_tokenize(raw)
print type(sentences), len(sentences), type(sentences[0])
for i in range(10):
    print '%d: %s' % (i, sentences[i])