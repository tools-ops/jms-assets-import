'''
JMS_VERSION: jumpserver-python-sdk 0.0.54
'''

import init_config
import requests
import json
from jms import service
from aws_assent_manage import aws_ec2_info

class jms_asset():
    '''
    https://github.com/jumpserver/jumpserver-python-sdk
    '''
    def __init__(self,config_jms='jms_config'):
        my_config = init_config.ConfigParser()
        global logger
        logger = init_config.log_format()
        self.jms_user = my_config.get_config(config_jms, 'jms_username')
        self.jms_pass = my_config.get_config(config_jms, 'jms_password')
        self.jms_host = my_config.get_config(config_jms, 'jms_server')
        self.user_service = service.UserService(endpoint=self.jms_host)
        self.user_service.login(username=self.jms_user, password=self.jms_pass, pubkey=None)
    def jms_now_info(self):
        assets_list = []
        logger.debug(self.user_service.__dict__)
        logger.debug(self.user_service._auth.token)
        now_assents = self.user_service.get_assets()
        logger.debug(self.user_service.get_profile())
        # logger.debug(self.user_service.get_user_asset_groups(self.user_service.get_profile())[0].__dict__)
        for i in now_assents:
            logger.debug(i.__dict__)
            assets_info = {}
            assets_info['hostname'] = i.hostname
            assets_info['comment'] = i.comment
            assets_list.append(assets_info)
        return assets_list

    def filter_host_to_regisger(self, import_data, jms_data):
        logger.debug('Abug Import Data is %s' % import_data)
        logger.debug('Abug Now JMS Server List is' % jms_data)
        register_list = []
        for i in import_data:
            if jms_data:
                for x in jms_data:
                    if i['hostname'] == x['hostname'] and i['comment'] == x['comment']:
                        logger.warn('The Host %s is aleary exist' % (i['hostname']))
                    elif 'hostname' in i.keys() and 'hostname' not in x.keys():
                        register_list.append(i)
            else:
                register_list.append(i)
        logger.debug('Adebug: Filter Register List is %s' %register_list)
        return register_list

    def jms_data_reform(self, primary_data, admin_user, sys_user, ass_node='DEFAULT'):
        '''

        :param primary_data:
        :param admin_user:
        :param sys_user:
        :param ass_node: 'DEFAULT,ALL'
        :return:
        '''
        logger.debug('Token: %s' %(self.user_service._auth.token))
        r_headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                     'Authorization': 'Bearer %s' % (self.user_service._auth.token)}
        uri_sys_user = '%s/api/assets/v1/system-user/?name=%s' % (self.jms_host, sys_user)
        uri_admin_user = '%s/api/assets/v1/admin-user/?name=%s' % (self.jms_host, admin_user)
        uri_asset_node = '%s/api/assets/v1/nodes/' % (self.jms_host)
        sys_uuid_list = requests.get(uri_sys_user, headers=r_headers)
        admin_uuid_list = requests.get(uri_admin_user, headers=r_headers, params='payload')
        node_uuid_list = requests.get(uri_asset_node, headers=r_headers,  params='payload')
        logger.debug(sys_uuid_list.text)
        logger.debug(admin_uuid_list.text)
        logger.debug(node_uuid_list.text)
        for x in json.loads(sys_uuid_list.text):
            if x['name'] == sys_user or x['username'] == sys_user:
                sys_uuid = x['id']
        for y in json.loads(admin_uuid_list.text):
            if y['name'] == admin_user or y['username'] == admin_user:
                admin_uuid = y['id']
        #Add default Nodes
        ass_node_input = ass_node.split(',')
        regiser_node_list = []
        if 'DEFAULT' not in ass_node_input:
            ass_node_input.append('DEFAULT')
        for each_node in ass_node_input:
            logger.debug(each_node)
            for each_node_uuid in json.loads(node_uuid_list.text):
                if each_node == each_node_uuid['value']:
                    logger.debug(each_node_uuid)
                    regiser_node_list.append(each_node_uuid['id'])
        logger.info(regiser_node_list)
        primary_data['nodes'] = regiser_node_list
        primary_data['admin_user'] = admin_uuid
        # primary_data['system-user'] = sys_uuid
        return primary_data


    def jms_register_host(self, json_data):
        '''
        https://jumpserver.readthedocs.io/zh/docs/api_style_guide.html
        https://github.com/jumpserver/jumpserver/issues/1520
        :param json_data:
        :return:
        '''
        r_uri = '%s/api/assets/v1/assets/' % (self.jms_host)
        r_headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                     'Authorization': 'Bearer %s' % (self.user_service._auth.token)}
        logger.debug(r_headers)
        requests.post(r_uri, headers=r_headers, data=json.dumps(json_data))

    def update_asset(self):
        pass


if __name__ == '__main__':
    # mjms = jms_asset()
    # mjms.jms_data_reform({},'ops-root','ops-user','ALL')
    # print(mjms.jms_now_info())
    # aws_info = aws_ec2_info('aws_hmt_tha')
    # print(aws_info.get_ec2_list())
    # mjms.jms_data_reform('ops-root', 'ops-user')
    #---
    jms_app = jms_asset()
    import_data = aws_ec2_info('aws_hmt_tha').get_ec2_list()  #AWS
    jms_regisger_list = jms_app.filter_host_to_regisger(import_data, jms_app.jms_now_info())
    for i in jms_regisger_list:
        x = jms_app.jms_data_reform(i, 'ops-root', 'ops-user')
        jms_app.jms_register_host(x)
        logger.warn('Now add Host %s' % (x))