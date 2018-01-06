import threading
import sys

class NotImplement(Exception):
    def __init__(self, desc="unknow"):
        self.desc = desc
    def __str__(self):
        return "function (%s) is not implement" %self.desc

class Runnable:
    def __init__(self):
        self.need_stop = False

    def work(self):
        raise NotImplement("work")
    def run(self):
        while not self.need_stop:
            self.work()
    def stop(self):
        self.need_stop = True
        print "stoping................"
    def start(self):
        self.need_stop = False
        t = threading.Thread(target = self.run)
        t.daemon = True
        t.start()
