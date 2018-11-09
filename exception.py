#! /usr/bin/python
# -*- coding: utf-8 -*-

from MTtest.MTSearchApi import MTSearch
from MTtest.MTSearchApi.ttypes import *
#from ttypes import *
#from MTSearch import *
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

import json, sys
from pprint import pprint


def json2dict(js, ret):
    for (key, val) in js.iteritems():
        ret[key.encode('utf-8')] = val.encode('utf-8')


def main():
    t_sock = TSocket.TSocket('dx-dataapp-mf-haiwaitrunk02', 8026)
    t_transport = TTransport.TFramedTransport(t_sock)
    t_protocol = TBinaryProtocol.TBinaryProtocol(t_transport)
    client = MTSearch.Client(t_protocol)
    t_transport.open()

    req = SearchQueryReq()
    ifName = ''

    with open('/tmp/test.json') as data_file:
        jsData = json.load(data_file)

    for (key, val) in jsData.iteritems():
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
        result = client.MTSearchPoi(req);
    elif ifName == u'MTSearchDeal':
        result = client.MTSearchDeal(req);
    elif ifName == u'MTMultiSearch':
        result = client.MTMultiSearch(req);
    elif ifName == u'MTMultiSearchDealPoi':
        result = client.MTMultiSearchDealPoi(req);


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Just print(e) is cleaner and more likely what you want,
        # but if you insist on printing message specifically whenever possible...
        if hasattr(e, 'message'):
            sys.stderr.write('Exception: %s\n' % e.message)
        else:
            sys.stderr.write('Exception: %s\n' % e)


# catch exception in function, add info and re-throw to main
def _check_agent(host):
    sock = None
    try:
        host = host.split('/')[-1]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.settimeout(2) # 10s
        sock.sendto('ping', (host, agent_port))
        data, addr = sock.recvfrom(1024)
        if not data:
            log.error('model_agent does not start properly on host %s' % host)
            return False
        return True
    except socket.timeout:
        log.error('model_agent is not running on host %s' % host)
        return False
    except Exception as ex:
        raise Exception('_check_agent error: %s' % ex)
    finally:
        if sock:
            sock.close()


"""
def main():
    test()
    sys.exit(0)

    t_sock = TSocket.TSocket('dx-dataapp-mf-haiwaitrunk02', 8026)
    #t_sock= TSocket.TSocket('dx-dataapp-mf-haiwaitrunk01', 8026)
    t_transport = TTransport.TFramedTransport(t_sock)
    t_protocol = TBinaryProtocol.TBinaryProtocol(t_transport)
    client = MTSearch.Client(t_protocol)
    t_transport.open()

#[I 170914 16:13:43 19799 savelog_handler.cpp:573] traceid=756899037339708062 userid= uuid=E7F420AD4E9E6CAA4EE7FFEC300B1E42E992C9F5A687BA5F7B6C38CAC048A932 total_result=0 global_id=756899037339708062 traceid=756899037339708062 query= category= location=47.52993,-122.26999 orderby= reqid=10020 cityid=2399 offset=0 limit=20 filter=distance:3000,poi_cateid:L20557, counter= control=__is_leaf:1,__return_score:1,hasGroup:1,results:1, source= uuid=E7F420AD4E9E6CAA4EE7FFEC300B1E42E992C9F5A687BA5F7B6C38CAC048A932 user_id= session_time= ip= ext_data=__global_id:756899037339708062,__referer:10.72.161.156:43013,request_source:overseas,sort_type:NEARESTINTRAVEL, if_name=MTSearchPoi card_time= qs_time= sphinx_time=14 type=leaf_deal_result total_cost=15 strategy= plugins=1:0,2:0,5:14,8:0,61:0,62:0,71:0,72:0,310:0,555:0,666:0,1090:0,1091:0  fromcache=0, is_update=0 task=0x7fa7f4004de0:1505376823268693 dt=1

####### query
    keywords = ''
    #keywords = '旅游'
    city = ''
    cityid = 2355
    control = {"hasGroup" : "1", "results" : "1"}
    counter = {}
    exdata = {"request_source" : "overseas"}
    filters = {"poi_cateid" : "L20969"}
    limit = 4
    location = '11.957808,121.93089'
    offset = 0
    reqid = 10020
    #  location = '36.076764061123335,120.423919753684'
    orderby = '@geodist:asc'
    #filters = {'distance':'300000', 'poi_cateid':'L20557'}

    query = SearchQueryReq(keywords, city, '', cityid, reqid, offset, limit, location, orderby, filters, counter, control, exdata, 0)

    print type(query)

    result = client.MTSearchPoi(query)
    #result = client.MTMultiSearch(query)
    print result.status
    print result
    for gres in result.group_res:
        res = gres.matches
        for item in res:
            print item
"""
