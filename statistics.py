#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, operator

# 吃	Accuracy = 47.8261% (11/23) (classification)
if __name__ == '__main__':
    L = []
    for line in sys.stdin:
        print line
        match = re.match( '(.*)\tAccuracy = (.*)% (.*) \(classification\)', line )
        L.append( (match.group(1), match.group(2), match.group(3)) )
    L.sort( key=operator.itemgetter(1) )        #!! 指定排序关键字

    for (v1,v2,v3) in L:
        print '%s:\t\t\t%s%% %s' % (v1,v2,v3)   #!! 打印百分数

    SUM = sum( [ float(v[1]) for v in L ] )
    avgAccuracy = SUM / float(len(L))
    print 'Average accuracy is: %s%%' % avgAccuracy