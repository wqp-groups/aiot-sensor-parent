#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: mqtt客户端

from common.edgeconf import EdgeConf
from paho.mqtt import subscribe, client, publish


class MqttClient:
    """
    Mqtt 客户端
    提供发布主题处理
    提供订阅主题处理
    """

    def __init__(self):
        pass

    @staticmethod
    def publish(messages):
        """
        发布主题数据(多主题)
        :param messages:
        :return:
        """
        publish.multiple(msgs=messages, hostname=EdgeConf.get_mqtt_host(), port=EdgeConf.get_mqtt_port(),
                         client_id=EdgeConf.get_mqtt_client_id(), keepalive=15, will=None,
                         auth=dict(username=EdgeConf.get_mqtt_publish_username(), password=EdgeConf.get_mqtt_publish_password()), tls=None, protocol=client.MQTTv311,
                         transport='tcp')
        print('publish success')

    @staticmethod
    def publish(topic: str, message: str):
        """
        发布主题数据(单主题)
        :param topic: 主题
        :param message: 数据
        :return:
        """
        publish.single(topic=topic, payload=message, qos=2,
                       retain=False, hostname=EdgeConf.get_mqtt_host(), port=EdgeConf.get_mqtt_port(),
                       client_id=EdgeConf.get_mqtt_client_id(), keepalive=15, will=None,
                       auth=dict(username=EdgeConf.get_mqtt_publish_username(), password=EdgeConf.get_mqtt_publish_password()), tls=None, protocol=client.MQTTv311,
                       transport='tcp')
        print('publish success')

    @staticmethod
    def subscribe(topics: str, callback):
        """
        订阅主题数据
        :param topics: 主题
        :param callback: 主题数据回调
        :return:
        """
        subscribe.callback(callback=callback, topics=topics, qos=2,
                           userdata=None, hostname=EdgeConf.get_mqtt_host(), port=EdgeConf.get_mqtt_port(),
                           client_id=EdgeConf.get_mqtt_client_id(), keepalive=15, will=None,
                           auth=dict(username=EdgeConf.get_mqtt_subscribe_username(), password=EdgeConf.get_mqtt_subscribe_password()), tls=None, protocol=client.MQTTv311,
                           transport='tcp', clean_session=True)
        print('subscribe success')



