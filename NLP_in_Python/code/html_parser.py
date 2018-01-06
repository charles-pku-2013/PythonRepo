#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 处理HTML网页

from urllib import urlopen
import nltk

#url = "http://news.bbc.co.uk/2/hi/health/2284783.stm"
url = "http://www.google.com"
html = urlopen(url).read()
print type(html), len(html)

# 清除HTML标记 clear html tags
raw = nltk.clean_html(html)
words = nltk.word_tokenize(raw)
print words