#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Examples:
# batch publish:
# python TpsDeploy/model_mgr.py --model knn/1 --target Cluster1 --cluster --batch 3
# single publish:
# python TpsDeploy/model_mgr.py --model knn/1 --target Cluster1/Host1
# check:
# python TpsDeploy/model_mgr.py --model knn/1 --target 127.0.0.1 --check

from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState
from kazoo.exceptions import BadVersionError
import os, sys, json, logging, getopt, time, socket
import ConfigParser

#http
import urllib
import urllib2

# model version num
model_version_num = 10

zk_servers = None
zk_path = None
cluster_iplist = None

model_name = None
model_ver = None
target = None
is_cluster = False
batch_size = 1
is_check = False
is_show = False
operate = None
is_rollback = False
retry_cnt = 0
agent_port = None

# model load check
request_url = 'http://HOST:8888/model/status/servable_all'

log = logging.getLogger(__name__)

def print_usage():
    print '1 Usage:'
    print '\t%s --model $model_name/$model_version --target $zk_path [--cluster] [--batch N]' % sys.argv[0]
    print ''
    print '--model:\t存储于Model Repository上的要发布模型信息，格式:模型名/版本号'
    print '--target:\t要发布的目标集群或主机，默认是单台主机，集群发布需要加 --cluster 参数，格式:/TPS/cluster_name/host_ip_or_name'
    print '--cluster:\t指定发布目标是集群 bool参数'
    print '--batch:\t集群发布时一次发布的主机数量，默认1'
    print '--rollback:\t版本回滚，删除线上比指定模型版本高的所有模型'
    print '--retry:\t失败后重试次数'
    print '--check:\t单机发布完成后检查是否成功'
    print '--show:\t显示指定主机上的模型信息'
    print ''
    print 'Examples:'
    print 'single host:'
    print '\t%s --model knn/1 --target Cluster1/Host1' % sys.argv[0]
    print 'batch cluster:'
    print '\t%s --model knn/1 --target Cluster1 --cluster --batch 10' % sys.argv[0]
    print 'check:'
    print '\t%s --model knn/1 --target $TPS_Host_IP --check' % sys.argv[0]
    print 'display model info on host:'
    print '\t%s --target cluster/host --show' % sys.argv[0]
    print ''
    print '2 Usage:'
    print '\t%s --target $cluster --operate $cmd' % sys.argv[0]
    print ''
    print '--target:\t目标集群ZK节点，参考配置文件server.conf cluster_node条目'
    print '--operate:\t创建/删除目标集群ZK节点，格式：add | delete'
    print ''
    print 'Examples:'
    print 'add cluster:'
    print '\t%s --target Cluster1 --operate add' % sys.argv[0]
    print 'delete cluster:'
    print '\t%s --target Cluster1 --operate delete' % sys.argv[0]
    print 'delete zk root path: --Do not recommend to use it'
    print '\t%s --target Cluster1 --operate zk_root' % sys.argv[0]
    print ''

def parse_args():
    global model_name
    global model_ver
    global target
    global is_cluster
    global batch_size
    global is_check
    global is_show
    global operate
    global is_rollback
    global retry_cnt
    try:
        if len(sys.argv) < 2:
            print_usage()
            sys.exit(0)

        opts, args = getopt.getopt(sys.argv[1:], "",
                ["help", "operate=", "model=", "target=", "cluster", "batch=", "check", "rollback", "show"])

        for opt, arg in opts:
            if opt in ("--model"):
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
            elif opt in ("--show"):
                is_show = True
            elif opt in ("--help"):
                print_usage()
                sys.exit(0)
            elif opt in ("--operate"):
                operate = str(arg)
            elif opt in ("--rollback"):
                is_rollback = True
            elif opt in ("--retry"):
                retry_cnt = int(arg)
            else:
                log.error('Invalid arg: %s' % opt)
                print_usage()
                sys.exit(-1)

        if is_show:
            if not target:
                log.error("target host must be set with --target")
                print_usage()
                sys.exit(-1)
            return

        if operate is None:
            if (not model_name) or (not model_ver):
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
    finally:
        if sock:
            sock.close()

def check_agent(host):
    try_cnt = 5 # ping 5 times, each wait 2s
    retval = False
    for i in range(try_cnt):
        retval = _check_agent(host)
        if retval:
            return retval
    return retval

def read_model_repo_config(client):
    global agent_port
    try:
        config_path = '/tfs/deploy_agent_config'
        data, _ = client.get(config_path)
        model_config_data = json.loads(data)
        agent_port = int(model_config_data['agent_port'])
    except Exception as ex: # re-throw to main
        raise Exception('read_model_repo_config() error %s' % ex)


class ZkNode:
    def __init__(self, client, path, model, ver):
        self.status = "not_set"
        self.client = client
        self.path = path
        self.model_name = model
        self.model_ver = ver
        self.data = {}
        self.version = 0

        @self.client.DataWatch(self.path)
        def OnDataChange(data, stat):
            # print 'OnDataChange data: %s' % data
            try:
                if self.status == 'not_set' or self.status == 'online' or self.status == 'deploy_failed' or self.status == 'file_not_exist':
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
        if not check_agent(self.path):
            self.status = "deploy_failed"
            return

        loop_flag = True
        retval = None

        while loop_flag:
            # first load data on zk node
            self._load_data()
            # then update data
            retval = self._set_data()
            if retval <= 0: # success or fail, > 0 retry
                loop_flag = False

        if retval == 0:
            self.status = "deploy_waiting"
        else:
            self.status = "deploy_failed"

    def _load_data(self):
        stat = None
        try:
            data, stat = self.client.get(self.path)
            self.data = json.loads(data)
        except:
            pass
        finally:
            if stat and (stat.version):
                self.version = stat.version


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

            if is_rollback:
                new_ver_list = []
                for ver_item in target_model['versions']:
                    if ver_item.has_key('version'):
                        if ver_item['version'] <= int(self.model_ver):
                            new_ver_list.append(ver_item)
                        else: # remove
                            log.info('Removing model %s/%s on %s' % (self.model_name, self.model_ver, self.path))
                ver_list = new_ver_list
            else: # publish routine
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

                # limit version count
                if len(ver_list) > model_version_num:
                    tmp_verlist = []
                    count = 0
                    ver_list.sort(key=lambda x:x['version'], reverse=True) # 按版本号从大到小进行排序
                    for item in ver_list:
                        if item['status'] == 'online':
                            if count < model_version_num:
                                tmp_verlist.append(item)
                            count = count + 1
                        else:
                            tmp_verlist.append(item)
                    tmp_verlist.sort(key=lambda x:x['version'])
                    target_model['versions'] = tmp_verlist

        # set data on zk
        try:
            # print 'updating %s, version = %d' % (self.path, self.version)
            self.client.set(self.path, json.dumps(self.data), version=self.version)
        except BadVersionError:
            log.warn('Version conflict when updating %s, try again...' % self.path)
            return 1
        except Exception as ex:
            log.error('Updating %s fail %s' % (self.path, str(ex)))
            return -1

        return 0

    def check_status(self):
        if not check_agent(self.path):
            self.status = "deploy_failed"
        return self.status

    def wait_finish(self):
        while True:
            time.sleep(1)
            self.check_status()
            if self.status == 'online':
                log.info('Successfully publish model %s/%s to %s' %
                        (self.model_name, self.model_ver, self.path))
                break
            elif self.status == 'deploy_failed':
                log.error('Failed to publish model %s/%s to %s!' %
                        (self.model_name, self.model_ver, self.path))
                break
            elif self.status == 'file_not_exist':
                log.error('Failed to publish model %s/%s to %s, because it not exist!' %
                        (self.model_name, self.model_ver, self.path))
                break
            else:
                continue
        return self.status

def publish_model_host(client, target):
    # print 'publish_model_host %s' % target
    log.info('Trying to publish to %s' % target)
    node = ZkNode(client, target, model_name, model_ver)
    node.set_data()
    return node.wait_finish()

def publish_model_host_with_retry(client, target):
    retval = publish_model_host(client, target)
    # retry if fail
    i = 0
    while retval == 'deploy_failed' and i < retry_cnt:
        log.info('Publish to %s fail, try again...' % target)
        retval = publish_model_host(client, target)
        i = i + 1

def publish_model_batch(client, path_list, fail_list):
    for path in path_list:
        try:
            retval = publish_model_host(client, path)
            if retval == 'deploy_failed':
                fail_list.append(path)
        except Exception as ex:
            log.error(str(ex))

def publish_model_batch_with_retry(client, path_list):
    fail_list = []
    publish_model_batch(client, path_list, fail_list)
    # retry if fail
    i = 0
    while len(fail_list) and i < retry_cnt:
        log.info('Publish to %s fail, try again...' % str(fail_list))
        path_list = fail_list
        fail_list = []
        publish_model_batch(client, path_list, fail_list)
        i = i + 1


def publish_model_batch_parallel(client, path_list, fail_list):
    pending_list = []
    work_que = []

    for path in path_list:
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
            status = node.check_status()
            if status == 'online':
                log.info('Successfully publish model %s/%s to %s' %
                        (node.model_name, node.model_ver, node.path))
            elif status == 'deploy_failed':
                log.error('Failed to publish model %s/%s to %s!' %
                        (node.model_name, node.model_ver, node.path))
                fail_list.append(node.path)
            elif status == 'file_not_exist': # 不需要重试
                log.error('Failed to publish model %s/%s to %s, because it not exist!' %
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


def publish_model_batch_parallel_with_retry(client, path_list):
    fail_list = []
    publish_model_batch_parallel(client, path_list, fail_list)
    # retry if fail
    i = 0
    while len(fail_list) and i < retry_cnt:
        log.info('Publish to %s fail, try again...' % str(fail_list))
        path_list = fail_list
        fail_list = []
        publish_model_batch_parallel(client, path_list, fail_list)
        i = i + 1


def publish_model(client):
    global target
    global zk_path
    # check target exists
    zk_node = zk_path + target
    if not client.exists(zk_node):
        raise Exception('Cluster %s does not exist on omi server!' % zk_node)
        #if is_cluster:
        #    raise Exception('Cluster %s does not exist on omi server!' % zk_node)
        #else:
        #    log.warn('%s does not exist on omi server, now creating it!' % zk_node)
        #    client.ensure_path(zk_node)

    _children = client.get_children(zk_node)
    children = []
    for child in _children:
        path = zk_node + '/' + child
        stat = client.exists(path)
        if stat and (not stat.ephemeralOwner):
            children.append(path)

    if len(children) > 0:
        # not a leaf/host
        if not is_cluster:
            raise Exception('%s is a cluster node, you have to specify --cluster' % zk_node)
        if batch_size > 1:
            publish_model_batch_parallel_with_retry(client, children)
        else:
            publish_model_batch_with_retry(client, children)
    else:
        # single host
        publish_model_host_with_retry(client, zk_node)

# tfs load model check
def load_check(host, model, version):
    global request_url
    #load check
    try:
        check_url = request_url.replace('HOST', host)
        request = urllib2.Request(check_url)
        response = urllib2.urlopen(request)
        code = response.getcode()
        if code != 200:
            log.error("request check load model faild! host:%s, errono:%s" % (host, str(code)))
            return -1
        body  = response.read().decode()
        #print body
        data = json.loads(body)
        modelInfos = data['modelStatusInfo']
        if len(modelInfos) == 0:
            print 'get response body:modelStatusInfo faild! host:%s' % host
            #log.error("get response body:modelStatusInfo faild! host:%s" % host)
            return -2
        available = 1
        for model_info in modelInfos:
            model_name = model_info['name']
            if model_name == model:
                model_versions = model_info['modelVersionStatus']
                #print model_versions
                if len(model_versions) != 0:
                    #print model_versions
                    for modelversion in model_versions:
                        model_version = modelversion['version']
                        #print model_version,version
                        if model_version == str(version):
                            status = modelversion['state']
                            #print status
                            if status == 'AVAILABLE':
                                available = 0
                else:
                    print 'get response body:modelStatusInfo faild! host:%s" % host'
                    #log.error("get response body:modelStatusInfo faild! host:%s" % host)
                    break
            #else:
            #    print '%s %s' % (model_name, model)

        if available == 0:
            return 0
        else:
            return 2
    #except urllib2.HTTPError, e:
    #except urllib2.URLError, e:
    except Exception as e:
        log.error('happen error:%s' % str(e))
        return 1

def do_check(host, model, version):
    #load check
    ret = load_check(host, model, version)
    if ret != 0:
        return ret
    # score check
    return 0

def read_conf(target):
    global zk_servers
    global zk_path
    global cluster_node
    global cluster_iplist

    config_file = 'server.conf'
    cf = ConfigParser.ConfigParser()
    if not os.path.isfile(config_file):
        raise Exception('%s is missing!' % config_file)
    cf.read(config_file)
    cluster_nodes = cf.get('clusters', 'cluster_node')
    cluster_list = cluster_nodes.split(',')
    # get cluster_node
    if target.find('/') > 0:
        cluster_node = target.split('/')[0]
    else:
        cluster_node = target
    # check cluster_node
    if cluster_node not in cluster_list:
        log.error('Invalid target param, target:%s!' % target)
        return -1
    # get zkhosts
    zk_servers = cf.get(cluster_node, 'zk_hosts')
    zk_path = cf.get(cluster_node, 'zk_dir')
    cluster_iplist = cf.get(cluster_node, 'iplist').split(',')

    return 0

# operate: add delete zk_root
def zk_clusterNode():
    # read conf
    global target
    global operate
    global is_check
    clusternode = target
    conf_ret = read_conf(clusternode)
    if conf_ret != 0:
        log.error('Invalid target param, clusternode:%s!' % clusternode)
        return -1
    # create node
    zk_client = KazooClient(hosts = zk_servers)
    zk_client.start()

    #  operate
    zk_node = zk_path + clusternode
    if operate == 'zk_root':
        zk_node = zk_path
        operate = 'delete'
    exist_flag = zk_client.exists(zk_node)
    if operate == 'delete':
        if exist_flag:
            zk_client.delete(zk_node,recursive=True)
            log.info('Delete cluster:%s node success!' % clusternode)
            if is_check:
                zk_client.delete(zk_path,recursive=True)
                log.info('Delete zk_path:%s node success!' % clusternode)
        else:
            log.info('cluster:%s node not exist!' % clusternode)
    elif operate == 'add':
        if not exist_flag:
            zk_client.ensure_path(zk_node)
        for host in cluster_iplist:
            new_node = zk_node + '/' + host
            if not zk_client.exists(new_node):
                zk_client.create(new_node, b'')

        # check host node
        children = zk_client.get_children(zk_node)
        if len(children) != len(cluster_iplist):
            log.error('Create cluster:%s node failed!' % clusternode)
            zk_client.stop()
            return -1
        log.info('create cluster:%s node success!' % clusternode)

    else:
        log.error('operate cluster:%s node cmd:%s not exist!' % (operate, clusternode))
        zk_client.stop()
        return -1

    zk_client.stop()
    return 0


def show_node_info(client):
    zk_node = zk_path + target
    data, _ = client.get(zk_node)
    model_cfg = json.loads(data)
    print json.dumps(model_cfg, indent=4)


if __name__ == '__main__':
    client = None
    try:
        #logging.basicConfig(level = logging.INFO)
        #logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',level=logging.INFO,
        #        datefmt='%a, %d %b %Y %H:%M:%S',
        #        filename='model_manager.log',
        #        filemode='w')
        # pathname | filename
        logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',level=logging.INFO)
        # model deploy cmd
        parse_args()

        #log.info('zk_servers: %s' % zk_servers)
        log.info('model_name: %s' % model_name)
        log.info('model_ver: %s' % model_ver)
        log.info('target: %s' % target)
        log.info('is_cluster: %s' % is_cluster)
        log.info('is_rollback: %s' % is_rollback)
        log.info('batch_size: %s' % batch_size)
        log.info('retry_cnt: %d' % retry_cnt)
        log.info('is_check: %s' % is_check)

        # operate cluster node
        if operate is not None:
            ret = zk_clusterNode()
            if ret == 0:
                sys.exit(0)
            else:
                sys.exit(-1)

        # check
        if is_check:
            check_ret = do_check(target, model_name, model_ver)
            if check_ret == 0:
                log.info('Model %s/%s load ok.' % (model_name, model_ver))
                sys.exit(0)
            else:
                log.error('Model %s/%s load failed.' % (model_name, model_ver))
                sys.exit(-1)

        # read conf
        conf_ret = read_conf(target)
        if conf_ret != 0:
            log.error('Invalid target param, clusternode:%s!' % clusternode)
            sys.exit(-1)

        client = KazooClient(hosts = zk_servers)
        client.start()

        if is_show:
            show_node_info(client)
        else:
            read_model_repo_config(client)
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

