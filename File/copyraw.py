#! /usr/bin/python

import sys, os

#for x in sys.argv:
#    print x
#print len(sys.argv)

jpgFiles = set()
jpgDir = ""
rawDir = ""
dstDir = ""

def PrintUsage():
    print 'Usage: %s jpg_folder raw_folder dst_folder' % sys.argv[0]

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


def Process():
    global jpgFiles
    global rawDir
    global dstDir
    cmd = 'find %s -type f -iname \"*.nef\"' % rawDir
# run cmd
    #  print jpgFiles
    fp = os.popen( cmd )
    count = 0
    for pathname in fp.readlines():
        pathname = pathname.rstrip()
        #  print pathname
        filename = os.path.basename(pathname)
        (mainName, ext) = os.path.splitext(filename)
        #  print mainName
        if mainName in jpgFiles:
            print 'copying %s' % pathname
            cmd = 'cp %s %s' % (pathname, dstDir)
            os.system(cmd)
            count = count + 1
    print "Totally copied %d files." % count



if __name__ == '__main__':
    if len(sys.argv) != 4:
        PrintUsage()
        sys.exit(-1)

    jpgDir = sys.argv[1]
    rawDir = sys.argv[2]
    dstDir = sys.argv[3]
    jpgDir = jpgDir + '/'
    rawDir = rawDir + '/'
    dstDir = dstDir + '/'

    if (not os.path.exists(jpgDir)) or (not os.path.isdir(jpgDir)):
        print 'Invalid jpg folder %s' % jpgDir
        sys.exit(-1)
    if (not os.path.exists(rawDir)) or (not os.path.isdir(rawDir)):
        print 'Invalid raw folder %s' % rawDir
        sys.exit(-1)
    if (not os.path.exists(dstDir)) or (not os.path.isdir(dstDir)):
        print 'Invalid raw folder %s' % dstDir
        sys.exit(-1)

    GetJpgFiles()
    Process()


#    for filename in jpgFiles:
#        print '%s' % filename
#    print len(jpgFiles)




