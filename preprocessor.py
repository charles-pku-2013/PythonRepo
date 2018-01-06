#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, codecs, os
from xml.dom.minidom import parse, Node

wordTypeIndex = None
wordDictionary = dict()
testAnswer = dict()
nAttributes = 10
directorySet = set()


outputFile = codecs.open( 'out.txt', 'w', encoding='utf-8' )


#def buildWordTypeIndex( tagFileName ):
#    global wordTypeIndex
#    L = map(unicode.split, codecs.open(tagFileName, 'r', encoding='utf-8'))
##    print L
#    tags = [ x[0] for x in L ]
#    tags.append( u'nx' )
#    tags.append( u'Ug' )
#    tags.append( u'az' )
#    tags.append( u'bz' )
#    tags.append( u'd2' )
#    tags.append( u'ys' )
#    tags.append( u'ap' )
##    print tags
##    print len(tags)
#    wordTypeIndex = { tag: (index+1) for (index, tag) in enumerate(tags) }
#    wordTypeIndex[u'NULL'] = 0
##    tagIndex = { tag: index for (index, tag) in tagIndex }
##    print { k: v for (v, k) in tagIndex.items() }

# to generate tags list
# cat *.xml | grep 'pos=' | awk -F'\"' '{print $4}' > pos_tags
def buildWordTypeIndex( tagFileName ):
    global wordTypeIndex
    S = set()
    for line in codecs.open(tagFileName, 'r', encoding='utf-8'):
        line = line.strip()
        if len(line):
            S.add(line)
    wordTypeIndex = { tag: (index+1) for (index, tag) in enumerate(S) }
    wordTypeIndex[u'NULL'] = 0


def buidDictionary( filename ):
    global wordDictionary
    for line in codecs.open(filename, 'r', encoding='utf-8'):
        L = line.strip().split()
        word = L[0]; explain = L[-1]
        wordDictionary[word] = wordDictionary.get(word, set())
        wordDictionary[word].add( explain )
    for key in wordDictionary.keys():
        value = wordDictionary[key]
        newValue = { word: index+1 for (index, word) in enumerate(value) }
        wordDictionary[key] = newValue


def getIndex( prefix, tagging, head ):
    if not len(prefix):
        return 0
    Str = u''
    index = 0
    for index in range(len(tagging)):
        Str += tagging[index][0]
        if prefix in Str:
            break
    if head not in tagging[index][0]:
        index = index + 1
    return index


# remove the leading and trailing empty lines
def stripWord( word ):
    L = map(unicode.strip, word.splitlines())
    for s in L:
        if len(s):
            return s

def createTrainDataSet( lexeltNode ):
    lexelt = lexeltNode.getAttribute('item')
    filename = 'train-preprocessed.txt'
    fullname = 'corpus-%s/%s' % (lexelt, filename)
    #!! 按需创建目录
    dirname = os.path.dirname(fullname)
    directorySet.add( dirname )
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    dataFile = open(fullname, 'w')
    
    outputFile.write( '%s\n' % lexelt )
    for instanceNode in lexeltNode.getElementsByTagName('instance'):
        senseid = instanceNode.getElementsByTagName('answer')[0].getAttribute('senseid')
        senseidIndex = wordDictionary[lexelt][senseid]
        outputFile.write( 'senseid = %s\n' % senseid )
        context = instanceNode.getElementsByTagName('context')[0]
        head = context.getElementsByTagName('head')[0].childNodes[0].nodeValue
        
#            for child in context.childNodes:
#                if child.nodeType == Node.TEXT_NODE:
#                    outputFile.write( child.nodeValue.strip() )
#            outputFile.write('\n')

        prefix = context.childNodes[0].nodeValue.strip()
        outputFile.write( 'prefix = %s\n' % prefix )

        postaggingNode = instanceNode.getElementsByTagName('postagging')[0]
        tagging = []
        for wordNode in postaggingNode.getElementsByTagName('word'):
            pos = wordNode.getAttribute('pos')
            word = wordNode.getElementsByTagName('token')[0].childNodes[0].nodeValue
            tagging.append( (stripWord(word), pos) )

        for (k,v) in tagging:
            outputFile.write( '%s:%s ' % (k,v) )
        outputFile.write('\n')
        
        index = getIndex( prefix, tagging, head )
        outputFile.write( 'head = %s, index = %s\n' % (head, index) )
        if head not in tagging[index][0]:
            outputFile.write( 'FUCK!!! %s\n' % tagging[index][0] )

        typeIndex = wordTypeIndex[ tagging[index][1] ]
        dataFile.write( '%s %s %s ' % (senseidIndex, typeIndex, index) )

        for j in range(len(tagging)):
            dataFile.write( '%s ' % wordTypeIndex[ tagging[j][1] ])
        dataFile.write('\n')


def createTestDataSet( lexeltNode ):
    lexelt = lexeltNode.getAttribute('item')
    filename = 'test-preprocessed.txt'
    fullname = 'corpus-%s/%s' % (lexelt, filename)
    dirname = os.path.dirname(fullname)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    dataFile = open(fullname, 'w')
    
    outputFile.write( '%s\n' % lexelt )
    for instanceNode in lexeltNode.getElementsByTagName('instance'):
        instanceName = instanceNode.getAttribute('id')
#        print 'instancesName = %s' % instanceName
        senseid = testAnswer[instanceName]
        senseidIndex = wordDictionary[lexelt][senseid]
        outputFile.write( 'senseid = %s\n' % senseid )
        context = instanceNode.getElementsByTagName('context')[0]
        head = context.getElementsByTagName('head')[0].childNodes[0].nodeValue
        prefix = context.childNodes[0].nodeValue.strip()
        outputFile.write( 'prefix = %s\n' % prefix )

        postaggingNode = instanceNode.getElementsByTagName('postagging')[0]
        tagging = []
        for wordNode in postaggingNode.getElementsByTagName('word'):
            pos = wordNode.getAttribute('pos')
            word = wordNode.getElementsByTagName('token')[0].childNodes[0].nodeValue
            tagging.append( (stripWord(word), pos) )
        
        for (k,v) in tagging:
            outputFile.write( '%s:%s ' % (k,v) )
        outputFile.write('\n')

        index = getIndex( prefix, tagging, head )
        outputFile.write( 'head = %s, index = %s\n' % (head, index) )
        if head not in tagging[index][0]:
            outputFile.write( 'FUCK!!! %s\n' % tagging[index][0] )

        typeIndex = wordTypeIndex[ tagging[index][1] ]
        dataFile.write( '%s %s %s ' % (senseidIndex, typeIndex, index) )
        
        for j in range(len(tagging)):
            dataFile.write( '%s ' % wordTypeIndex[ tagging[j][1] ])
        dataFile.write('\n')


def loadTestAnswer( filename ):
    global testAnswer
    for line in codecs.open(filename, 'r', encoding='utf-8'):
        line = line.strip()
        if len(line):
            L = line.split()
            key = L[1]
            sepIndex = key.find(u'.')
            name = key[:sepIndex]
            NO = int(key[sepIndex+1:])
            key = u'%s.%s' % (name, NO)     #!! unicode字符串构造
            testAnswer[ key ] = L[2]



def convertToUnScaledData( filename ):
    dataFileName = filename.replace( 'preprocessed', 'unscale' )
    dataFile = open( dataFileName, 'w' )
    for record in open(filename, 'r'):
        attrList = []
        L = record.strip().split()     #!! 处理空行
        if len(L):
            target = L[0]               # meaning id
            attr1 = L[1]                # 第一个属性：词性
            index = int(L[2])
            remainder = L[3:]
            attrList.append(attr1)
            step = 1
            while True:
                iBefore = index - step
                if iBefore >= 0:
                    attrList.append(remainder[iBefore])
                    if len(attrList) >= nAttributes + 1:
                        break
                iAfter = index + step
                attrValue = remainder[iAfter] if iAfter < len(remainder) else wordTypeIndex[u'NULL']
                attrList.append(attrValue)
                if len(attrList) >= nAttributes + 1:
                    break
                step = step + 1
            attrList = [ (index+1, value) for (index, value) in enumerate(attrList) ]
            # write to file
            dataFile.write( '%s ' % target )
            for (index, value) in attrList:
                dataFile.write( '%s:%s ' % (index, value) )
            dataFile.write('\n')


def convertToCSV( filename ):
    dataFileName = filename.replace( '-preprocessed.txt', '.csv' )
    dataFile = open( dataFileName, 'w' )
    # title line
    for i in range(nAttributes+1):
        dataFile.write( 'Attr%d,' % i )
    dataFile.write('Target\n')
    for record in open(filename, 'r'):
        attrList = []
        L = record.strip().split()     #!! 处理空行
        if len(L):
            target = L[0]               # meaning id
            attr1 = L[1]                # 第一个属性：词性
            index = int(L[2])
            remainder = L[3:]
            attrList.append(attr1)
            step = 1
            while True:
                iBefore = index - step
                if iBefore >= 0:
                    attrList.append(remainder[iBefore])
                    if len(attrList) >= nAttributes + 1:
                        break
                iAfter = index + step
                attrValue = remainder[iAfter] if iAfter < len(remainder) else wordTypeIndex[u'NULL']
                attrList.append(attrValue)
                if len(attrList) >= nAttributes + 1:
                    break
                step = step + 1
            # write to file
            for i in range(nAttributes+1):
                dataFile.write('%s,' % attrList[i])
            dataFile.write('%s\n' % target)

# for weka
def convertToARFF( filename ):
    relationName = 'corpus'
    dataFileName = filename.replace( '-preprocessed.txt', '.arff' )
    dataFile = open( dataFileName, 'w' )
    
    wholeList = []                  #!! 用list构建二维矩阵 append(newList)
    
    for record in open(filename, 'r'):
        attrList = []
        L = record.strip().split()     #!! 处理空行
        if len(L):
            target = L[0]               # meaning id
            attr1 = L[1]                # 第一个属性：词性
            index = int(L[2])
            remainder = L[3:]
            attrList.append(attr1)
            step = 1
            while True:
                iBefore = index - step
                if iBefore >= 0:
                    attrList.append(remainder[iBefore])
                    if len(attrList) >= nAttributes + 1:
                        break
                iAfter = index + step
                attrValue = remainder[iAfter] if iAfter < len(remainder) else wordTypeIndex[u'NULL']
                attrList.append(attrValue)
                if len(attrList) >= nAttributes + 1:
                    break
                step = step + 1
            attrList.append(target)
            wholeList.append(attrList)

    # write to file
    dataFile.write( '@relation %s\n\n' % relationName )
    # write attributes section @attribute Attr0 {1,2,3,4,5}
    nAttrToWrite = len(wholeList[0])
    for i in range(nAttrToWrite):
        attrName = ('Attr%d' % i) if (i < nAttrToWrite-1) else 'Target'
        attrValSet = sorted(set([ r[i] for r in wholeList ]) )      #!! 这样选取列
        dataFile.write( '@attribute %s {' % attrName )
        for j in range(len(attrValSet)-1):
            dataFile.write( '%s, ' % attrValSet[j] )
        dataFile.write( '%s}\n' % attrValSet[-1] )
    # write data section
    dataFile.write( '\n@data\n' )
    for i in range(len(wholeList)):
        for j in range(nAttrToWrite-1):
            dataFile.write('%s,' % wholeList[i][j])
        dataFile.write('%s\n' % wholeList[i][-1])



def mergePreprocessedFile():
    pwd = os.getcwd()
    for dirname in directorySet:
        os.chdir( dirname )
        os.system( 'cat train-preprocessed.txt test-preprocessed.txt > all-preprocessed.txt' )
        os.chdir( pwd )



posTypefileName = 'pos_tags'
dictionaryFileName = 'Chinese_train_pos.key'
trainXmlFileName = 'Chinese_train_pos.xml'
testXmlFileName = 'Chinese_test_pos.xml'
testAnswerFileName = 'ChineseLS.test.key'


if __name__ == '__main__':
    print 'wordTypeIndex:'
    buildWordTypeIndex(posTypefileName)
    for (k,v) in wordTypeIndex.items():
        print '%s: %s' % (k,v)
    print 'wordDictionary:'
    buidDictionary(dictionaryFileName)
    for (k, v) in wordDictionary.items():
        print '%s: %s' % (k, v)

    # 处理训练数据
    xmltree = parse(trainXmlFileName)
    #!! 不一定从根节点开始
    for lexeltNode in xmltree.getElementsByTagName('lexelt'):
        createTrainDataSet( lexeltNode )

    loadTestAnswer( testAnswerFileName )
#    for (k, v) in testAnswer.items():
#        print '%s: %s' % (k, v)

    # 处理测试数据
    xmltree = parse(testXmlFileName)
    for lexeltNode in xmltree.getElementsByTagName('lexelt'):
        createTestDataSet( lexeltNode )

    # 生成未scale的数据
#    for v in directorySet:
#        print v
    for dirname in directorySet:
        trainFileName = u'%s/train-preprocessed.txt' % dirname
        testFileName = u'%s/test-preprocessed.txt' % dirname
        allFileName = u'%s/all-preprocessed.txt' % dirname
        convertToUnScaledData( trainFileName )
        convertToUnScaledData( testFileName )
#        convertToCSV( trainFileName )
#        convertToCSV( testFileName )
#        convertToARFF( trainFileName )
        mergePreprocessedFile()
        convertToARFF( allFileName )
        convertToARFF( testFileName )














