#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
下一版，这次上线前改不好就用现在的版本
每次运行用subcmd指定要执行的任务如 publish check operate
Examples:
# 发布模型
model_mgr.py publish --model ... --target ...
# check
model_mgr.py check --model ... --target ...
# operate
model_mgr.py op add --target ...
model_mgr.py op delete --target ...
model_mgr.py op root --target ...

"""

from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState
from kazoo.exceptions import BadVersionError
import sys, json, logging, getopt, time
import ConfigParser

#http
import urllib
import urllib2

# model version num
model_version_num = 3

zk_servers = None
zk_path = None
cluster_iplist = None

model_name = None
model_ver = None
target = None
is_cluster = False
batch_size = 1
is_rollback = False
retry_cnt = 0

# model load check
request_url = 'http://HOST:8888/model/status/servable_all'

log = logging.getLogger(__name__)


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

                # limit version count 3
                if len(ver_list) > 3:
                    tmp_verlist = sorted(ver_list,key=lambda x:x['version'])
                    if tmp_verlist[0]['status'] == 'online':
                        tmp_verlist.pop(0)
                        target_model['versions'] = tmp_verlist
                    else:
                        raise Exception('Target model %s/%s status failed!' %
                                (self.model_name, tmp_verlist[0]['version']))
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
            if node.status == 'online':
                log.info('Successfully publish model %s/%s to %s' %
                        (node.model_name, node.model_ver, node.path))
            elif node.status == 'deploy_failed':
                log.error('Failed to publish model %s/%s to %s!' %
                        (node.model_name, node.model_ver, node.path))
                fail_list.append(node.path)
            elif node.status == 'file_not_exist': # 不需要重试
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


def read_conf(target):
    global zk_servers
    global zk_path
    global cluster_node
    global cluster_iplist

    cf = ConfigParser.ConfigParser()
    cf.read("server.conf")
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


def parse_publish_args(arglist):
    global model_name
    global model_ver
    global target
    global is_cluster
    global batch_size
    global is_rollback
    global retry_cnt

    def print_usage():
        print 'Usage:'
        print '\t%s --model $model_name/$model_version --target $zk_path [--cluster] [--batch N]' % sys.argv[0]
        print ''
        print '--model:\t存储于Model Repository上的要发布模型信息，格式:模型名/版本号'
        print '--target:\t要发布的目标集群或主机，默认是单台主机，集群发布需要加 --cluster 参数，格式:/TPS/cluster_name/host_ip_or_name'
        print '--cluster:\t指定发布目标是集群 bool参数'
        print '--batch:\t集群发布时一次发布的主机数量，默认1'
        print '--rollback:\t版本回滚，删除线上比指定模型版本高的所有模型'
        print '--retry:\t失败后重试次数'
        print '--check:\t单机发布完成后检查是否成功'
        print ''
        print 'Examples:'
        print 'single host:'
        print '\t%s --model knn/1 --target Cluster1/Host1' % sys.argv[0]
        print 'batch cluster:'
        print '\t%s --model knn/1 --target Cluster1 --cluster --batch 10' % sys.argv[0]
        print ''

    try:
        if len(arglist) <= 0:
            print_usage() # TODO multi level
            sys.exit(0)

        opts, args = getopt.getopt(arglist, "",
                ["help", "model=", "target=", "cluster", "batch=", "rollback"])

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
            elif opt in ("--help"):
                print_usage()
                sys.exit(0)
            elif opt in ("--rollback"):
                is_rollback = True
            elif opt in ("--retry"):
                retry_cnt = int(arg)
            else:
                log.error('Invalid arg: %s' % opt)
                print_usage()
                sys.exit(-1)

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


def do_publish(arglist):
    client = None
    try:
        log.info('Running publish...')

        parse_publish_args(arglist)

        log.info('model_name: %s' % model_name)
        log.info('model_ver: %s' % model_ver)
        log.info('target: %s' % target)
        log.info('is_cluster: %s' % is_cluster)
        log.info('is_rollback: %s' % is_rollback)
        log.info('batch_size: %s' % batch_size)
        log.info('retry_cnt: %d' % retry_cnt)

        # read conf
        conf_ret = read_conf(target)
        if conf_ret != 0:
            log.error('Invalid target param, clusternode:%s!' % clusternode)
            sys.exit(-1)

        client = KazooClient(hosts = zk_servers)
        client.start()
        publish_model(client)

    finally:
        if client:
            client.stop()


def parse_check_args(arglist):
    global model_name
    global model_ver
    global target

    def print_usage():
        print 'Usage:'
        print '\t%s check --model $model_name/$model_version --target $zk_path' % sys.argv[0]
        print ''

    try:
        if len(arglist) <= 0:
            print_usage()
            sys.exit(0)

        opts, args = getopt.getopt(arglist, "",
                ["help", "model=", "target="])

        for opt, arg in opts:
            if opt in ("--model"):
                lst = str(arg).split('/')
                if len(lst) != 2:
                    raise Exception('--model should be in format model_name/model_version')
                model_name = lst[0]
                model_ver = lst[1]
            elif opt in ("--target"):
                target = str(arg)
            elif opt in ("--help"):
                print_usage()
                sys.exit(0)
            else:
                log.error('Invalid arg: %s' % opt)
                print_usage()
                sys.exit(-1)

        if (not model_name) or (not model_ver):
            log.error("Model info must be set with --model in form of model_name/model_version")
            print_usage()
            sys.exit(-1)
        elif not target:
            log.error("target host/cluster must be set with --target")
            print_usage()
            sys.exit(-1)

    except getopt.GetoptError as err:
        log.error("%s" % err)
        print_usage()
        sys.exit(-1)


def do_check(arglist):
    log.info('Running check...')

    parse_check_args(arglist)

    log.info('model_name: %s' % model_name)
    log.info('model_ver: %s' % model_ver)
    log.info('target: %s' % target)

    ret = load_check(target, model_name, model_ver)
    if ret == 0:
        log.info('Model %s/%s load ok.' % (model_name, model_ver))
        sys.exit(0)
    else:
        log.error('Model %s/%s load failed.' % (model_name, model_ver))
        sys.exit(-1)


def do_operate(arglist):
    def print_usage():
        print 'Usage:'
        print '\t%s add --target Cluster1' % sys.argv[0]
        print '\t%s delete --target Cluster1' % sys.argv[0]
        print '\t%s root --target Cluster1' % sys.argv[0]
        print ''

    def parse_op_args(arglist):
        global target
        try:
            if len(arglist) <= 0:
                print_usage()
                sys.exit(0)

            opts, args = getopt.getopt(arglist, "", ["help", "target="])

            for opt, arg in opts:
                if opt in ("--target"):
                    target = str(arg)
                elif opt in ("--help"):
                    print_usage()
                    sys.exit(0)
                else:
                    log.error('Invalid arg: %s' % opt)
                    print_usage()
                    sys.exit(-1)

            if not target:
                log.error("target host/cluster must be set with --target")
                print_usage()
                sys.exit(-1)

        except getopt.GetoptError as err:
            log.error("%s" % err)
            print_usage()
            sys.exit(-1)

    if len(arglist) <= 0:
        print_usage()
        sys.exit(0)

    subcmd = arglist[0]
    parse_op_args(arglist[1:])
    log.info('Running operate %s target = %s' % (subcmd, target))

    zk_client = None
    try:
        clusternode = target
        conf_ret = read_conf(clusternode)
        if conf_ret != 0:
            raise Exception('Invalid target param, clusternode:%s!' % clusternode)
        # create node
        zk_client = KazooClient(hosts = zk_servers)
        zk_client.start()

        zk_node = zk_path + clusternode
        exist_flag = zk_client.exists(zk_node)

        if subcmd == 'root':
            zk_node = zk_path
            subcmd = 'delete'

        if subcmd == 'add':
            if not exist_flag:
                zk_client.ensure_path(zk_node)
            for host in cluster_iplist:
                new_node = zk_node + '/' + host
                if not zk_client.exists(new_node):
                    zk_client.create(new_node, b'')
            # check host node
            children = zk_client.get_children(zk_node)
            if len(children) != len(cluster_iplist):
                raise Exception('Create cluster:%s node failed!' % clusternode)
            log.info('create cluster:%s node success!' % clusternode)
        elif subcmd == 'delete':
            if exist_flag:
                zk_client.delete(zk_node,recursive=True)
                log.info('Delete cluster:%s node success!' % clusternode)
                # if is_check:  # TODO
                    # zk_client.delete(zk_path,recursive=True)
                    # log.info('Delete zk_path:%s node success!' % clusternode)
            else:
                log.info('cluster:%s node not exist!' % clusternode)
        else:
            raise Exception('Invalid op command %s' % subcmd)

    finally:
        if zk_client:
            zk_client.stop()


def main():
    try:
        logging.basicConfig(format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                level=logging.INFO)

        if len(sys.argv) < 2:
            print_usage() # TODO multi level
            sys.exit(0)

        subcmd = sys.argv[1]
        if subcmd == 'publish':
            do_publish(sys.argv[2:])
        elif subcmd == 'check':
            do_check(sys.argv[2:])
        elif subcmd == 'op':
            do_operate(sys.argv[2:])
        else:
            log.error('Invalid command %s' % subcmd)
            sys.exit(-1)

        sys.exit(0)

    except KeyboardInterrupt:
        log.warn('Terminated by user.')
        sys.exit(0)

    except Exception as ex:
        log.error('Exception: %s' % ex)
        sys.exit(-1)


if __name__ == '__main__':
    main()

