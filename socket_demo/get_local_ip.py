#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

if __name__ == '__main__':
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        print 'local ip: %s' % sock.getsockname()[0]
        print 'local port: %s' % sock.getsockname()[1]
        # print(sock.getsockname()[0])
        # for item in sock.getsockname():
            # print item
    finally:
        if sock:
            sock.close()
