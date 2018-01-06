#coding:utf8
import socket
import parse
import struct
import bs_pb2
import sys
import select
import thread
import threading
import time
import traceback
import runnable

class Sender(runnable.Runnable):
    def __init__(self):
        self.epoll = select.epoll()
        self.rpc_timeout = 1
        self.fd_sock_hash = {}

    def set_rpc_timeout(self, timeout):
        self.rpc_timeout = timeout
    
    def recv_async_data(self, sock_data):
        def recv_data(sock_data, expect):
            try:
                sock = sock_data["sock"]
                while expect > 0:
                    data = sock.recv(expect)
                    if not data:
                        return "half"
                    sock_data["res_data"] += data
                    expect -= len(data)
                return "all"
            except socket.error,err:   #[Errno 11] Resource temporarily unavailable
                #logging.debug(sys.exc_info)
                #print err, type(err)
                #traceback.print_exc()
                return "half"
            except:
                return "error"

        head_size = 8
        sock = sock_data["sock"]
        recved = sock_data["res_data"].__len__()
        
        if recved < head_size:
            state = recv_data(sock_data, head_size - recved)
            if state == "half" or state == "error":
                #print "recv head half"
                return state
            elif state == "all":
                #print "recv head all"
                x = struct.unpack("2HI", sock_data["res_data"])
                body_size = x[2]
                sock_data["body_size"] = body_size + head_size
        
        body_size = sock_data["body_size"]

        state = recv_data(sock_data, body_size - recved)
        #print "recv body", state
        return state
            
    def handler_recv_async_data(self, sock, data):
        """
            called while sock has input data. 
            it should be implemented by user according to the transport protocol
            args:
                sock is the socket object
                data is a dict, you can store some data in it to reuse while you reenter this function on the same fd
            return: 
                "all" if all data received successful
                "half" if only received part of data
                "error" if an error occured during the data receiving 
        """
        raise NotImplementedError
    def send_sync(self, host, port, request, timeout = 1):
        try:
            result = ""

            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            address = (host, port)
            sock.connect(address)
            sock.settimeout(timeout)

            sock.sendall(request)
           
            head_size = 8
            recved = 0
            while recved < head_size:
                data = sock.recv(head_size - recved) 
                if not data: 
                    break
                result += data
                recved += len(data)
            
            x = struct.unpack("2HI", result)
            buf_size = x[2]
            
            recved = 0
            while recved < buf_size:
                data = sock.recv(buf_size - recved) 
                if not data:
                    break
                result += data
                recved += len(data)

        except socket.timeout:
            return ("TIMEOUT", None)
        except None:
            return ("ERROR", None)
        return ("OK", result)

    def send_no_result(self, host, port, request):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            address = (host, port)
            sock.connect(address)
            sock.sendall(request)
            sock.close()
        except :
            print sys.exc_info()
            traceback.print_exc()
            
    def send_async(self, host, port, request, callback, **args):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            address = (host, port)
            sock.connect(address)
            sock.setblocking(0)

            sock.sendall(request)

            fd = sock.fileno()
            
            sock_data = args
            sock_data["has_recved"] = False
            sock_data["send_time"] = time.time()
            sock_data["sock"] = sock
            sock_data["callback"] = callback
            sock_data["res_data"] = ""
            sock_data["usr_data"] = {}
            self.fd_sock_hash[fd] = sock_data

            self.epoll.register(fd, select.EPOLLIN | select.EPOLLERR)
        except socket.error, e:
            print "get a socket.error:", e.__str__()
    
    def work(self):
        events = self.epoll.poll(0.01)
        for event in events:
            fd = event[0]
            flag = event[1]

            if flag == select.EPOLLIN:
                sock_data = self.fd_sock_hash[fd]

                #在第一次接收数据的时候计算cost值
                if not sock_data["has_recved"]:
                    recv_time = time.time()
                    send_time = sock_data["send_time"]
                    sock_data["cost"] = (recv_time - send_time) * 1000
                    sock_data["has_recved"] = True

                state = self.recv_async_data(sock_data)
                if state == "all":
                    self.handler_recv_all(fd)
                elif state == "half":
                    self.handler_recv_half(fd)
                elif state == "error":
                    self.handler_error(fd)
            
            elif flag == select.EPOLLERR:
                self.handler_error(fd)
            
        #check timeout
        timeout_time = time.time() - self.rpc_timeout
        for fd in self.fd_sock_hash.keys():
            send_time = self.fd_sock_hash[fd]["send_time"]
            has_recved = self.fd_sock_hash[fd]["has_recved"]
            if send_time < timeout_time and not has_recved :
                self.handler_timeout(fd)
    
    
    def handler_recv_all(self, fd):
        args = self.fd_sock_hash[fd]
        args["status"] = "OK"

        callback = args.pop("callback")
        sock = args.pop("sock")
        args.pop("has_recved")
        args.pop("usr_data")

        apply(callback, [], args)
        
        self.epoll.unregister(fd)
        self.fd_sock_hash.pop(fd)
        sock.close()

    def handler_recv_half(self, fd):
        pass
    
    def handler_timeout(self, fd):
        args = self.fd_sock_hash[fd]
        args["status"] = "TIMEOUT"

        callback = args.pop("callback")
        sock = args.pop("sock")
        args.pop("has_recved")
        args.pop("usr_data")

        apply(callback, [], args)
        
        self.epoll.unregister(fd)
        self.fd_sock_hash.pop(fd)
        sock.close()

    def handler_error(self, fd):
        #print "handler_error" 
        args = self.fd_sock_hash[fd]
        args["status"] = "ERROR"
        
        callback = args.pop("callback")
        sock = args.pop("sock")
        args.pop("has_recved")
        args.pop("usr_data")

        apply(callback, [], args)
        
        self.epoll.unregister(fd)
        self.fd_sock_hash.pop(fd)
        sock.close()

def callback_func(**attrs):
    print "\ncallback_func runs:"
    for x in attrs:
        print x, attrs[x]
    pass

if __name__ == "__main__":
    sender = Sender()
    sender.set_rpc_timeout(2)
    sender.start()

    request = bs_pb2.IndexQueryReq()
    request.query.version = 1  
    request.query.qid = "test"
    request.query.offset = 0
    request.query.limit = 1000
    request.query.indexname = "search_online"
    request.query.querystr = "火锅"

    req = parse.make_bin_req(request)

    res = sender.send_async("dataapp-test06", 8712, req, callback = callback_func, reqid = 66, tag= "test")
    #print res

    time.sleep(10)
