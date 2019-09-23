#!/usr/bin/python3
# _*_ coding: UTF-8 _*_


import time
import json
import datetime
import RPi.GPIO as GPIO
from threading import Thread
from ..common.senseconf import SenseConf, SensorUtil
from ..common.sensorconf import SensorConf


class Dht11Gather(Thread):
    """
    dht11温湿度采集
    """

    def __init__(self):
        """
        初始化
        """
        Thread.__init__(self)
        self.GPIO_PIN = 17
        GPIO.setmode(GPIO.BCM)

    def gather_data(self):
        """
        传感器采集数据

        第一步操作：主机发送起始信号
            1.先设置引脚为输出，主机先拉高data；
            2.再拉低data并延迟18ms；
            3.再拉高data并把引脚设置为输入

        第二步操作：从机（dht11）收到起始信息后进行应答
            1.从机拉低data，主机读到data线被拉低持续80us后从机拉高data线持续80us
            2.直到高电平结束，意味着主机可以开始接受数据

        第三步操作：主机开始接收数据：
            1.主机先把data线拉高并把pin设置为输入
            2.从机把data线拉低，主机读取data线电平直到低电平结束（约50us）
            3.从机再拉高data线延迟40us左右（28-70us之间）主机再次读取data线电平，如果为低电平则为0，如果为高电平则为1
            4.继续重复上述1,2,3步骤累计40次

        第四步操作：主机拉低data线50us表示读取结束

        第五步操作：校验数据

        :returns 温湿度数据
        """

        # 设置GPIO引脚为输出
        GPIO.setup(self.GPIO_PIN, GPIO.OUT)
        # 设置GPIO引脚输出高电平
        GPIO.output(self.GPIO_PIN, GPIO.HIGH)
        # 延时0.05秒
        time.sleep(0.05)
        # 设置GPIO引脚输出低电平
        GPIO.output(self.GPIO_PIN, GPIO.LOW)
        # 延时0.02秒
        time.sleep(0.02)
        # 设置GPIO引脚为输入，同时上拉
        GPIO.setup(self.GPIO_PIN, GPIO.IN, GPIO.PUD_UP)

        while GPIO.input(self.GPIO_PIN) is GPIO.LOW:
            continue

        while GPIO.input(self.GPIO_PIN) is GPIO.HIGH:
            continue

        origin_data = []    # 原始温湿度数据
        count = 0   # 计数器
        while count < 40:
            temp_count = 0
            while GPIO.input(self.GPIO_PIN) is GPIO.LOW:
                continue
            while GPIO.input(self.GPIO_PIN) is GPIO.HIGH:
                temp_count += 1
                if temp_count > 100:
                    break
            if temp_count < 8:
                origin_data.append(0)
            else:
                origin_data.append(1)
            count += 1

        print(origin_data)
        humidity_bit = origin_data[0:8]
        humidity_point_bit = origin_data[8:16]
        temperature_bit = origin_data[16:24]
        temperature_point_bit = origin_data[24:32]
        check_sum_bit = origin_data[32:40]

        humidity = 0
        humidity_point = 0
        temperature = 0
        temperature_point = 0
        check_sum = 0

        for i in range(8):
            humidity += humidity_bit[i] * 2 ** (7 - i)
            humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
            temperature += temperature_bit[i] * 2 ** (7 - i)
            temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
            check_sum += check_sum_bit[i] * 2 ** (7 - i)

        GPIO.cleanup()
        if check_sum is (humidity + humidity_point + temperature + temperature_point):
            return '{}.{}'.format(temperature, temperature_point), '{}.{}'.format(humidity, humidity_point)
        else:
            return None, None

    def launcher(self):
        """
        启动获取传感器温湿度值,写入文件到指定目录
        :return:
        """

        conf_dht11 = SensorConf.get_aiot_sensor_conf_dict(self, 'dht11')
        if conf_dht11 is None:
            raise ValueError('dht11 params conf error')
        time.sleep(1)

        while True:
            temperature, humidity = self.gather_data()
            if temperature is not None or humidity is not None:
                gather_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                origin_value = dict(productid=SenseConf.get_product_id(), edgeid=SenseConf.get_edge_id(), devicedata=[
                    dict(deviceid=conf_dht11['deviceid'], gathertime=gather_time, dataname='temperature', datavalue=temperature, datatype='float'),
                    dict(deviceid=conf_dht11['deviceid'], gathertime=gather_time, dataname='humidity', datavalue=humidity, datatype='float')
                ])
                with open(SensorUtil.generate_sensor_data_file_name(), 'w') as f:
                    json.dump(origin_value, f)
            time.sleep(conf_dht11['gatherfrequency'])

    def run(self):
        print('dht11 start')
        self.launcher()
