# 列出语料库文件
import nltk
nltk.corpus.gutenberg.fileids()
# 文件中单词
emma = nltk.corpus.gutenberg.words('austen-emma.txt')


>>> from nltk.corpus import gutenberg
>>> gutenberg.fileids()

# 文本文件统计信息，单词数，句子数 ...
"""
    import nltk
    from nltk.corpus import gutenberg
    
    for fileid in gutenberg.fileids():
    num_chars = len(gutenberg.raw(fileid))
    num_words = len(gutenberg.words(fileid))
    num_sents = len(gutenberg.sents(fileid))
    num_vocab = len(set([w.lower() for w in gutenberg.words(fileid)]))
    print int(num_chars/num_words), int(num_words/num_sents), int(num_words/num_vocab), fileid
"""

# 载入自建语料库
from nltk.corpus import PlaintextCorpusReader
# 指定存放文本的根目录
corpus_root = './Training_Data'
wordlists = PlaintextCorpusReader(corpus_root, '.*')
wordlists.fileids()
# 单词 句子 计数 分词 分句
A = wordlists.words('WWEND10.TXT')
A = wordlists.sents('WWEND10.TXT')




















