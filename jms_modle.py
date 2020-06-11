import requests
import json
import uuid
from config import Log
from config import base_config

Log = Log()

class jms():
    def __init__(self,project_config):
        config = base_config(project_config)
        self.project = project_config
        self.url = config.get('jms_host', special_select='base')
        self.username = config.get('jms_user', special_select='base')
        self.password = config.get('jms_pass', special_select='base')
        self.headers = {
            'Content-Type': 'application/json',
            'accept': 'application/json'
            }
    def get_token(self):
        login_data = {
            'username' : self.username,
            'password' : self.password,
            'public_key': None
        }
        token = requests.post(
            url=self.url+'/api/v1/authentication/auth/',
            data=login_data).text
        Log.debug('token is %s' % token)
        self.headers['Authorization']  = 'Bearer %s' % json.loads(token)['token']

    def nodes_list(self):
        rst_node = requests.get(
            url=self.url+'/api/v1/assets/nodes/',
            headers=self.headers).text
        Log.debug('Nodes is %s' % rst_node)
        return  rst_node

    def assets_list(self):
        return json.loads(
            requests.get(
                url=self.url+'/api/v1/assets/assets/',
                headers=self.headers
            ).text)


    def assets_create(self, data):
        f_uuid = self.node_create(data[1])
        d_uuid = self.domain_create(data[2])
        a_uuid = self.admin_user_create(data[3])
        jms_assets = self.assets_list()

        for each_asset in data[0]:
            each_asset['nodes'] = self.node_child_create(f_uuid, each_asset['group'])
            each_asset['domain'] = d_uuid
            each_asset['admin_user'] = a_uuid
            if each_asset['id'] in [x['id'] for x in jms_assets]:
                self.assets_update(each_asset,jms_assets)
            else:
                rst = requests.post(
                    url=self.url+'/api/v1/assets/assets/',
                    headers=self.headers,
                    data=json.dumps(each_asset)
                )
                if str(rst.status_code).startswith('2'):
                    Log.info('create asset %s %s' % (each_asset['hostname'], rst.status_code))
                else:
                    Log.error('create asset faild %s: %s' % (rst.status_code, rst.text))

    def assets_update(self, asset_info, jms_info):
        jms_info_asset = [x for x in jms_info if x['id'] == asset_info['id']][0]
        if (jms_info_asset['hostname'] == asset_info['hostname'] and
        jms_info_asset['ip'] == asset_info['ip'] and
        jms_info_asset['comment'] == asset_info['comment']):
            Log.debug('The assets %s is no change' % asset_info['hostname'])
        else:
            rst = requests.put(
                url=self.url + '/api/v1/assets/assets/%s/' % asset_info['id'],
                headers=self.headers,
                data=json.dumps(asset_info)
            )
            Log.info('Update the assent %s: %s' % (rst.status_code, asset_info['hostname']))

    def assets_delete(self):
        pass

    def node_create(self, node_name):
        __data = {
            'id' : str(uuid.uuid3(uuid.NAMESPACE_DNS, node_name)),
            'value' : node_name
        }
        if node_name in  [i['value'] for i in json.loads(self.nodes_list()) if i['value'] == node_name]:
            Log.info('The Group %s is exist' % node_name)
        else:
            requests.post(
                url=self.url + '/api/v1/assets/nodes/',
                headers=self.headers,
                data=json.dumps(__data)
            ).text()
            Log.info('Create node %s' % node_name)
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, node_name))

    def node_child_list(self, node_uuid):
        return json.loads(requests.get(
            url=self.url + '/api/v1/assets/nodes/%s/children/' % str(node_uuid),
            headers=self.headers
        ).text)

    def node_child_create(self, node_uuid, node_child):
        rst_child_nodes = self.node_child_list(node_uuid)
        if isinstance(node_child, list):
            for each_child_node in node_child:
                if each_child_node not in [x['value'] for x in rst_child_nodes]:
                    child_data = {'value' : each_child_node}
                    requests.post(
                        url=self.url + '/api/v1/assets/nodes/%s/children/' % str(node_uuid),
                        headers=self.headers,
                        data=json.dumps(child_data)
                    )
                    Log.info('Create child node %s' % each_child_node)
        return [x['id'] for x in rst_child_nodes if x['value'] in node_child]

    def domain_list(self):
        return json.loads(requests.get(url=(self.url + '/api/v1/assets/domains/'),
                     headers=self.headers).text)


    def domain_create(self, domain_name):
        __data = {
            'id' : str(uuid.uuid3(uuid.NAMESPACE_DNS, domain_name)),
            'name' : domain_name,
            'assets' : []
        }
        if domain_name in [x['name'] for x in self.domain_list()]:
            Log.info('The domain %s is exist' % domain_name)
        else:
            requests.post(
                url=self.url + '/api/v1/assets/domains/',
                headers=self.headers,
                data=json.dumps(__data)
            )
            Log.info('Create domain %s' % domain_name)

        return [x for x in self.domain_list() if x['name'] == domain_name][0]['id']

    def admin_user_list(self):
        return json.loads(requests.get(
            url=self.url + '/api/v1/assets/admin-users/',
            headers=self.headers
        ).text)

    def admin_user_create(self, admin_user):
        __data = {
            'id' : str(uuid.uuid3(uuid.NAMESPACE_DNS, admin_user)),
            'name' : admin_user
        }
        if admin_user in [x['name'] for x in self.admin_user_list()]:
            Log.info('The Admin User %s is exist' % admin_user)
        else:
            requests.post(
                url=self.url + '/api/v1/assets/admin-users/',
                headers=self.headers,
                data=json.dumps(__data)
            )
            Log.info('Create admin user: %s' % admin_user)
        return [x for x in self.admin_user_list() if x['name'] == admin_user][0]['id']


def main(project):
    from assents_modle import assents
    assents_all = assents(project)
    m_assents=jms(project)
    m_assents.get_token()
    m_assents.assets_create(assents_all)

if __name__ == '__main__':
    main('test')

