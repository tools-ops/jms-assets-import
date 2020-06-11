
import uuid
import re
import json
from config import Log
from botocore.client import Config
from boto3.session import Session
#Ali
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
#pip install aliyun-python-sdk-ecs
from etcd_modle import extend_mesage



Log = Log()

class aws_ec2_assent():
    def __init__(self, aws_access_key, aws_secret_key, aws_region):
        session = Session(aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key,region_name=aws_region)
        self.ec2 = session.resource('ec2', config=Config(signature_version='s3v4'))
        self.ec2_client = session.client('ec2', config=Config(signature_version='s3v4'))

    def get_assents(self,register_prefix='',default_re='',extend_re='dev',project=''):
        final_re = '|'.join(default_re.split('|') + extend_re.split('|')).strip('|')
        Log.debug(final_re)
        server_list = []
        for each_instance in self.ec2.instances.all():
            server_info = {}
            Name_index = [i for i, x in enumerate(each_instance.tags) if x['Key'].find('Name') != -1]
            if re.search(final_re, each_instance.tags[Name_index[0]]['Value']):
                server_info['group'] = ['dev']
            else:
                server_info['group'] = ['base']
            if register_prefix:
                server_info['hostname'] = str(register_prefix) + each_instance.tags[Name_index[0]]['Value']
            else:
                server_info['hostname'] = each_instance.tags[Name_index[0]]['Value']
            server_info['id'] = str(uuid.uuid3(uuid.NAMESPACE_DNS,each_instance.id))
            server_info['ip'] = each_instance.private_ip_address
            server_info['is_actice'] = 'true'
            server_info['platform'] = "Linux"
            if not extend_mesage(project, each_instance.private_ip_address):
                Comman_index = [i for i, x in enumerate(each_instance.tags) if x['Key'].find('Service') != -1]
                if Comman_index:
                    comman_info = str(each_instance.tags[Comman_index[0]]['Value'])
                else:
                    comman_info = '[]'
                server_info['comment'] = comman_info
            server_info['comment'] = extend_mesage(project, each_instance.private_ip_address)
            Log.debug(server_info)
            server_list.append(server_info)
        return server_list

class ali_ecs_assent():
    def __init__(self,ali_access_key,ali_secret_key,ali_region):
        self.accessKeyID = ali_access_key
        self.accessKeySecret = ali_secret_key
        self.region = ali_region
    def get_aliyun_hosts(self,register_prefix='',default_re='',extend_re='dev',project=''):
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
                if register_prefix:
                    dict['hostname'] = str(register_prefix) + host['InstanceName']
                else:
                    dict['hostname'] = host['InstanceName']
                dict['is_active'] = 'true'
                dict['platform'] = "Linux"
                if not extend_mesage(project, dict['ip']):
                    if 'Tags' in host:
                        comment=host['Tags']['Tag'][0]['TagValue']
                        dict['comment'] = "[%s]" %comment
                    else:
                        dict['comment'] = "[123]"
                dict['comment'] = extend_mesage(project, dict['ip'])
                # if host['InstanceName'].startswith('G') or host['InstanceName'].startswith('c'):
                final_re = '|'.join(default_re.split('|') + extend_re.split('|')).strip('|')
                if re.search(final_re, host['InstanceName']):
                    dict['group'] = ['dev']
                else:
                    dict['group'] = ['base']
                list.append(dict)
        Log.debug(list)
        return  list



def assents(project_config):
    from config import base_config
    cf = base_config(project_config)

    if cf.get('platform_type') == 'aliyun':
        ali_assent = ali_ecs_assent(ali_access_key=cf.get('access_key'),
                                    ali_secret_key=cf.get('secret_key'),
                                    ali_region=cf.get('region'))
        now_assents = ali_assent.get_aliyun_hosts(register_prefix=cf.get('register_prefix'),
                                                  default_re=cf.get('default_regular', special_select='base'),
                                                  extend_re=cf.get('extend_regular'),project=project_config)
    elif cf.get('platform_type') == 'aws':
        massent = aws_ec2_assent(aws_access_key=cf.get('access_key'),
                                 aws_secret_key=cf.get('secret_key'),
                                 aws_region=cf.get('region'))
        now_assents = massent.get_assents(register_prefix=cf.get('register_prefix'),
                                          default_re=cf.get('default_regular', special_select='base'),
                                          extend_re=cf.get('extend_regular'),project=project_config)
    return now_assents,cf.get('jms_assents_group'),cf.get('jms_domain_name'), cf.get('jms_admin_user')


if __name__ == '__main__':
    pass


