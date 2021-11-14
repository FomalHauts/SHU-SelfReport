import os
import sys
import configparser


# 目录路径
config_path = os.path.dirname(os.path.abspath(__file__))    # 配置文件目录路径
root_path = os.path.split(config_path)[0]                   # 根目录

sys.path.insert(0, root_path)
sys.path.insert(0, config_path)

class DictParser(configparser.ConfigParser):
    """transfer config content into dict.

    Args:
        configparser (class): original class to read config file.
    """
    def format_to_dict(self):
        d = dict(self._sections)
        for key in d:
            d[key] = dict(self._defaults, **d[key])
            d[key].pop('__name__', None)
        return d

cf = DictParser()
cf.read(os.path.join(config_path, "autoreport.conf"), encoding='utf8')

config = cf.format_to_dict()

