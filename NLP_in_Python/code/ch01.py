from nltk.book import *
text1
text2

# search
text1.concordance('monstrous')
text1.similar('monstrous')

text2.common_contexts(['monstrous', 'very'])

text4.dispersion_plot(["citizens", "democracy", "freedom", "duties", "America"])

text3.generate()

len(text3)
set(text3)
len(set(text3))
sorted(set(text3))

# 除法 返回小数 否则返回整数
from __future__ import division
len(text3) / len(set(text3))

text3.count('smote')

fdist1 = FreqDist(text1)
vocabulary1 = fdist1.keys()

long_words = [w for w in text1 if len(w) > 15]

# 二元组
nltk.bigrams(['more', 'is', 'said', 'than', 'done'])

text4.collocations()

# chatting
nltk.chat.chatbots()
























