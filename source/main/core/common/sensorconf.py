#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 传感设备配置类

import os
import json5
from common.sensorutil import SensorUtil


class SensorConf:
    """
    传感设备配置类
    """
    __sensor_conf = None

    @staticmethod
    def get_sensor_conf():
        """
        加载配置文件
        :return:
        """
        if SensorConf.__sensor_conf is None:
            aiot_edge_sense_config_file = os.path.join(SensorUtil.get_system_root_path(), 'aiot', 'server', 'aiotsensorconf.json')
            with open(aiot_edge_sense_config_file) as f:
                data = f.read()
                f.close()
                sensor_conf = json5.loads(data)
                SensorConf.__sensor_conf = sensor_conf

        return SensorConf.__sensor_conf

    @staticmethod
    def get_aiot_sensor_conf_list() -> list:
        """
        获取传感设备配置参数列表
        :return: 全部传感设备参数列表
        """
        return SensorConf.get_sensor_conf()

    @staticmethod
    def get_aiot_sensor_conf_dict(conf_alias: object) -> object:
        """
        获取传感设备配置参数
        :param conf_alias: 配置参数别名
        :return: 指定传感设备参数配置字典，不存在返回None
        """
        for conf in SensorConf.get_sensor_conf():
            # status = CharUtil.equal(conf['devicealias'], conf_alias)
            if conf['devicealias'] == conf_alias:
                return conf
        return None
        # conf_list = [conf for conf in self.aiot_sensor_conf if conf['devicealias'] == conf_alias]
        # if len(conf_list) > 0:
        #     return conf_list[0]
        # else:
        #     return None
