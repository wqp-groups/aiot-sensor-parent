#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 传感设备配置类

import os
import json5
from .sensorutil import SensorUtil


class SensorConf:
    """
    传感设备配置类
    """

    def __init__(self):
        aiot_edge_sense_config_file = os.path.join(SensorUtil.get_system_root_path(), 'aiot', 'server',
                                                   'aiotedgesensorconf.json')
        with open(aiot_edge_sense_config_file) as f:
            data = f.read()
            f.close()
            self.___aiot_sensor_conf = json5.loads(data)

    @staticmethod
    def get_aiot_sensor_conf_list(self) -> list:
        """
        获取传感设备配置参数列表
        :param self: 上下文
        :return: 全部传感设备参数列表
        """
        return self.___aiot_sensor_conf

    @staticmethod
    def get_aiot_sensor_conf_dict(self, conf_alias) -> dict:
        """
        获取传感设备配置参数
        :param self: 上下文
        :param conf_alias: 配置参数别名
        :return: 指定传感设备参数配置字典，不存在返回None
        """
        conf_list = [conf for conf in self.___aiot_sensor_conf if conf['devicealias'] == conf_alias]
        if len(conf_list) > 0:
            return conf_list[0]
        else:
            return None
