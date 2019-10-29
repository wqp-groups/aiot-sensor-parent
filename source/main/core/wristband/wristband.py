#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note:使用raspberry pi蓝牙功能向手环发送数据，在手环上显示

from bluepy.btle import Scanner, Peripheral, UUID, ADDR_TYPE_RANDOM
from threading import Thread
from mqtt.mqttclient import MqttClient
from common.edgeconf import EdgeConf
from common.sensorconf import SensorConf
import sched
import time
import binascii


class ScannerDevice(Thread):
    """
    定时扫描设备线程类
    """

    def __init__(self):
        Thread.__init__(self)
        # 创建扫描设备定时调度器
        self.scheduler = sched.scheduler(time.time, time.sleep)
        # 定时任务延迟时间
        self.scheduler_delay = 5
        # 扫描有效设备mac列表
        self.scanner_device_list = []

    def scanner_device(self):
        """
        执行一次设备扫描处理
        注：仅获取设备名称为V2的手环设备
        :return:
        """
        self.scanner_device_list.clear()
        scanner = Scanner()
        devices = scanner.scan()
        for device in devices:
            if str(device.getValueType(9)).strip() == 'V2':
                self.scanner_device_list.append(device.addr)

    @staticmethod
    def get_scanner_device_list(self):
        """
        获取已扫描到的设备列表
        :return:
        """
        return self.scanner_device_list

    def launcher(self):
        self.scanner_device()
        self.scheduler.enter(self.scheduler_delay, 0, self.launcher())

    def run(self):
        print('wristband start')
        self.scheduler.enter(self.scheduler_delay, 0, self.launcher())
        self.scheduler.run()

    def __del__(self):
        self.scheduler.cancel(self.launcher())


class SendDataToDevice:
    """
    发送数据到手环设备
    发送数据指令格式 : 操作码(1字节) + 数据长度(1字节) + state(1byte) + content(n byte)
    data format : opcode(1byte) + datalength(1byte) + state(1byte) + content(n byte)
    """

    def __init__(self):
        # 创建发送数据到设备调度器
        self.scheduler = sched.scheduler(time.time(), time.sleep())

        # 发送数据到手环开始指令
        self.command_send_data_start = 'a403000002'
        # 发送数据到手环结束指令
        self.command_send_data_end = 'a40103'

    def dispatch_task(self, data: dict):
        """
        按设备派发任务发送数据
        :param data: 数据, 示例：{title:'标题',content:'内容'}
        :return:
        """
        device_list = ScannerDevice.get_scanner_device_list()
        for device_addr in device_list:
            self.scheduler.enter(0, 0, self.send_data(device_addr, data), ())
            self.scheduler.run(blocking=False)

    def send_data(self, device_addr: str, data: dict):
        """
        发送数据到设备
        :param device_addr: 设备地址
        :param data: 数据, 示例：{title:'标题',content:'内容'}
        :return:
        """
        # 发送数据到手环标题指令(字符串转16进制)
        hex_data_title_origin = binascii.b2a_hex(data['title'].encode())
        hex_data_title_length = '{0}'.format(hex(len(hex_data_title_origin) + 1)).zfill(2)
        command_send_data_title = 'a4' + hex_data_title_length + '01' + hex_data_title_origin
        # 发送数据到手环内容指令(字符串转16进制)
        hex_data_content_origin = binascii.b2a_hex(data['content'].encode())
        hex_data_content_length = '{0}'.format(hex(len(hex_data_content_origin) + 1)).zfill(2)
        command_send_data_content = 'a4' + hex_data_content_length + '02' + hex_data_content_origin

        peripheral = Peripheral(deviceAddr=device_addr, addrType=ADDR_TYPE_RANDOM, iface=0)
        time.sleep(1)
        peripheral.writeCharacteristic(handle=29, val=binascii.a2b_hex(self.command_send_data_start))
        time.sleep(0.1)
        peripheral.writeCharacteristic(handle=29, val=binascii.a2b_hex(command_send_data_title))
        time.sleep(0.1)
        peripheral.writeCharacteristic(handle=29, val=binascii.a2b_hex(command_send_data_content))
        time.sleep(0.1)
        peripheral.writeCharacteristic(handle=29, val=binascii.a2b_hex(self.command_send_data_end))


def mqtt_subscribe_callback(client, userdata, message):
    print("%s %s" % (message.topic, message.payload))
    SendDataToDevice().dispatch_task(data=dict(title='标题', content=message.payload))


if __name__ == '__main__':
    # 手环设备扫描
    ScannerDevice().start()
    # mqtt方式订阅手环消息
    wristband_conf = SensorConf.get_aiot_sensor_conf_dict('wristband')
    if wristband_conf is not None:
        topics = 'aiot/' + EdgeConf.get_product_id() + '/' + EdgeConf.get_edge_id() + '/' + wristband_conf['deviceid']
        MqttClient.subscribe(topics, mqtt_subscribe_callback)
    else:
        print('wristband参数未配置,启动订阅失败')

