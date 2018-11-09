#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, time

UDP_IP = "127.0.0.1"
UDP_PORT = 10080
MESSAGE = "Hello, World!"

if __name__ == '__main__':
    sock = None
    try:
        print "UDP target IP:", UDP_IP
        print "UDP target port:", UDP_PORT
        print "message:", MESSAGE

        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.settimeout(5)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print data

    finally:
        if sock:
            sock.close()
