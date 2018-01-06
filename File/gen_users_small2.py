import sys, os

def PrintUsage():
    print 'Usage: appname idfile users_csv_file dest_file'

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 4:
        PrintUsage()
        sys.exit(-1)

    idFileName = sys.argv[1]
    userFileNmae = sys.argv[2]
    dstFileName = sys.argv[3]

    idSet = set()
    for line in open(idFileName, 'r').readlines():
        line = line.strip()
        if ( line != 'user_id' ):
            idSet.add(line)
    print 'Total %d user ids' % len(idSet)

    userFile = open(userFileNmae, 'r')
    dstFile = open(dstFileName, 'w')

    # copy the title line
    dstFile.write( userFile.readline() )

    for line in userFile.readlines():
        if ( line.split()[0] in idSet ):
            dstFile.write( line )
