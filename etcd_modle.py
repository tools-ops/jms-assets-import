'''
For get Shardid from etcd
'''
from config import Log
from config import base_config
from urllib.parse import urljoin
from os import path
import requests
import json
import re
from multiprocessing import Pool


Log = Log()

class Etcd():
    def __init__(self, project_config):
        config = base_config(project_config)
        self.etcd_host = config.get('ETCD_HOST')
        self.etcd_root = config.get('ETCD_ROOT')
    def get_data(self,multi=1):
        base_url = urljoin(self.etcd_host,
                           path.join('v2/keys', self.etcd_root.strip('/')))
        Log.debug('baseUrl: %s' % base_url)
        try:
            root_all = []
            sub_keys = json.loads(requests.get(base_url).content)
            m_parten = '%s/[0-9]{1,3}$' % self.etcd_root
            for each_keys in sub_keys['node']['nodes']:
                rst = self.mul_gid(m_parten, each_keys, multi=multi)
                if rst:
                    root_all += [i.get() for i in rst if i.get()]
            return root_all
        except IOError:
            Log.error('Network is unavailable')
        except KeyError:
            Log.error('Etcd response no available key')

    def mul_gid(self,m_parten, each_keys, multi=1):
        if re.search(m_parten, each_keys['key']):
            rst = json.loads(requests.get(path.join(self.etcd_host, 'v2/keys', each_keys['key'].strip('/'))).content)
            poo = Pool(multi)
            results = []
            for each_shard in rst['node']['nodes']:
                '''
                Multi support
                '''
                result = poo.apply_async(self.mul_shard, args=(each_shard,))
                results.append(result)
            poo.close()
            poo.join()
            return results
    def mul_shard(self, each_shard):
        shard_info = {}
        i_parten = '%s/[0-9]{3}/[0-9]{4,5}$' % self.etcd_root
        if re.search(i_parten, str(each_shard['key'])):
            Log.debug('All shard info %s' % each_shard)
            shard_url = path.join(self.etcd_host, 'v2/keys', str(each_shard['key']).strip('/'))
            info_get = [
                'merge_rel',
                'gm/private_ip'
            ]
            try:
                for i in info_get:
                    rst_each = json.loads(requests.get(path.join(shard_url, i)).content)
                    shard_info[i] = rst_each['node']['value']
            except KeyError:
                shard_info.clear()
                Log.warning('No such key %s' % rst_each)
            return shard_info


def extend_mesage(project_config):
    a = Etcd(project_config)
    db = a.get_data(multi=20)
    rst={}
    for each_record in db:
        Log.debug('Etcd each Record %s' % each_record)
        ip = each_record['gm/private_ip']
        try:
            rst[ip] += ',%s' % each_record['merge_rel']
        except KeyError:
            rst[ip] = each_record['merge_rel']
        '''
        value need list uniq
        '''
    return rst


if __name__ == '__main__':
    rst = extend_mesage('prod-jws-hmt')
    print(rst)
