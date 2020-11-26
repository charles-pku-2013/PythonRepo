#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState
from kazoo.exceptions import BadVersionError
import os, sys, json, logging, time


if __name__ == '__main__':
    client = None
    try:
        logging.basicConfig()

        client = KazooClient(hosts='127.0.0.1:2181')
        client.start()

        path = "/tfs/tfs_clusters/_sync_scp"

        if not client.exists(path):
            client.create(path)

        tmp_node = os.path.join(path, 'tmp_node1')
        client.create(tmp_node, '', None, True)
        children = client.get_children(path)
        print 'N children: %d' % len(children)
        print 'Press enter to delete tmp node...'
        cmd = sys.stdin.readline()
        client.delete(tmp_node)
        print 'Press enter to end...'
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

