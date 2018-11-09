#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 10080

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
# sock.settimeout(10)

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    # print "received message:", data, " from ", addr
    print 'received msg %s from %s' % (data, addr)
    sock.sendto('running', addr)
