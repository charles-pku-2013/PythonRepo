import struct
import bs_pb2
import json
import sys

def parse_attr_data(attr_name, attr_type, attr_data):
    
    # define type
    DATATYPE_U32 = 0x06
    DATATYPE_U64 = 0x08
    DATATYPE_FLOAT = 0x0d
    DATATYPE_DOUBLE = 0x0e
 
    DATATYPE_VECTOR_U32 = 0x16
    DATATYPE_VECTOR_U64 = 0x18
    DATATYPE_VECTOR_FLOAT = 0x1d
    DATATYPE_VECTOR_DOUBLE = 0x1e

    DATATYPE_STR = 0x20

    attr_list = {}
    index = 0
    for i in range(len(attr_type)):
        type = attr_type[i]
        #print "type=", type
        if type == DATATYPE_U32:
            #print "DATATYPE_U32"
            attr = {attr_name[i] : (struct.unpack('I',attr_data[index:index+4]))[0]}
            attr_list.update(attr)
            index += 4
        elif type == DATATYPE_U64:
            attr = {attr_name[i] : (struct.unpack('Q',attr_data[index:index+8]))[0]}
            attr_list.update(attr)
            index += 8
        elif type == DATATYPE_FLOAT:
            attr = {attr_name[i] : (struct.unpack('f',attr_data[index:index+4]))[0]}
            attr_list.update(attr)
            index += 4
        elif type == DATATYPE_DOUBLE:
            attr = {attr_name[i] : (struct.unpack('d',attr_data[index:index+8]))[0]}
            attr_list.update(attr)
            index += 8
        elif type == DATATYPE_VECTOR_U32:
            data_format = 'I'
            size = (struct.unpack('I',attr_data[index:index+4]))[0]
            index += 4
            if size>0:
                dataformat = repr(size)+'I'
                attr = {attr_name[i] : struct.unpack(dataformat,attr_data[index:index+size*4])}
                attr_list.update(attr)
                index += size*4
        elif type == DATATYPE_VECTOR_U64:
            data_format = 'I'
            size = (struct.unpack('I',attr_data[index:index+4]))[0]
            index += 4
            if size>0:
                dataformat = repr(size)+'Q'
                attr = {attr_name[i] : struct.unpack(dataformat,attr_data[index:index+size*8])}
                attr_list.update(attr)
                index += size*8
        elif type == DATATYPE_VECTOR_FLOAT:
            data_format = 'I'
            size = (struct.unpack('I',attr_data[index:index+4]))[0]
            index += 4
            if size>0:
                dataformat = repr(size)+'f'
                attr = {attr_name[i] : struct.unpack(dataformat,attr_data[index:index+size*4])}
                attr_list.update(attr)
                index += size*4
        elif type == DATATYPE_VECTOR_DOUBLE:
            data_format = 'I'
            size = (struct.unpack('I',attr_data[index:index+4]))[0]
            index += 4
            if size>0:
                dataformat = repr(size)+'d'
                attr = {attr_name[i] : struct.unpack(dataformat,attr_data[index:index+size*8])}
                attr_list.update(attr)
                index += size*8
        elif type == DATATYPE_STR:
            data_format = 'I'
            size = (struct.unpack('I',attr_data[index:index+4]))[0]
            index += 4
            if size>0:
               dataformat=repr(size)+'s'
               attr = {attr_name[i] : struct.unpack(dataformat,attr_data[index:index+size*1])}
               attr_list.update(attr)
               index += size
        else:
            sys.stderr.write("Not supported type %x\n" % type)
    #print attr_list
    return attr_list

def parse_result(result):
    result_pb = bs_pb2.IndexQueryRes()
    head_size = 8
    body = result[head_size:]
    result_pb.ParseFromString(body)
    
    json_obj = []
    json_obj.append({"status": result_pb.result.status})
    json_obj.append({"qid": result_pb.result.qid})
    
    if result_pb.result.HasField("tag"):
        json_obj.append({"tag": result_pb.result.tag})

    attr_type = []
    attr_name = []
    
    attrmetalist = []
    json_obj.append({"attrmetalist": attrmetalist})
    for attr_meta in result_pb.result.attrmetalist:
        attr_type.append(attr_meta.type)
        attr_name.append(attr_meta.name)
        attrmetalist.append({"type": attr_meta.type, "name": attr_meta.name})

    recordlist = []
    json_obj.append({"recordlist": recordlist})
    sys.stderr.write("qid = %s, nResults = %d\n" % (result_pb.result.qid, len(result_pb.result.recordlist)))
    #  print result_pb.result.qid, len(result_pb.result.recordlist)
    for record in result_pb.result.recordlist:
        record_result = {}
        recordlist.append(record_result)
        record_result["id"] = record.id
        record_result["weight"] = record.weight
        if record.HasField("attrdata"):
            attr_data = record.attrdata
            if not attr_data:
                sys.stderr.write("warning: no attr_data\n")
                continue
        
            attr_list = parse_attr_data(attr_name, attr_type, attr_data)
            record_result["attrdata"] = attr_list

    return json.dumps(json_obj, indent=2, sort_keys=True)
