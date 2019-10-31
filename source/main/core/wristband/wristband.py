#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note:使用raspberry pi蓝牙功能向手环发送数据，在手环上显示

from bluepy.btle import Scanner, Peripheral, ADDR_TYPE_RANDOM, BTLEException, BTLEDisconnectError
from threading import Thread
from common.mqttclient import MqttClient, MqttSubscribeCallback
from common.edgeconf import EdgeConf
from common.sensorconf import SensorConf
from queue import Queue
import sched
import time
import binascii
import json5

__version__ = '0.0.1'

# 手环订阅接接收收消息队列
wristband_receive_message_queue = Queue(maxsize=0)

scanner_device_name = 'V2'
# 扫描有效设备mac列表
scanner_device_list = []


def subscribe_receive_message(client, userdata, message):
    print('receive mqtt message: {}'.format(message))
    # 接收到的消息创建任务存入队列
    # 生产任务放入队列中
    wristband_receive_message_queue.put(item=JobTask(create_time=time.time(), origin_data=message.payload))


class ScannerDevice(Thread):
    """
    定时扫描设备线程类
    """
    def __init__(self):
        Thread.__init__(self)
        pass

    def run(self):
        print('wristband start')
        # 启动设备扫描
        TimeScannerDevice().start()
        # 启动设备消息订阅
        WristBandMqttSubscribe().start()
        # 启动发送数据到设备
        WristbandConsumerQueue().start()

    def __del__(self):
        """
        销毁定时扫描任务
        :return:
        """
        # self.scheduler.cancel(self.launcher())


class SendDataToDevice:
    """
    发送数据到手环设备（内部采用异步调用执行发送处理）
    发送数据指令格式 : 操作码(1字节) + 数据长度(1字节) + state(1byte) + content(n byte)
    data format : opcode(1byte) + datalength(1byte) + state(1byte) + content(n byte)
    """

    def __init__(self, origin_data):
        """
        初始化发送数据到设备
        :param origin_data: 原始数据, 示例：{title:'标题',content:'内容'}
        """
        # 待发送到手环的原始数据
        self.origin_data = origin_data
        # 发送数据到手环开始指令
        self.command_send_data_start = 'a403000002'
        # 发送数据到手环结束指令
        self.command_send_data_end = 'a40103'

    def dispatch_task(self):
        """
        按设备派发任务发送数据
        :return:
        """
        for device_addr in scanner_device_list:
            self.send_data(device_addr, self.origin_data)

    def send_data(self, device_addr: str, origin_data):
        """
        异常执行-发送数据到设备
        :param device_addr: 设备地址
        :param origin_data 待发送的原始数据
        :return:
        """
        # 此处需要把原始数据转换为字典数据，示例：{title:'标题',content:'内容'}
        # print('origin_data:{}'.format(origin_data))
        # data_str = binascii.a2b_hex(origin_data)  # 16 -> str
        data_dict = json5.loads(origin_data)

        # 优先连接手环设备
        try:
            peripheral = Peripheral(deviceAddr=device_addr, addrType=ADDR_TYPE_RANDOM, iface=0)
        except BTLEException as e:
            print('连接手环蓝牙失败了 {}'.format(e))
            return

        # 发送数据到手环标题指令(字符串转16进制)
        hex_data_title_origin = binascii.b2a_hex(data_dict['title'].encode())
        command_send_data_title = 'a4' + hex(len(hex_data_title_origin) + 1)[2:].zfill(2) + '01' + str(hex_data_title_origin).strip('b').strip("'")
        # 发送数据到手环内容指令(字符串转16进制)
        hex_data_content_origin = binascii.b2a_hex(data_dict['payload'].encode())
        command_send_data_content = 'a4' + hex(len(hex_data_content_origin) + 1)[2:].zfill(2) + '02' + str(hex_data_content_origin).strip('b').strip("'")

        # 正常连接到设备蓝牙
        time.sleep(1)
        peripheral.writeCharacteristic(handle=29, val=binascii.a2b_hex(self.command_send_data_start))
        time.sleep(0.1)
        peripheral.writeCharacteristic(handle=29, val=binascii.a2b_hex(command_send_data_title))
        time.sleep(0.1)
        peripheral.writeCharacteristic(handle=29, val=binascii.a2b_hex(command_send_data_content))
        time.sleep(0.1)
        peripheral.writeCharacteristic(handle=29, val=binascii.a2b_hex(self.command_send_data_end))


class TimeScannerDevice(Thread):

    def __init__(self):
        Thread.__init__(self)
        # 创建扫描设备定时调度器
        self.scheduler = sched.scheduler(time.time, time.sleep)
        # 定时任务延迟时间
        self.scheduler_delay = 5

    def run(self) -> None:
        # 设备手环设备扫描定时任务
        self.scheduler.enter(delay=self.scheduler_delay, priority=0, action=self.launcher_scanner())
        self.scheduler.run()

    def scanner_device(self):
        """
        执行一次设备扫描处理
        注：仅获取设备名称为V2的手环设备
        :return:
        """
        print('scan device running')
        # ScannerDevice.__scanner_device_list.clear()
        scanner = Scanner()
        try:
            devices = scanner.scan()
        except BTLEDisconnectError as be:
            print(be)
            return

        for device in devices:
            new_device_name = str(device.getValueText(9))
            if scanner_device_name.lower() in new_device_name.lower():
                if device.addr not in scanner_device_list:
                    scanner_device_list.append(device.addr)
                    print('Scanner new wristband ble mac address:{}'.format(device.addr))

    def launcher_scanner(self):
        """

        :return:
        """
        self.scanner_device()
        self.scheduler.enter(delay=self.scheduler_delay, property=0, action=self.launcher_scanner())


class WristBandMqttSubscribe(Thread):
    """
    手环订阅主题消息类
    """

    def __init__(self):
        Thread.__init__(self)

    def run(self) -> None:
        # mqtt方式订阅手环消息
        wristband_conf = SensorConf.get_aiot_sensor_conf_dict('wristband')
        if wristband_conf is not None:
            topic = 'aiot/' + EdgeConf.get_product_id() + '/' + EdgeConf.get_edge_id() + '/' + wristband_conf['deviceid']
            MqttClient.subscribe(topic, subscribe_receive_message)
        else:
            print('wristband参数未配置,启动订阅失败')


class JobTask:
    """
    工作任务类
    """
    def __init__(self, create_time, origin_data):
        self.create_time = create_time
        self.origin_data = origin_data

    def execute(self):
        """
        执行任务（发送数据）
        :return:
        """
        SendDataToDevice(origin_data=self.origin_data).dispatch_task()


class WristbandConsumerQueue(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self) -> None:
        # 暂停3秒等待设备扫描启动
        time.sleep(3)

        # 消费任务从队列取出
        while True:
            if (scanner_device_list is not None) and (scanner_device_list.__len__() > 0) :
                if wristband_receive_message_queue.empty():
                    pass
                else:
                    job_task = wristband_receive_message_queue.get()
                    job_task.execute()
            time.sleep(1)
            print('No task to consumer')


