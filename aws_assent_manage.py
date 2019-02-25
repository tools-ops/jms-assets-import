'''
AWS Info
boto3 == 1.9.71
botocore == 1.12.71
Return Data Format:
{"id": "e0316cf8-35a4-11e9-xxxxx","ip": "192.168.0.1","hostname": "vpc1-xxx","port": 22,
"is_active": 'true', "comment": "","admin_user": "872a01b7-b21f-4623-b7b3-xxxxx"}

'''
import init_config
from botocore.client import Config
from boto3.session import Session
import uuid


class aws_ec2_info():
    def __init__(self,config_area):
        my_config = init_config.ConfigParser()
        global logger
        logger = init_config.log_format()
        self.aws_region = my_config.get_config(config_area, 'aws_region')
        self.aws_access_key_id = my_config.get_config(config_area, 'aws_access_key_id')
        self.aws_secret_access_key = my_config.get_config(config_area, 'aws_secret_access_key')
        session = Session(aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key, region_name=self.aws_region)
        self.ec2 = session.resource('ec2',config=Config(signature_version='s3v4'))
        self.ec2_client = session.client('ec2',config=Config(signature_version='s3v4'))

    def get_ec2_list(self):
        server_list = []
        for each_instance in self.ec2.instances.all():
            server_info = {}
            Name_index = [i for i, x in enumerate(each_instance.tags) if x['Key'].find('Name') != -1]
            Comman_index = [ i for i, x in enumerate(each_instance.tags) if x['Key'].find('Service') != -1]
            if Comman_index:
                comman_info = str(each_instance.tags[Comman_index[0]]['Value'])
            else:
                comman_info = '[]'
            server_info['id'] = str(uuid.uuid3(uuid.NAMESPACE_DNS,each_instance.id))
            server_info['ip'] = each_instance.private_ip_address
            server_info['hostname'] = each_instance.tags[Name_index[0]]['Value']
            server_info['port'] = '22'
            server_info['is_actice'] = 'true'
            server_info['comment'] = comman_info
            #print(server_info)
            server_list.append(server_info)
        return server_list



        # print(type(token))
if __name__ == '__main__':
    test = aws_ec2_info('aws_hmt_tha')
    # aaa = test.get_ec2_list()
    # print(aaa)
