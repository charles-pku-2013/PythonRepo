#coding:utf8
import os,sys,time
import parse
import send
import logger
import json
import parse_result
import hashlib
import getopt

#  JSON_NAME = "data.json"

DEFAULT_BS_PORT = 8712
DEFAULT_BS_PROXY_PORT = 8912
DEFAULT_TIMEOUT = 180000

def print_usage():
    sys.stderr.write('Usage: python %s -h[host] $bsHost -l[logfile] $logfile -o[output] $outfile\n\n' % sys.argv[0])
    sys.stderr.write('Example:\n')


#  def parse_host(strHostPort, strHost, nPort): # NOTE!!! string int 是常量，不可以通过参数修改
def parse_host(strHostPort):
    pos = strHostPort.rfind(":")
    if 0 == pos:
        raise Exception('Invalid host!')
    elif -1 == pos:
        strHost = strHostPort
        if strHost.find("proxy") != -1:
            nPort = DEFAULT_BS_PROXY_PORT
        else:
            nPort = DEFAULT_BS_PORT
        sys.stderr.write('port not specified, use default %d\n' % nPort)
    else:
        strHost = strHostPort[:pos]
        nPort = int(strHostPort[pos + 1:])
        if nPort <= 0 or nPort > 65535:
            raise Exception('Invalid host port range!')
    return (strHost, nPort)



if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print_usage()
        sys.exit(-1)

    try:
        # := 表示要带参数
        opts, args = getopt.getopt(sys.argv[1:], "h:l:o:", ["host=", "logfile=", "output="])
    except getopt.GetoptError as err:
        sys.stderr.write('%s\n' % str(err))
        print_usage()
        sys.exit(-1)

    try:
        strHostPort = None
        strHost = None
        nPort = 0
        strOutput = None
        strLogfile = None
        fLogFile = None
        fOutput = None

        # parse args
        for opt, arg in opts:
            if opt in ("-h", "--host"):
                strHostPort = arg
                strHost, nPort = parse_host(strHostPort)
                #  print 'host = %s port = %d' % (strHost, nPort)   # debug
            elif opt in ("-l", "--logfile"):
                strLogfile = arg
            elif opt in ("-o", "--output"):
                strOutput = arg
            else:
                assert False, "unhandled option %s" % opt

        if strHostPort == None:
            sys.stderr.write('host not specified!\n')
            sys.exit(-1)

        if strLogfile == None or strLogfile == "-":
            fLogFile = sys.stdin
            sys.stderr.write('logfile not specified, use stdin.\n')
        else:
            fLogFile = open(strLogfile, 'r')

        if strOutput == None or strOutput == "-":
            fOutput = sys.stdout
            sys.stderr.write('output file not specified, use stdout.\n')
        else:
            fOutput = open(strOutput, 'w')

        # send request
        #  sys.exit(0)
        sys.stderr.write('Requesting bs server %s:%d\n' % (strHost, nPort))
        for i, line in enumerate(fLogFile):
            line = line.strip()
            if len(line) == 0:
                continue
            #  print 'line = %s' % line
            request = parse.parse(line)
            if request == None:
                sys.stderr.write("Parse log fail!")
                continue
            fOutput.write('Request is:\n%s\n' % request)
            bin_req = parse.make_bin_req(request)
            sender = send.Sender()
            status, bin_res = sender.send_sync(strHost, nPort, bin_req, DEFAULT_TIMEOUT)
            if status == "OK":
                sys.stderr.write('Success!\n')
                res = parse_result.parse_result(bin_res)
                fOutput.write('Result is:\n%s\n' % res)
            else:
                sys.stderr.write("Request server error! status = %s\n" % status)

    except Exception as ex:
        sys.stderr.write('Exception: %s\n' % str(ex))




"""
    try:
        with open(JSON_NAME, 'r') as f:
            json_content = json.loads(f.read())
    except ValueError:
        print "Decoding Json has failed"

    #print hashlib.md5("abc").hexdigest()
    #print hashlib.md5("fuck 123").hexdigest()
    # m= hashlib.md5()
    #m.update("abc")
    #print m.hexdigest()
    #print m.digest()
    #print json_content["logInfoFileName"]
    with open(json_content["logInfoFileName"]) as logFile:
        for i, line in enumerate(logFile):
            try:
                request = parse.parse(line)
                bin_req = parse.make_bin_req(request)
                sender = send.Sender()
                status, bin_res = sender.send_sync(json_content["bsServerAddr"], json_content["bsServerPort"],
                                               bin_req, json_content["requestTimeout"])
                if status == "OK":
                    #res = parse.parse_res(bin_res)
                    res = parse_result.parse_result(bin_res)
                    # \n
                    #print hashlib.md5(res+"\n").hexdigest(),"\t",request.query.querystr
                    #print request.query.querystr
                    print res
                    #print hashlib.md5(res+"\n").hexdigest(),"\t",request.query.querystr
                    #print res
            except Exception, e:
                print "Decoding Json has failed"
"""
