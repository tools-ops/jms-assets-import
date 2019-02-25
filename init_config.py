#
import configparser
import logging

my_config = configparser.ConfigParser()
config_path='aws_config.ini'

def log_format():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    return logger
    # logger.info('This is a log info')
    # logger.debug('Debugging')
    # logger.warning('Warning exists')
    # logger.info('Finish')

class ConfigParser():
    def get_config(clf,sector, item):
            cf = configparser.ConfigParser()
            cf.read(config_path, encoding='utf8')  #注意setting.ini配置文件的路径
            value = cf.get(sector, item)
            return value


if __name__ == '__main__':
    my_config = ConfigParser()
    print(my_config.get_config('jms_config', 'jms_password'))
