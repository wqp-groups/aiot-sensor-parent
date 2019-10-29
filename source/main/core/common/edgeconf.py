#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 边缘设备感知配置类

import os
import json5
import uuid
from common.sensorutil import SensorUtil


class EdgeConf:
    """
    边缘设备配置类
    __product_id：产品id
    __edge_id：边缘设备id
    __sensor_data_storage_directory：传感器采集数据存储目录
    """
    __edge_conf = None
    __product_id = None
    __edge_id = None
    __sensor_data_storage_directory = None
    __mqtt_conf = None
    __netty_conf = None
    __mqtt_client_id = str(uuid.uuid4())

    @staticmethod
    def get_edge_conf():
        if EdgeConf.__edge_conf is None:
            aiot_edge_config_file = os.path.join(SensorUtil.get_system_root_path(), 'aiot', 'server', 'aiotedgeconf.json')
            with open(aiot_edge_config_file) as f:
                data = f.read()
                f.close()
                aiot_config = json5.loads(data)
                EdgeConf.__product_id = aiot_config['productid']
                EdgeConf.__edge_id = aiot_config['edgeid']
                EdgeConf.__sensor_data_storage_directory = aiot_config['uploaddirectory']
                EdgeConf.__mqtt_conf = aiot_config['mqtt']
                EdgeConf.__netty_conf = aiot_config['netty']
                EdgeConf.__edge_conf = aiot_config

        return EdgeConf.__edge_conf

    @staticmethod
    def get_product_id():
        """
        获取边缘设备产品id
        :return:
        """
        EdgeConf.get_edge_conf()
        return EdgeConf.__product_id

    @staticmethod
    def get_edge_id():
        """
        获取边缘设备id
        :return:
        """
        EdgeConf.get_edge_conf()
        return EdgeConf.__edge_id

    @staticmethod
    def get_sensor_data_storage_directory():
        """
        获取传感设备数据本地存储目录
        :return:
        """
        EdgeConf.get_edge_conf()
        return EdgeConf.__sensor_data_storage_directory

    @staticmethod
    def get_mqtt_conf():
        """
        获取mqtt配置参数
        :param key: 参数名
        :return:
        """
        if EdgeConf.__mqtt_conf is None:
            EdgeConf.get_edge_conf()

        if EdgeConf.__mqtt_conf is None:
            raise Exception('mqtt参数未配置')

        return EdgeConf.__mqtt_conf

    @staticmethod
    def get_netty_conf():
        """
        获取netty配置参数
        :return:
        """
        if EdgeConf.__netty_conf is None:
            EdgeConf.get_edge_conf()

        if EdgeConf.__netty_conf is None:
            raise Exception('netty参数未配置')

        return EdgeConf.__netty_conf

    @staticmethod
    def get_mqtt_host():
        """
        获取mqtt主机
        :return: 主机
        """
        mqtt_conf = EdgeConf.get_mqtt_conf()
        if mqtt_conf is None:
            return '127.0.0.1'
        return mqtt_conf['host']

    @staticmethod
    def get_mqtt_port():
        """
        获取mqtt端口
        :return: 端口
        """
        mqtt_conf = EdgeConf.get_mqtt_conf()
        if mqtt_conf is None:
            return 1883
        return mqtt_conf['port']

    @staticmethod
    def get_mqtt_publish_username():
        """
        获取mqtt发布端用户名
        :return: 用户名
        """
        mqtt_conf = EdgeConf.get_mqtt_conf()
        if mqtt_conf is None:
            return None
        publish = mqtt_conf['publish']
        if publish is None:
            return None
        return publish['username']

    @staticmethod
    def get_mqtt_publish_password():
        """
        获取mqtt发布端密码
        :return: 密码
        """
        mqtt_conf = EdgeConf.get_mqtt_conf()
        if mqtt_conf is None:
            return None
        publish = mqtt_conf['publish']
        if publish is None:
            return None
        return publish['password']

    @staticmethod
    def get_mqtt_subscribe_username():
        """
        获取mqtt订阅端用户名
        :return: 用户名
        """
        mqtt_conf = EdgeConf.get_mqtt_conf()
        if mqtt_conf is None:
            return None
        publish = mqtt_conf['subscribe']
        if publish is None:
            return None
        return publish['username']

    @staticmethod
    def get_mqtt_subscribe_password():
        """
        获取mqtt订阅端密码
        :return: 密码
        """
        mqtt_conf = EdgeConf.get_mqtt_conf()
        if mqtt_conf is None:
            return None
        publish = mqtt_conf['subscribe']
        if publish is None:
            return None
        return publish['password']

    @staticmethod
    def get_mqtt_client_id():
        """
        获取mqtt客户端id
        :return:
        """
        return EdgeConf.__mqtt_client_id







# if __name__ == '__main__':
#     edge_conf = EdgeConf()
#     edge_conf.get_mqtt_publish_username()




