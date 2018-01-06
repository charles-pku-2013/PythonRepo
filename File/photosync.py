#! /usr/bin/python

import sys, os

#for x in sys.argv:
#    print x
#print len(sys.argv)

jpgFiles = set()
jpgDir = ""
rawDir = ""

def PrintUsage():
    print 'Usage: %s jpg_folder raw_folder' % sys.argv[0]

def GetJpgFiles():
    global jpgFiles
    global jpgDir
    cmd = 'find %s -type f -iname \"*.jpg\"' % jpgDir
#    print cmd
    fp = os.popen( cmd )
    for line in fp.readlines():
        line = line.rstrip()
        filename = os.path.basename(line)
        (mainName, ext) = os.path.splitext(filename)
        if ext == ".jpg" or ext == ".JPG":
            jpgFiles.add( mainName )


def ProcessRawDir():
    global jpgFiles
    global rawDir
    cmd = 'find %s -type f -iname \"*.nef\"' % rawDir
# run cmd
    fp = os.popen( cmd )
    count = 0
    for pathname in fp.readlines():
        pathname = pathname.rstrip()
#        print pathname
        filename = os.path.basename(pathname)
        (mainName, ext) = os.path.splitext(filename)
        if mainName not in jpgFiles:
            print 'removing %s' % pathname
            os.remove(pathname)
            count = count + 1
    print "Totally removed %d files." % count



if __name__ == '__main__':
    if len(sys.argv) != 3:
        PrintUsage()
        sys.exit(-1)

    jpgDir = sys.argv[1]
    rawDir = sys.argv[2]
    jpgDir = jpgDir + '/'
    rawDir = rawDir + '/'

    if (not os.path.exists(jpgDir)) or (not os.path.isdir(jpgDir)):
        print 'Invalid jpg folder %s' % jpgDir
        sys.exit(-1)
    if (not os.path.exists(rawDir)) or (not os.path.isdir(rawDir)):
        print 'Invalid raw folder %s' % rawDir
        sys.exit(-1)

    GetJpgFiles()
    ProcessRawDir()


#    for filename in jpgFiles:
#        print '%s' % filename
#    print len(jpgFiles)




