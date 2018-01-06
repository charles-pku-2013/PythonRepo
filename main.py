#! /usr/bin/python
# -*- coding: utf-8 -*-

from MTtest.MTSearchApi import MTSearch
from MTtest.MTSearchApi.ttypes import *
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from pprint import pprint
import json, sys, glob
#  reload(sys)
#  sys.setdefaultencoding('utf-8')


def connect(host, port):
    t_sock = TSocket.TSocket(host, port)
    t_transport = TTransport.TFramedTransport(t_sock)
    t_protocol = TBinaryProtocol.TBinaryProtocol(t_transport)
    client = MTSearch.Client(t_protocol)
    t_transport.open()
    return client


#  @static_var("count", 0)
def addOutReq(outReq, jsItem):
    addOutReq.count += 1
    jsItem.pop(u'LogNO', None)
    jsItem[u'ReqNO'] = addOutReq.count
    outReq.append(jsItem)
# attribute must be initialized
addOutReq.count = 0


def json2dict(js, ret):
    for (key, val) in js.iteritems():
        ret[key.encode('utf-8')] = val.encode('utf-8')


def process(client, reqFile, fRes, outReq):
    maxNResults = 0
    maxResult = None
    maxReq = None

    fReq = open(reqFile, 'r')
    jsData = json.load(fReq)
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
        else:
            raise Exception('Invalid if_name %' % ifName)

        if len(result.group_res):
            nResults = int(result.group_res[0].exinfo["count"])
            if nResults >= 20:
                fRes.write('%s\n' % result)
                addOutReq(outReq, jsItem)
                print '%s has %d results.' % (reqFile, nResults)
                return
            elif nResults > maxNResults:
                maxNResults = nResults
                maxResult = result
                maxReq = jsItem

    if maxNResults:
        fRes.write('%s\n' % maxResult)
        addOutReq(outReq, jsItem)
        print '%s has %d results.' % (reqFile, maxNResults)
    else:
        print '%s has 0 result.' % reqFile



if __name__ == '__main__':
    try:
        if len(sys.argv) < 5:
            sys.stderr.write('Usage: %s server:port reqDir resFile outReqFile\nEg: python main.py yf-dataapp-mf-meishitrunk01:8026 data/10023 data/res.txt data/sample_req.json\n' % sys.argv[0])
            exit(0)

        # parse args
        strSvr = sys.argv[1]
        sep = strSvr.find(':')
        if sep == 0:
            raise Exception('server name/addr cannot be empty!')
        svrHost = strSvr[:sep]
        svrPort = 8026
        if sep != -1:
            svrPort = int(strSvr[sep + 1:])
        #  print '%s : %d' % (svrHost, svrPort)

        strReqFiles = sys.argv[2]
        strResFile = sys.argv[3]
        strOutReqFile = sys.argv[4]

        client = connect(svrHost, svrPort)

        strReqFiles += '/req*.json'
        reqFileList = glob.glob(strReqFiles)
        #  print reqFileList
        print 'Totally %d req file to process.' % len(reqFileList)

        fRes = open(strResFile, 'w')
        outReq = []
        for reqFile in reqFileList:
            print 'Processing %s...' % reqFile
            try:
                process(client, reqFile, fRes, outReq)
            except Exception as ex:
                sys.stderr.write('Exception: %s\n' % ex)

        with open(strOutReqFile, 'w') as out:
            pprint(json.dumps(outReq), stream=out)

    except Exception as e:
        sys.stderr.write('Exception: %s\n' % e)

