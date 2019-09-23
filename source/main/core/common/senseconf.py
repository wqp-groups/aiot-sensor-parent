#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 边缘设备感知配置类

import os
import json5
from .sensorutil import SensorUtil


class SenseConf:
    """
    边缘设备感知配置类
    __product_id：产品id
    __edge_id：边缘设备id
    __sensor_data_storage_directory：传感器采集数据存储目录
    """

    def __init__(self):
        aiot_edge_sense_config_file = os.path.join(SensorUtil.get_system_root_path(), 'aiot', 'server', 'aiotedgesenseconf.json')
        with open(aiot_edge_sense_config_file) as f:
            data = f.read()
            f.close()
            aiot_config = json5.loads(data)
            self.__product_id = aiot_config['productid']
            self.__edge_id = aiot_config['edgeid']
            self.__sensor_data_storage_directory = aiot_config['uploaddirectory']

    @staticmethod
    def get_product_id(self):
        return self.__product_id

    @staticmethod
    def get_edge_id(self):
        return self.__edge_id

    @staticmethod
    def get_sensor_data_storage_directory(self):
        return self.__sensor_data_storage_directory
