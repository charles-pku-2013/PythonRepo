#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, time

if __name__ == '__main__':
    flgfile = "/tmp/running.flg"
    if os.path.exists(flgfile):
        print("Already running!")
        sys.exit(0)  # never run into finally

    try:
        flg = open(flgfile, "w")
        print("doing...")
        time.sleep(10)
    finally:
        print('Done...')
        if os.path.exists(flgfile):
            os.remove(flgfile)


