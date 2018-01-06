#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

filename = u'明月千里寄相思.txt'
#print type(filename)

F = open( filename )
#print F.encoding
#print sys.stdin.encoding

content = [ line.strip().decode('utf-8') for line in F.readlines() ]

"""
for line in content:
    print line
print type( content[0] )
"""

F1 = open('copy.txt', 'w')
for line in content:
    F1.write( '%s\n' % line.encode('GB2312') )