#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
处理单个请求文件, 请求文件内是json数组，每个数组元素代表一个请求
"""

from MTtest.MTSearchApi import MTSearch
from MTtest.MTSearchApi.ttypes import *
#from ttypes import *
#from MTSearch import *
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from pprint import pprint

import json, sys
#  reload(sys)
#  sys.setdefaultencoding('utf-8')

g_SvrHost = ''
g_SvrPort = 8026
g_InputFile = ''
g_OutputFile = ''


def json2dict(js, ret):
    for (key, val) in js.iteritems():
        ret[key.encode('utf-8')] = val.encode('utf-8')


def main():
    global g_SvrHost
    global g_SvrPort
    global g_InputFile
    global g_OutputFile

    t_sock = TSocket.TSocket(g_SvrHost, g_SvrPort)
    t_transport = TTransport.TFramedTransport(t_sock)
    t_protocol = TBinaryProtocol.TBinaryProtocol(t_transport)
    client = MTSearch.Client(t_protocol)
    t_transport.open()

    if len(g_InputFile):
        fInput = open(g_InputFile, 'r')
    else:
        fInput = sys.stdin

    if len(g_OutputFile):
        fOutput = open(g_OutputFile, 'w')
    else:
        fOutput = sys.stdout

    jsData = json.load(fInput)
    #  print len(jsData)
    for jsItem in jsData:
        #  print jsItem
        req = SearchQueryReq()
        ifName = ''
        for (key, val) in jsItem.iteritems():
            #  print '%s = %s' % (key, val)
            if key == u'category':
                req.category = val.encode('utf-8')
            elif key == u'city':
                req.city = val.encode('utf-8')
            elif key == u'orderby':
                req.orderby = val.encode('utf-8')
            elif key == u'key_words':
                req.key_words = val.encode('utf-8')
            elif key == u'location':
                req.location = val.encode('utf-8')
            elif key == u'id':
                req.id = val
            elif key == u'cityid':
                req.cityid = val
            elif key == u'offset':
                req.offset = val
            elif key == u'limit':
                req.limit = val
            elif key == u'opt':
                req.opt = val
            elif key == u'filter':
                if val != None:
                    req.filter = dict()
                    json2dict(val, req.filter)
            elif key == u'counter':
                if val != None:
                    req.counter = dict()
                    json2dict(val, req.counter)
            elif key == u'control':
                if val != None:
                    req.control = dict()
                    json2dict(val, req.control)
            elif key == u'exdata':
                if val != None:
                    req.exdata = dict()
                    json2dict(val, req.exdata)
            elif key == u'if_name':
                ifName = val.encode('utf-8')

        #  print req
        result = SearchMultiRes()
        if ifName == u'MTSearchPoi':
            result = client.MTSearchPoi(req)
        elif ifName == u'MTSearchDeal':
            result = client.MTSearchDeal(req)
        elif ifName == u'MTMultiSearch':
            result = client.MTMultiSearch(req)
        elif ifName == u'MTMultiSearchDealPoi':
            result = client.MTMultiSearchDealPoi(req)

        fOutput.write('%s\n' % result)
        for gr in result.group_res:
            if gr.type == "poiid_list":
                sys.stderr.write('%d\n' % int(gr.exinfo["count"]))


if __name__ == '__main__':
    #  try:
    if len(sys.argv) <= 1:
        sys.stderr.write('Usage: %s server:port [inputfile] [outputfile]\nEg: python main.py dx-dataapp-mf-trunk01:8026 req.json\n' % sys.argv[0])
        exit(0)

    strSvr = sys.argv[1]
    sep = strSvr.find(':')
    if sep == 0:
        raise Exception('server name/addr cannot be empty!')
    g_SvrHost = strSvr[:sep]
    if sep != -1:
        g_SvrPort = int(strSvr[sep + 1:])

    if len(sys.argv) > 2:
        g_InputFile = sys.argv[2]
    if len(sys.argv) > 3:
        g_OutputFile = sys.argv[3]

    main()

    #  except Exception as e:
        #  sys.stderr.write('Exception: %s\n' % e)


