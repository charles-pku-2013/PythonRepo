#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://kazoo.readthedocs.io/en/latest/basic_usage.html

from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState
import sys, json, logging, time

def build_json(_dict):
    encodedjson = json.dumps(_dict)
    return encodedjson

def fake_nodes(client):
    for i in range(10):
        path = '/TPS/Cluster1/Host' + str(i)
        client.ensure_path(path)

def test_set_data(client, path, _data):
    if client.exists(path):
        data, stat = client.get(path)
        print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))
        # print type(stat)
        # print dir(stat)
        # print stat
        stat = client.set(path, _data)
        print 'After set, version is %s' % stat.version
    else:
        print "zkpath %s does not exist!" % path


def sess_listener(state):
    if state == KazooState.CONNECTED:
        print "Connection established!"
    elif state == KazooState.LOST:
        print "Connection lost!"
    elif state == KazooState.SUSPENDED:
        print "Connection suspended!"
    else:
        print "Connection state is %s" % state


def test_json(jsobj):
    print dir(jsobj)
    print type(jsobj)
    print jsobj


class ZkNode:
    def __init__(self, client, path):
        self.client = client
        self.path = path

        @self.client.DataWatch(self.path)
        def OnDataChange(data, stat):
            print("ZkNode Version: %s, data: %s" % (stat.version, data.decode("utf-8")))
            #  print 'ZkNode path = %s' % self.path


def test_change_data(client, path):
    if client.exists(path):
        found = False
        data, stat = client.get(path)
        config_data = json.loads(data)
        models = config_data["models"]
        for m_itr in range(0, len(models)):
            model_name = models[m_itr]["model"]
            if model_name == 'knn':
                for v_itr in range(0, len(models[m_itr]["versions"])):
                    model_version = models[m_itr]["versions"][v_itr]["version"]
                    model_status = models[m_itr]["versions"][v_itr]["status"]
                    if model_version == 1:
                        print 'Found!!!'
                        found = True
                        models[m_itr]["versions"][v_itr]["status"] = 'online'
                        # models[m_itr]["versions"][v_itr]["status"] = 'deploy_failed'

        if not found:
            print 'Not Found!!!'
        else:
            client.set(path, json.dumps(config_data))
            data, stat = client.get(path)
            print 'After set data: %s' % data
    else:
        print "zkpath %s does not exist!" % path


def test_lock(client):
    lock = client.Lock('/TPS/Cluster1/Host1', sys.argv[1])
    print 'Trying to acquire the lock.'
    with lock:
        print 'Lock acquired, doing work...'
        time.sleep(10)
    print 'Job done, release the lock.'


if __name__ == '__main__':
    client = None
    try:
        logging.basicConfig() # ??

        model_cfg = {"Model" : "KNN", "Version" : 1, "Flag" : "Online"}
        model_cfg_json = build_json(model_cfg)
        #  print type(model_cfg_json)
        #  print model_cfg_json
        #  dir(KazooState)
        #  sys.exit(0)

        #  help(KazooClient)
        """
        __init__(self, hosts='127.0.0.1:2181', timeout=10.0, client_id=None, handler=None, default_acl=None, auth_data=None, read_only=None, randomize_hosts=True, connection_retry=None, command_retry=None, logger=None, **kwargs)
         |      :param hosts: Comma-separated list of hosts to connect to
         |                    (e.g. 127.0.0.1:2181,127.0.0.1:2182,[::1]:2183).
         |      :param timeout: The longest to wait for a Zookeeper connection.
        """
        client = KazooClient(hosts='127.0.0.1:2181')

        client.add_listener(sess_listener)

        # @client.DataWatch(path)
        # def watch_node(data, stat):
            # print "data change detected!"
            # print dir(stat)
            # print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))

        client.start()

        # fake_nodes(client)
        # sys.exit(0)

        #  @client.ChildrenWatch("/TPS/Cluster1")
        #  def watch_children(children):
            #  print("Children are now: %s" % children)

        #  @client.DataWatch("/TPS/Cluster1")
        #  def watch_node(data, stat):
            #  print("Version: %s, data: %s" % (stat.version, data.decode("utf-8")))

        # node = ZkNode(client, "/TPS/Cluster1/Host1") # 刚建立时也会触发data watch
        # nodeSet = dict()
        # nodeSet[node.path] = node
        #  nodeSet["/TPS/Cluster1/Host1"] = ZkNode(client, "/TPS/Cluster1/Host1")
        # print len(nodeSet)
        # print nodeSet
        #  sys.stdin.readline()

        #  client.ensure_path("/my/favorite") # Recursively create a path if it doesn’t exist.
        #  client.create("/my/favorite/node", b"a value") # requires the path to it to exist first, unless the makepath option is set to True.
        # with open('/tmp/test.json', 'r') as f:
            # model_cfg_json = json.load(f)
            # test_json(model_cfg_json)
        # model_cfg_json = json.dumps(model_cfg_json)
        # test_set_data(client, "/TPS/Cluster1/Host1", model_cfg_json)

        # test_lock(client)
        # client.stop()
        # sys.exit(0)

        test_change_data(client, "/TPS/Cluster1/Host0")
        test_change_data(client, "/TPS/Cluster1/Host1")
        test_change_data(client, "/TPS/Cluster1/Host2")
        test_change_data(client, "/TPS/Cluster1/Host3")
        test_change_data(client, "/TPS/Cluster1/Host4")
        test_change_data(client, "/TPS/Cluster1/Host5")
        test_change_data(client, "/TPS/Cluster1/Host6")
        test_change_data(client, "/TPS/Cluster1/Host7")
        test_change_data(client, "/TPS/Cluster1/Host8")
        test_change_data(client, "/TPS/Cluster1/Host9")

        # sys.stdin.readline()
        client.stop()
        sys.exit(0)

    except KeyboardInterrupt:
        print('Terminated by user.')
        if client:
            client.stop()
        sys.exit(0)

    except Exception as ex:
        print('Exception: %s' % ex)
        if client:
            client.stop()
        sys.exit(-1)

