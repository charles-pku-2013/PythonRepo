#!/usr/bin/python
# -*- coding: UTF-8 -*-

import argparse
import json
from agent2server.configservice.ttypes import *
from agent2server.configservice.ConfigService import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

def parse_parameters():
    parser = argparse.ArgumentParser('This is a client which can reg meta info with cs server')
    parser.add_argument('-H', type=str, default='localhost', help='server ip')
    parser.add_argument('-p', type=int, default=9988, help='server port')
    parser.add_argument('-r', type=str, default='', help='read req from which file')
    parser.add_argument('--appkey', type=str, default='', help='meta appkey')
    parser.add_argument('--env', type=str, default='', help='meta env')
    parser.add_argument('--file', type=str, default='', help='meta file')
    return parser.parse_args()


def initReq(args):
    meta_get_req = MetaItem()
    meta_get_req.appkey = args.appkey
    meta_get_req.environment = args.env
    with open(args.file, 'r') as f:
        j_req = json.load(f)
        if j_req.has_key('val'):
            meta_get_req.content = json.dumps(j_req, indent=2, sort_keys=False)
            meta_get_req.content = meta_get_req.content.decode('unicode-escape').encode('utf8')
            print meta_get_req.content
        else:
            raise Exception('val is missing')
            return
    desc = Description()
    desc.desc = "屏蔽"
    rdinfo = []
    rd = RdInfo()
    rd2 = RdInfo()
    rd3 = RdInfo()
    rd4 = RdInfo()
    rd.name = "maoningxiang"
    rd.phone = "18610905842"
    rd2.name = "anlongfei"
    rd2.phone = "123456"
    rd3.name = "sunchao14"
    rd3.phone = "123456"
    rd4.name = "wangdachuan"
    rd4.phone = "123456"
    rdinfo = []
    rdinfo.append(rd)
    rdinfo.append(rd2)
    rdinfo.append(rd3)
    rdinfo.append(rd4)
    desc.rdinfo = rdinfo
    return (True, meta_get_req, desc)
'''
def initReqFromFile(path):
    with open(path, 'r') as f:
        j_req = json.load(f)
        if j_req.has_key('cinfo'):
            #consumer info
            consumer_info = AConsumerInfo()
            if j_req['cinfo'].has_key('appkey'):
                consumer_info.appkey = j_req['cinfo']['appkey']
            else:
                raise Exception('appkey is empty')
            if j_req['cinfo'].has_key('environment'):
                consumer_info.environment = j_req['cinfo']['environment']
            else:
                consumer_info.environment = 'test'
            if j_req['cinfo'].has_key('tag'):
                consumer_info.tag = j_req['cinfo']['tag']
            else:
                consumer_info.tag = ''
            #remote conf sev
            remote_conf_sev = ARemoteConfSev()
            if j_req['cinfo'].has_key('remote_info') and\
                    j_req['cinfo']['remote_info'].has_key(host) and\
                    j_req['cinfo']['remote_info'].has_key(port):
                remote_conf_sev.host = j_req['cinfo']['remote_info']['host']
                remote_conf_sev.port = j_req['cinfo']['remote_info']['port']
            else:
                remote_conf_sev.host = ''
                remote_conf_sev.port = 0
            consumer_info.remote_info = remote_conf_sev
            #extension?

            meta_get_req = AMetaGetReq()
            meta_get_req.cinfo = consumer_info
            if j_req.has_key('is_use_group'):
                meta_get_req.is_use_group = j_req['is_use_group']
            #else:
            #    meta_get_req.is_use_group = False
            if j_req.has_key('host'):
                meta_get_req.host = j_req['host']
            else:
                meta_get_req.host = ''
            if j_req.has_key('container'):
                meta_get_req.container = j_req['container']
            else:
                meta_get_req.container = ''
            return (True, meta_get_req)
        else:
            raise Exception('cinfo is missing')
    return (False, AMetaGetReq())
'''

if '__main__' == __name__:
    args = parse_parameters()

    req = {}
    desc = {}
    init_success = False
    init_res = initReq(args)
    req = init_res[1]
    desc = init_res[2]
    init_success = init_res[0]


    try:
        socket = TSocket.TSocket(args.H, args.p)
        #transport = TTransport.TFramedTransport(socket)
        transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        #protocol = TCompactProtocol.TCompactProtocol(transport)
        client = Client(protocol)

        transport.open()
        j_res = client.RegisterMeta(req, desc)
    except Thrift.TException,tx:
        print 'reg meta failed!'
        print 'test : %s' % (tx.message)
    else:
        print (j_res)

