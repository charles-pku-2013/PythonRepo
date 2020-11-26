#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

if __name__ == '__main__':
    dir = "/tmp"
    for fname in os.listdir(dir):
        #  print(fname)
        path = os.path.join(dir, fname)
        if os.path.isdir(path):  
            print("%s is a directory" % path)
        elif os.path.isfile(path):  
            print("%s is a regular file" % path)
        else:
            print("%s is invalid file!" % path)


