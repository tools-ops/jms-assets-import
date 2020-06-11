'''
For get Shardid from etcd
'''
from config import Log
from config import base_config
from urllib.parse import urljoin
from os import path
import requests
import json
Log = Log()

class Etcd():
    def __init__(self, project_config):
        config = base_config(project_config)
        self.etcd_host = config.get('ETCD_HOST')
        self.etcd_root = config.get('ETCD_ROOT')
    def get_data(self):
        base_url = urljoin(self.etcd_host,
                           path.join('v2/keys', self.etcd_root.strip('/')))
        Log.debug('baseUrl: %s' % base_url)
        try:
            rst = json.loads(requests.get(path.join(base_url,'105')).content)
            Log.debug(rst)
            all_shard = []
            for each_node in rst['node']['nodes']:
                if str(each_node['key']).startswith(path.join(self.etcd_root,str(105),str(105))):
                    Log.debug('All shard info %s' % each_node)
                    shard_url = path.join(self.etcd_host,'v2/keys',str(each_node['key']).strip('/'))
                    info_get = [
                        'dn',
                        'gid',
                        'shard_id',
                        'merge_rel',
                        'gm/private_ip',
                        'gm/redis',
                        'gm/redis_db',
                        'gm/redis_rank',
                        'gm/redis_rank_db'
                    ]
                    shard_info = {}
                    for i in info_get:
                        rst_each = json.loads(requests.get(path.join(shard_url,i)).content)
                        shard_info[i] = rst_each['node']['value']
                    all_shard.append(shard_info)
            return all_shard
        except IOError:
            Log.error('Network is unavailable')
        except KeyError:
            Log.error('Etcd response no available key')



def extend_mesage(project_config,private_ip):
    a = Etcd(project_config)
    db = a.get_data()
    rst=[]
    for each_record in db:
        if private_ip == each_record['gm/private_ip']:
            rst.append(each_record['merge_rel'])
    return ','.join(list(set(rst)))


if __name__ == '__main__':
    pass
