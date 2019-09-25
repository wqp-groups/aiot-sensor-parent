#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 边缘设备感知配置类

import os
import json5
from common.sensorutil import SensorUtil

__product_id = ''
__edge_id = ''
__sensor_data_storage_directory = ''


class SenseConf:
    """
    边缘设备感知配置类
    __product_id：产品id
    __edge_id：边缘设备id
    __sensor_data_storage_directory：传感器采集数据存储目录
    """
    __sensor_conf = None
    __product_id = None
    __edge_id = None
    __sensor_data_storage_directory = None

    @staticmethod
    def get_sense_conf():
        if SenseConf.__sensor_conf is None:
            aiot_edge_sense_config_file = os.path.join(SensorUtil.get_system_root_path(), 'aiot', 'server',
                                                       'aiotedgesenseconf.json')
            with open(aiot_edge_sense_config_file) as f:
                data = f.read()
                f.close()
                aiot_config = json5.loads(data)
                SenseConf.__product_id = aiot_config['productid']
                SenseConf.__edge_id = aiot_config['edgeid']
                SenseConf.__sensor_data_storage_directory = aiot_config['uploaddirectory']
                SenseConf.__sensor_conf = aiot_config

        return SenseConf.__sensor_conf

    @staticmethod
    def get_product_id():
        SenseConf.get_sense_conf()
        return SenseConf.__product_id

    @staticmethod
    def get_edge_id():
        SenseConf.get_sense_conf()
        return SenseConf.__edge_id

    @staticmethod
    def get_sensor_data_storage_directory():
        SenseConf.get_sense_conf()
        return SenseConf.__sensor_data_storage_directory
