#coding:utf8
import struct
import send
import bs_pb2

class MyException(Exception):
    def __init__(self, str):
        self.str = str
    def __str__(self):
        return self.str


def get_value(line, name):
    """
    [2015-11-19 17:24:55.866781] [pipeline/pipeline.cpp:155]        [tid=139963441620736] [indexname:search_online_ex][query:@(city,short_title,title,range,category,custombrand,brandname,poi_name) "湘王府酒店 阳光店"~1 @(city) "酒泉"|"全国" ][limit:3000][offset:0][ranker:1,score desc][combiner:][selectattr:dealid,poi_id,][indexweight:][fieldweight:(brandname,200)(category,50)(custombrand,50)(poi_name,100)(short_title,100)(title,1)][geoanchor:][filter:(0,cityid,0,0,9999,368,)(0,is_soldout,0,0,)(0,mergeid,0,0,)(0,status,1,4,)][204,230,4,21300,8,0,85][41,21839,21880][49,0,0][34]
    """
    beg = line.find("[%s:"%name)
    if beg == -1:
        return None
    beg += len("[%s:"%name)
    end = line.find("]", beg)
    if end == -1:
        return None

    result = line[beg:end]
    return result

def parse(line):
    offset = get_value(line, "offset")
    if offset is None:
        return None
    limit = get_value(line, "limit")
    if limit is None:
        return None
    indexname = get_value(line, "indexname")
    if indexname is None:
        return None
    querystr = get_value(line, "query")
    if querystr is None:
        return None
    ranker_str = get_value(line, "ranker")
    if ranker_str is None:
        return None
    #print "ranker:", ranker_str

    selectattr_str = get_value(line, "selectattr")
    if selectattr_str is None:
        return None
    #print "selectattr:", selectattr_str

    fieldweight_str = get_value(line, "fieldweight")
    if fieldweight_str is None:
        return None
    #print "fieldweight:", fieldweight_str

    filter_str = get_value(line, "filter")
    if filter_str is None:
        return None
    #print "filter_str:",filter_str

    combiner_str = get_value(line, "combiner")
    if combiner_str is None:
        return None

    indexweight_str = get_value(line, "indexweight")
    if indexweight_str is None:
        return None

    geoanchor_str = get_value(line, "geoanchor")
    if geoanchor_str is None:
        return None

    version_str = get_value(line, "version")
    if version_str is None:
        return None

    qid_str = get_value(line, "qid")
    if qid_str is None:
        return None

    debug_str = get_value(line, "debug")
    if debug_str is None:
        return None

    request = bs_pb2.IndexQueryReq()
    request.query.qid = qid_str
    request.query.offset = int(offset)
    request.query.limit = int(limit)
    request.query.indexname = indexname
    request.query.querystr = querystr

    try:
        version = int(version_str)
    except:
        version = 1
    request.query.version = version

    try:
        debug = int(debug_str)
    except:
        debug = 0
    request.query.debug = debug

    if ranker_str != "":
        try:
            ranker_type = ranker_str.split(",")[0]
            ranker_content = ranker_str.split(",")[1]
            request.query.ranker.type = int(ranker_type)
            request.query.ranker.content = ranker_content
        except None:
            pass
        #print request.query.ranker, type(request.query.ranker)
    if selectattr_str != "":
        for x in selectattr_str.split(","):
            if x.strip() == "":
                continue
            request.query.selectattrlist.append(x)
        #print "selectattr:", request.query.selectattrlist, type(request.query.selectattrlist)
    if fieldweight_str != "":
        try:
            for s in fieldweight_str.split(")"):
                if s.strip() == "":
                    continue
                s = s.replace("(", "")
                name = s.split(",")[0]
                weight = int(s.split(",")[1])
                fw = request.query.fieldweightlist.add()
                fw.name = name
                fw.weight = weight
        except None:
            pass
        #print request.query.fieldweightlist, type(request.query.fieldweightlist)
    if filter_str != "":
        try:
            for s in filter_str.split(")"):
                if s.strip() == "":
                    continue
                s = s.replace("(", "")
                _type = int(s.split(",")[0])
                if _type == 0:   #按属性字段过滤
                    field = s.split(",")[1]
                    if s.split(",")[2] == "1" :
                        exclude = True
                    else:
                        exclude = False
                    values = s.split(",")[3:]
                    values.remove("")
                    v = [int(x) for x in values]

                    f = request.query.filterlist.add()
                    f.type = _type
                    f.name = field
                    f.exclude = exclude
                    [f.values.append(x) for x in v]
                elif _type == 1:    #按整数范围过滤
                    field = s.split(",")[1]
                    if s.split(",")[2] == "1" :
                        exclude = True
                    else:
                        exclude = False
                    min = int(s.split(",")[3])
                    max = int(s.split(",")[4])

                    f = request.query.filterlist.add()
                    f.type = _type
                    f.name = field
                    f.exclude = exclude
                    f.min_value = min
                    f.max_value = max
                elif _type == 2:    #按浮点数范围过滤
                    field = s.split(",")[1]
                    if s.split(",")[2] == "1" :
                        exclude = True
                    else:
                        exclude = False
                    min = float(s.split(",")[3])
                    max = float(s.split(",")[4])

                    f = request.query.filterlist.add()
                    f.type = _type
                    f.name = field
                    f.exclude = exclude
                    f.f_min_value = min
                    f.f_max_value = max
        except None:
            pass
    #combiner_str = "2,dealid,@geodist asc"
    if combiner_str != "":
        #combiner:2,dealid,@geodist asc
        try:
            _type = int(combiner_str.split(",")[0])
            if _type == 1:
                groupby = combiner_str.split(",")[1]

                request.query.combiner.type = _type
                request.query.combiner.groupby = groupby
            elif _type == 2:
                groupby = combiner_str.split(",")[1]
                groupsortby = combiner_str.split(",")[2]

                request.query.combiner.type = _type
                request.query.combiner.groupby = groupby
                request.query.combiner.groupsort = groupsortby

            else:
                raise MyException("logic err:combiner type = %d"%_type)
        except None:
            pass

    if indexweight_str != "":
        try:
            weight = int(indexweight_str)
        except None:
            pass
        request.query.indexweight = weight

    if geoanchor_str != "":
        try:
            latitude_name = geoanchor_str.split(",")[0]
            longitude_name =  geoanchor_str.split(",")[1]
            latitude_value = float(geoanchor_str.split(",")[2])
            longitude_value = float(geoanchor_str.split(",")[3])

            request.query.geo_anchor.latitude_name = latitude_name
            request.query.geo_anchor.longitude_name = longitude_name
            request.query.geo_anchor.latitude_value = latitude_value
            request.query.geo_anchor.longitude_value = longitude_value
        except None:
            pass

    #print "\n"
    #request.query.filterlist = 1
    #request.query.combiner = 1
    #request.query.ranker = 1
    #request.query.selectattrlist = 1
    #request.query.indexweight = 1
    #request.query.fieldweightlist = 1
    #request.query.geo_anchor = 1
    return request

def make_bin_req(request):
    data = request.SerializeToString()
    result = struct.pack('2HI', 0, 1, len(data))
    result += data
    return result

def parse_res(res_data):
    try:
        result_pb = bs_pb2.IndexQueryRes()
        head_size = 8
        body = res_data[head_size:]
        result_pb.ParseFromString(body)
    except None:
        print " parse_res failed"
        return None
    return result_pb

if __name__ == "__main__":
    # line = """[2016-03-21 17:03:08.392474] [pipeline/pipeline.cpp:155]        [tid=140613904860928] [version:1][qid:][indexname:search_waimai_poi][query:@(wm_poi_name,tag1,category,wm_food_name) 芒果双皮奶 ][limit:3000][offset:0][debug:0][ranker:1,score desc][combiner:2,poi_id,poi_status asc][selectattr:poi_id,dealid,wm_poi_id,poi_status,][indexweight:][fieldweight:(category,100)(tag1,1)(wm_poi_name,100)][geoanchor:lat,lng,40.0078,116.491][filter:(0,cityid,0,0,9999,1,)(0,@region,0,1,)][67,53,2,1508,4,2,18][28,1660,1688][212,4,4][18]"""

    line = """[2016-07-28 16:29:23.132756] [pipeline/pipeline.cpp:155][tid=140633975756544] [version:1][qid:delay_5][indexname:search_online][query:@(category,custombrand,brandname,poi_name) 台球 @(city) 大连|全国 ][limit:10000][offset:0][debug:0][ranker:1,score1 desc][combiner:][selectattr:dealid,poi_id,][indexweight:][fieldweight:(brandname,200)(category,50)(custombrand,50)(poi_name,100)(short_title,100)(title,1)][geoanchor:][filter:(0,backcateid,0,293,3,5003,5310,6,84,)(0,cityid,0,0,65,9999,)(0,poi_cateid,1,389,)(0,is_soldout,0,0,)(0,mergeid,0,0,)(0,status,1,4,)][81,84,3,11730,29,26,131,0][13,12092,12105][4259,137,137][30]"""
    request = parse(line)
    print request

    bin_req = make_bin_req(request)
    sender = send.Sender()
    #status, bin_res = sender.send_sync("yf-dataapp-search-bs-staging04", 8712, bin_req, 10)
    status, bin_res = sender.send_sync("cq-dataapp-search-querybs-staging03", 8712, bin_req, 10)
    if status == "OK":
        #print "bin_res:", bin_res
        res = parse_res(bin_res)
        print "res:", res
