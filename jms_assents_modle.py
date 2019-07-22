
import uuid
import re
import requests
import json
import logging
from botocore.client import Config
from boto3.session import Session
from jms import service
#Ali
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
#pip install aliyun-python-sdk-ecs


logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

class aws_ec2_assent():
    def __init__(self, aws_access_key, aws_secret_key, aws_region):
        session = Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key,region_name=aws_region)
        self.ec2 = session.resource('ec2', config=Config(signature_version='s3v4'))
        self.ec2_client = session.client('ec2', config=Config(signature_version='s3v4'))

    def get_assents(self):
        server_list = []
        for each_instance in self.ec2.instances.all():
            server_info = {}
            Name_index = [i for i, x in enumerate(each_instance.tags) if x['Key'].find('Name') != -1]
            Comman_index = [ i for i, x in enumerate(each_instance.tags) if x['Key'].find('Service') != -1]
            if Comman_index:
                comman_info = str(each_instance.tags[Comman_index[0]]['Value'])
            else:
                comman_info = '[]'
            if re.search('game|match|cross|jenkins|auth|pay|gmtools', each_instance.tags[Name_index[0]]['Value']):
                server_info['group'] = ['dev']
            else:
                server_info['group'] = ['base']
            server_info['hostname'] = each_instance.tags[Name_index[0]]['Value']
            server_info['id'] = str(uuid.uuid3(uuid.NAMESPACE_DNS,each_instance.id))
            server_info['ip'] = each_instance.private_ip_address
            server_info['is_actice'] = 'true'
            server_info['comment'] = comman_info
            logging.debug(server_info)
            server_list.append(server_info)
        return server_list

class ali_ecs_assent():
    def __init__(self,ali_access_key,ali_secret_key,ali_region):
        self.accessKeyID = ali_access_key
        self.accessKeySecret = ali_secret_key
        self.region = ali_region
    def get_aliyun_hosts(self):
        client = AcsClient(self.accessKeyID, self.accessKeySecret, self.region)
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_PageNumber(1)
        request.set_PageSize(50)
        response = client.do_action_with_exception(request)
        data = json.loads(response)
        PageNumber = int(data['TotalCount'] / 50 + 2)
        list = []
        for Number in range(1, PageNumber):
            request.set_PageNumber(Number)
            request.set_PageSize(50)
            response = client.do_action_with_exception(request)
            data = json.loads(response)

            for host in data['Instances']['Instance']:
                dict = {}
                id=re.split(r'-',host['SerialNumber'])
                id=''.join(str(i) for i in id)
                dict['id'] = id
                dict['ip'] = host['NetworkInterfaces']['NetworkInterface'][0]['PrimaryIpAddress']
                dict['hostname'] = host['InstanceName']
                dict['is_active'] = 'true'
                if 'Tags' in host:
                    comment=host['Tags']['Tag'][0]['TagValue']
                    dict['comment'] = "[%s]" %comment
                else:
                    dict['comment'] = "[123]"

                if host['InstanceName'].startswith('G') or host['InstanceName'].startswith('c'):
                    dict['group'] = ['dev']
                else:
                    dict['group'] = ['base']
                list.append(dict)
        logging.debug(list)
        return  list


class jms():
    def __init__(self,jms_host,jms_user,jms_pass):
        self.jms_host = jms_host
        self.user_service = service.UserService(endpoint=jms_host)
        self.user_service.login(username=jms_user, password=jms_pass, pubkey=None)
        self.r_headers = {'Content-Type': 'application/json',
                          'Accept': 'application/json',
                          'Authorization': 'Bearer %s' % (self.user_service._auth.token)}

    def assent_assent_filter(self):
        now_assents = self.user_service.get_assets()
        logging.info(now_assents)
        logging.debug(now_assents[0].__dict__)

    def data_reform(self,primary_data,admin_user,group_info,domain_id=None):
        logging.debug('Token: %s' % (self.user_service._auth.token))
        uri_admin_user = '%s/api/assets/v1/admin-user/?name=%s' % (self.jms_host, admin_user)
        uri_asset_node = '%s/api/assets/v1/nodes/' % (self.jms_host)
        admin_uuid_list = requests.get(uri_admin_user, headers=self.r_headers, params='payload')
        node_uuid_list = requests.get(uri_asset_node, headers=self.r_headers,  params='payload')
        logging.debug(node_uuid_list.content)
        logging.debug(json.loads(admin_uuid_list.text)[0]['id'])
        add_node_list=[]
        add_node_list.append(group_info['Default'])
        for i in primary_data['group']:
            add_node_list.append(group_info[i][0])
        logging.debug(add_node_list)
        primary_data['nodes'] = add_node_list
        primary_data['domain'] = domain_id
        primary_data['admin_user'] = json.loads(admin_uuid_list.text)[0]['id']
        primary_data['protocols'] = ['ssh/22']
        primary_data.pop('group')
        logging.debug(primary_data)
        self.assent_register(primary_data)
        # return primary_data


    def group_add(self,first_group,sub_group):
        need_group={}
        uri_asset_node = '%s/api/assets/v1/nodes/' % (self.jms_host)
        node_uuid_list = requests.get(uri_asset_node, headers=self.r_headers, params='payload')
        logging.debug(json.loads(node_uuid_list.text))
        if first_group in [i['value'] for i in json.loads(node_uuid_list.text)]:
            logging.debug('Group %s already exist' % first_group)
        else:
            logging.info('Group %s is not exist now create it' % first_group)
            root_node = [i['id'] for i in json.loads(node_uuid_list.text) if 'Default' == i['value']]
            self.group_data_register(first_group,root_node[0])
            logging.info('The Root ID %s' % root_node)
        for i in sub_group:
            node_uuid_list = requests.get(uri_asset_node, headers=self.r_headers, params='payload')
            up_node = [i['id'] for i in json.loads(node_uuid_list.text) if first_group == i['value']]
            up_node_key = [i['key'] for i in json.loads(node_uuid_list.text) if first_group == i['value']]
            sub_node_key = [i['value'] for i in json.loads(node_uuid_list.text) if re.match(up_node_key[0],i['key'])]
            logging.debug(up_node_key[0])
            logging.debug(sub_node_key)
            if sub_node_key:
                if i in sub_node_key:
                    logging.debug('The first group %s already have %s' %(first_group,i))
                else:
                    self.group_data_register(i, up_node[0])
            else:
                self.group_data_register(i,up_node[0])
            need_group[first_group] = up_node[0]
            node_uuid_list = requests.get(uri_asset_node, headers=self.r_headers, params='payload')
            need_group[i] = [x['id'] for x in json.loads(node_uuid_list.text) if re.match(up_node_key[0],x['key']) and i == x['value']]
        need_group['Default'] = [i['id'] for i in json.loads(node_uuid_list.text) if 'Default' == i['value']][0]
        logging.debug(need_group)
        return need_group


    def group_data_register(self,group_name, up_id):
        group_uri = '%s/api/assets/v1/nodes/%s/children/' % (self.jms_host,up_id)
        group_data = {'value': group_name}
        gg = requests.post(group_uri, headers=self.r_headers, data=json.dumps(group_data))
        if gg.status_code == 200 or gg.status_code == 201:
            logging.info('create group %s success. Return code %s' % (group_name, str(gg.status_code)))
        else:
            logging.warning('create group %s faild. Err code %s . Check or create by yourself' % (group_name, str(gg.status_code)))

    def assent_register(self,data):
        now_assents = self.user_service.get_assets()
        logging.debug(now_assents)
        logging.debug(data)
        if data['hostname'] in [i.hostname for i in now_assents]:
            for y in now_assents:
                    logging.debug(y.__dict__)
                    if data['hostname'] == y.hostname and data['comment'] == y.comment:
                        logging.info('The %s alreary exist' % data['hostname'])
                    if data['hostname'] == y.hostname and data['comment'] != y.comment:
                        logging.info('The %s will be update' % data['hostname'])
                        self.assent_delete(data)
                        self.assent_add(data)
        else:
            logging.info('New assent %s will be add' % data['hostname'])
            self.assent_add(data)


    def domain_get(self,domain_name):
        gata_uri = '%s/api/assets/v1/domain/' % (self.jms_host)
        gg = requests.get(gata_uri, headers=self.r_headers)
        logging.debug(json.loads(gg.text))
        return [ i['id'] for i in json.loads(gg.text) if domain_name == i['name']][0]

    def assent_add(self,assent):
        r_uri = '%s/api/assets/v1/assets/' % (self.jms_host)
        gg = requests.post(r_uri, headers=self.r_headers, data=json.dumps(assent))
        logging.debug(assent)
        if gg.status_code == 200 or gg.status_code == 201:
            logging.info('Register %s success. response code is %s' % (assent['hostname'], str(gg.status_code)))
        else:
            logging.warning('Register %s failed. error code is %s' % (assent['hostname'], str(gg.status_code)))
    def assent_delete(self,assent):
        r_uri = '%s/api/assets/v1/assets/' % (self.jms_host)
        gg = requests.delete(r_uri + assent['id'])
        if gg.status_code == 200 or gg.status_code == 201:
            logging.info('Delete %s is success. response code is %s' % (assent['hostname'], str(gg.status_code)))
        else:
            logging.warning('Delete %s is failed. error code is %s' % (assent['hostname'], str(gg.status_code)))


if __name__ == '__main__':
    def run(project_config):
        import configparser
        cf = configparser.ConfigParser()
        cf.read('config.ini')
        if cf.get(project_config, 'platform_type') == 'aliyun':
            ali_assent = ali_ecs_assent(ali_access_key=cf.get(project_config, 'access_key'),
                                        ali_secret_key=cf.get(project_config, 'secret_key'),
                                        ali_region=cf.get(project_config, 'region'))
            now_assents = ali_assent.get_aliyun_hosts()
        elif cf.get(project_config, 'platform_type') == 'aws':
            massent = aws_ec2_assent(aws_access_key=cf.get(project_config, 'access_key'),
                                     aws_secret_key=cf.get(project_config, 'secret_key'),
                                     aws_region=cf.get(project_config, 'region'))
            now_assents = massent.get_assents()
        mjms = jms(jms_host=cf.get(project_config, 'jms_host'),
                   jms_user=cf.get(project_config, 'jms_user'),
                   jms_pass=cf.get(project_config, 'jms_pass'))
        group_list = [','.join(i['group']) for i in now_assents]
        group_info = mjms.group_add(cf.get(project_config, 'jms_assents_group'),
                                    list(set(group_list)))
        logging.debug(group_info)
        domain_info = mjms.domain_get(cf.get(project_config, 'jms_domain_name'))
        for i in now_assents:
            mjms.data_reform(i, cf.get(project_config, 'jms_admin_user')
                             , group_info, domain_info)

    run('project-template')
