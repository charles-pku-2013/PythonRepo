#! /usr/bin/python

import sys, os


def PrintUsage():
    print 'Usage: open filename(s)'


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc <= 1:
            PrintUsage()
            sys.exit(-1)
    
    B = bytearray()		# like stringstream StringBuilder sstream
    B.extend( 'sublime_text'.encode() )
    for i in range(1, argc):
            B.extend( (' %s' % sys.argv[i]).encode() )
    B.extend( ' 2>/dev/null &'.encode() )
    
    cmdStr = str(B)
    # print cmdStr
    os.system( cmdStr )
