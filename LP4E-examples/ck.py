#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

openFileCmd = 'open -a xcode '

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: ck fileExt string'
        sys.exit(-1)

    fileExt = sys.argv[1]
    searchStr = sys.argv[2]
    opts = sys.argv[3:]

    afterLineN = 5
    for i in range(len(opts)):
        if opts[i][0:2] == '-A':
            afterLineN = int(opts[i][2:])
            opts[i] = ''

    opts = [ x for x in opts if len(x) ]

#   print opts
    cmdStr = "find -L . -iname \'*.%s\' | xargs egrep -n -A%d " % (fileExt, afterLineN)
    for x in opts:
        cmdStr += "%s " % x
    cmdStr += "\'%s\'" % searchStr
    print cmdStr

    res = os.popen( cmdStr ).read().split('--')
    for i in range(len(res)):
        res[i] = res[i].strip()

    res = [ x for x in res if len(x) ]

    fileList = dict()
    for i in range(len(res)):
        line = res[i].splitlines()[0]
        loc = line.find( '.%s' % fileExt )
        filename = line[:loc+len(fileExt.strip())+1]
        fileList[i+1] = filename
        print '\n%s No.%d: %s %s' % ('-'*30, i+1, filename, '-'*30)
        print res[i]

    fileToOpen = set()
    if len(fileList):
        print 'Enter Number of file you want to open:'
        reply = sys.stdin.readline().strip()
        if not len(reply):
            sys.exit(0)
        if reply == 'a':
            fileToOpen = sorted(set(fileList.itervalues()))
        else:
            for x in reply.split():
                if not x.isdigit():
                    sys.exit(0)
                fileToOpen.add( fileList[int(x)] )
    else:
        sys.exit(0)


    for x in fileToOpen:
        openFileCmd += '%s ' % x
    os.system( openFileCmd )

#   print openFileCmd

#   print fileList

"""
    for x in res:
        print '#'*20
        print x
    print len(res)
"""
"""
    print fileExt
    print searchStr
    print opts
"""


