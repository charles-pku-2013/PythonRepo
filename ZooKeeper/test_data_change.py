#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kazoo.client import KazooClient
from kazoo.client import DataWatch
from kazoo.protocol.states import KazooState
from kazoo.exceptions import BadVersionError
import sys, json, logging, time


def OnDataChange(data, stat):
    print("ZkNode Version: %s, data: %s" % (stat.version, data.decode("utf-8")))


if __name__ == '__main__':
    client = None
    try:
        logging.basicConfig()

        client = KazooClient(hosts='127.0.0.1:2181')
        client.start()

        DataWatch(client, "/tfs/tfs_clusters/ht_gpu/11.7.157.11", OnDataChange)

        sys.stdin.readline()
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

