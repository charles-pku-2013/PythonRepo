#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Examples:
# batch publish:
# python TpsDeploy/model_mgr.py --omi 127.0.0.1 --model knn/1 --target /TPS/Cluster1 --cluster --batch 3
# single publish:
# python TpsDeploy/model_mgr.py --omi 127.0.0.1 --model knn/1 --target /TPS/Cluster1/Host1
# check:
# python TpsDeploy/model_mgr.py --model knn/1 --target 127.0.0.1 --check

from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState
from enum import Enum
import sys, json, logging, getopt, time

omi_servers = None
model_name = None
model_ver = None
target = None
is_cluster = False
batch_size = 1
is_check = False

log = logging.getLogger(__name__)

def print_usage():
    print 'Usage:'
    print '\t%s --omi $server --model $model_name/$model_version --target $zk_path [--cluster] [--batch N]' % sys.argv[0]
    print ''
    print '--omi:\t\t指定Online Model Information zookeeper server，与zkCli参数格式相同。'
    print '--model:\t存储于Model Repository上的要发布模型信息，格式:模型名/版本号'
    print '--target:\t要发布的目标集群或主机，默认是单台主机，集群发布需要加 --cluster 参数，格式:/TPS/cluster_name/host_ip_or_name'
    print '--cluster:\t指定发布目标是集群 bool参数'
    print '--batch:\t集群发布时一次发布的主机数量，默认1'
    print '--check:\t单机发布完成后检查是否成功'
    print ''
    print 'Examples:'
    print 'single host:'
    print '\t%s --omi 127.0.0.1 --model knn/1 --target /TPS/Cluster1/Host1' % sys.argv[0]
    print 'batch cluster:'
    print '\t%s --omi 127.0.0.1 --model knn/1 --target /TPS/Cluster1 --cluster --batch 10' % sys.argv[0]
    print 'check:'
    print '\t%s --model knn/1 --target $TPS_Host_IP' % sys.argv[0]
    print ''

def parse_args():
    global omi_servers
    global model_name
    global model_ver
    global target
    global is_cluster
    global batch_size
    global is_check

    try:
        if len(sys.argv) < 2:
            print_usage()
            sys.exit(0)

        opts, args = getopt.getopt(sys.argv[1:], "",
                ["help", "omi=", "model=", "target=", "cluster", "batch=", "check"])

        for opt, arg in opts:
            if opt in ("--omi"):
                omi_servers = str(arg).split(',')
            elif opt in ("--model"):
                lst = str(arg).split('/')
                if len(lst) != 2:
                    raise Exception('--model should be in format model_name/model_version')
                model_name = lst[0]
                model_ver = lst[1]
            elif opt in ("--target"):
                target = str(arg)
            elif opt in ("--cluster"):
                is_cluster = True
            elif opt in ("--batch"):
                batch_size = int(arg)
            elif opt in ("--check"):
                is_check = True
            elif opt in ("--help"):
                print_usage()
                sys.exit(0)
            else:
                log.error('Invalid arg: %s' % opt)
                print_usage()
                sys.exit(-1)

        if not omi_servers:
            if not is_check:
                log.error("Online model information servers must be set with --omi")
                print_usage()
                sys.exit(-1)
        elif (not model_name) or (not model_ver):
            log.error("Model info must be set with --model in form of model_name/model_version")
            print_usage()
            sys.exit(-1)
        elif not target:
            log.error("target host/cluster must be set with --target")
            print_usage()
            sys.exit(-1)
        elif (not is_cluster) and (batch_size > 1):
            log.error("--batch must be used together with --cluster")
            print_usage()
            sys.exit(-1)
        elif batch_size < 1:
            log.error("Invalid batch_size! --batch must be above 0")
            print_usage()
            sys.exit(-1)

    except getopt.GetoptError as err:
        log.error("%s" % err)
        print_usage()
        sys.exit(-1)


class ZkNode:
    def __init__(self, client, path, model, ver):
        self.status = "not_set"
        self.client = client
        self.path = path
        self.model_name = model
        self.model_ver = ver
        self.data = {}

        @self.client.DataWatch(self.path)
        def OnDataChange(data, stat):
            # print 'OnDataChange data: %s' % data
            try:
                if self.status == 'not_set' or self.status == 'online' or self.status == 'deploy_failed':
                    return

                found = False
                config_data = json.loads(data)
                models = config_data["models"]
                for m_itr in range(0, len(models)):
                    model_name = models[m_itr]["model"]
                    if model_name == self.model_name:
                        for v_itr in range(0, len(models[m_itr]["versions"])):
                            model_version = models[m_itr]["versions"][v_itr]["version"]
                            model_status = models[m_itr]["versions"][v_itr]["status"]
                            if model_version == int(self.model_ver):
                                found = True
                                self.status = model_status
                                # print 'status = %s' % self.status

                if not found:
                    self.status = 'deploy_failed'

            except Exception as ex:
                log.error("Invalid data response: %s" % ex)
                self.status = 'deploy_failed'

    def set_data(self):
        lock = self.client.Lock(self.path, 'model_mgr')
        with lock:
            # load data on zk node
            data, stat = self.client.get(self.path)
            try:
                self.data = json.loads(data)
            except:
                pass
            # then update data
            self._set_data()


    def _set_data(self):
        model_list = []
        ver_info = {'version' : int(self.model_ver), 'status' : 'deploy_waiting'}

        if (self.data.has_key('models')):
            model_list = self.data['models']
        else:
            self.data['models'] = model_list
        # print model_list

        target_model = {}
        for model_cfg in model_list:
            if model_cfg.has_key('model') and model_cfg['model'] == self.model_name:
                target_model = model_cfg
                break

        if not target_model:
            # target model not exist
            target_model['model'] = self.model_name
            target_model['versions'] = []
            target_model['versions'].append(ver_info)
            model_list.append(target_model)
        else:
            # target model exists, check version
            ver_list = []
            if target_model.has_key('versions'):
                ver_list = target_model['versions']
            else:
                target_model['versions'] = ver_list

            found_ver = False
            for ver_item in target_model['versions']:
                if ver_item.has_key('version') and ver_item['version'] == int(self.model_ver):
                    found_ver = True
                    log.warn('Model %s/%s already exists on %s, now replacing it.'
                            % (self.model_name, self.model_ver, self.path))
                    ver_item['status'] = "deploy_waiting"
                    break

            if not found_ver:
                ver_list.append(ver_info)

        self.client.set(self.path, json.dumps(self.data))
        self.status = "deploy_waiting"

    def wait_finish(self):
        while True:
            time.sleep(1)
            if self.status == 'online':
                log.info('Successfully publish model %s/%s to %s' %
                        (self.model_name, self.model_ver, self.path))
                break
            elif self.status == 'deploy_failed':
                log.error('Failed to publish model %s/%s to %s!' %
                        (self.model_name, self.model_ver, self.path))
                break
            else:
                continue


def publish_model_host(client, target):
    # print 'publish_model_host %s' % target
    log.info('Trying to publish to %s' % target)
    node = ZkNode(client, target, model_name, model_ver)
    node.set_data()
    node.wait_finish()


def publish_model_batch(client, children):
    for child in children:
        path = target + '/' + child
        try:
            publish_model_host(client, path)
        except Exception as ex:
            log.error(str(ex))


def publish_model_batch_parallel(client, children):
    pending_list = []
    work_que = []

    for child in children:
        path = target + '/' + child
        pending_list.append(path)
    pending_list.sort(reverse = True)
    # for item in pending_list:
        # print item

    # init work_que
    for i in range(min(batch_size, len(pending_list))):
        _target = pending_list.pop()
        log.info('Trying to publish to %s' % _target)
        node = ZkNode(client, _target, model_name, model_ver)
        node.set_data()
        work_que.append(node)

    while len(work_que):
        time.sleep(1)
        work_que_tmp = []
        for node in work_que:
            if node.status == 'online':
                log.info('Successfully publish model %s/%s to %s' %
                        (node.model_name, node.model_ver, node.path))
            elif node.status == 'deploy_failed':
                log.error('Failed to publish model %s/%s to %s!' %
                        (node.model_name, node.model_ver, node.path))
            else:
                work_que_tmp.append(node) # not finish

        num_done = len(work_que) - len(work_que_tmp)
        work_que = work_que_tmp
        for i in range(min(len(pending_list), num_done)):
            _target = pending_list.pop()
            log.info('Trying to publish to %s' % _target)
            node = ZkNode(client, _target, model_name, model_ver)
            node.set_data()
            work_que.append(node)


def publish_model(client):
    # check target exists
    if not client.exists(target):
        if is_cluster:
            raise Exception('Cluster %s does not exist on omi server!' % target)
        else:
            log.warn('%s does not exist on omi server, now creating it!' % target)
            client.ensure_path(target)
    children = client.get_children(target)
    if len(children) > 0:
        # not a leaf/host
        if not is_cluster:
            raise Exception('%s is a cluster node, you have to specify --cluster' % target)
        if batch_size > 1:
            publish_model_batch_parallel(client, children)
        else:
            publish_model_batch(client, children)
    else:
        # single host
        publish_model_host(client, target)


def do_check():
    log.error('Check routine remain TODO')


if __name__ == '__main__':
    client = None
    try:
        logging.basicConfig(level = logging.INFO)

        parse_args()

        log.info('omi_servers: %s' % omi_servers)
        log.info('model_name: %s' % model_name)
        log.info('model_ver: %s' % model_ver)
        log.info('target: %s' % target)
        log.info('is_cluster: %s' % is_cluster)
        log.info('batch_size: %s' % batch_size)
        log.info('is_check: %s' % is_check)

        if is_check:
            do_check()
            sys.exit(0)

        client = KazooClient(hosts = omi_servers)
        client.start()

        publish_model(client)

        client.stop()
        sys.exit(0)

    except KeyboardInterrupt:
        log.warn('Terminated by user.')
        if client:
            client.stop()
        sys.exit(0)

    except Exception as ex:
        log.error('Exception: %s' % ex)
        if client:
            client.stop()
        sys.exit(-1)

