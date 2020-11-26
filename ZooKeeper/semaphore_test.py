#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState
from kazoo.exceptions import BadVersionError
import sys, json, logging, time

def init_semaphore(zkc, path, name, n):
    semaphore = None
    try:
        # first, try to del path
        zkc.delete(path)
        semaphore = zkc.Semaphore(path, name, n)
    except:
        print('%s already exists' % path)
        # path exists and in use
        data, stat = zkc.get(path)
        print data
        n = int(data)
        semaphore = zkc.Semaphore(path, name, n)

    return semaphore



if __name__ == '__main__':
    client = None
    try:
        logging.basicConfig()

        client = KazooClient(hosts='127.0.0.1:2181')
        client.start()

        path = "/tfs/tfs_clusters/semaphores"

        # first, try to delete it

        # semaphore = client.Semaphore(path, sys.argv[1], 2)
        semaphore = init_semaphore(client, path, sys.argv[1], 2)
        if not semaphore:
            print "init semaphore fail!"
            sys.exit(-1)

        with semaphore:  # blocks waiting for lock acquisition
            print 'Test 1'
            print semaphore.lease_holders()
            cmd = sys.stdin.readline()

        with semaphore:  # blocks waiting for lock acquisition
            print 'Test 2'
            print semaphore.lease_holders()
            cmd = sys.stdin.readline()

        client.stop()
        sys.exit(0)

    except KeyboardInterrupt:
        print('Terminated by user.')
        if client:
            client.stop()
        sys.exit(0)

    except Exception as ex:
        print('Exception: %s' % ex)
        if client:
            client.stop()
        sys.exit(-1)

