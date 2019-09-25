#!/usr/bin/python3
# _*_ coding: UTF-8 _*_


import time
import json
import datetime
# import RPi.GPIO as GPIO
import Adafruit_DHT as DHT
from threading import Thread
from common.fileutil import FileUtil
from common.sensorconf import SensorConf
from common.senseconf import SenseConf


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

#    def gather_data(self):

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

        """
        origin_data = []  # 原始温湿度数据
        count_sequence = 0  # 计数器

        GPIO.setmode(GPIO.BCM)                      # 设置GPIO模式为BCM
        time.sleep(1)                               # 延时1秒
        GPIO.setup(self.GPIO_PIN, GPIO.OUT)         # 设置GPIO引脚为输出
        GPIO.output(self.GPIO_PIN, GPIO.LOW)        # 输出电平拉低
        time.sleep(0.02)                            # 延时0.02秒，提示传感器开始工作
        GPIO.output(self.GPIO_PIN, GPIO.PUD_UP)     # 输出电平拉高
        GPIO.setup(self.GPIO_PIN, GPIO.IN)          # 设置GPIO引脚为输入

        print(2)
        while GPIO.input(self.GPIO_PIN) is GPIO.LOW:    # 跳过从机初始状态的低电平
            continue
        print(3)
        while GPIO.input(self.GPIO_PIN) is GPIO.HIGH:   # 跳过从机初始状态的高电平
            continue
        print(4)
        # origindata = 0
        # 主机开始接收数据,从机每次传数据会先拉低50us后再拉高
        while count_sequence < 40:
            temp_count = 0
            while GPIO.input(self.GPIO_PIN) is GPIO.LOW:    # 跳过从机状态的低电平（约50us）
                continue
            # time.sleep(0.000004)
            # origin_data.append(GPIO.input(self.GPIO_PIN))
            # while GPIO.input(self.GPIO_PIN) is GPIO.HIGH:   # 跳过从机状态的高电平（0为26us~28us,1为70us,注:上面已延时40us）
            #     print('5-3')
            #     continue
            # print('5-4')
            time.sleep(0.04)
            if GPIO.input(self.GPIO_PIN) is GPIO.HIGH:
                origin_data.append(1)
                print('5-2')
                while GPIO.input(self.GPIO_PIN) is GPIO.HIGH:
                    temp_count += 1
                    if temp_count > 100:
                        print('5-3')
                        break
            else:
                origin_data.append(0)
            count_sequence += 1
        
        print('dht11采集原始数据:{}'.format(origin_data))

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

        print('dht11->3')
        print('dht11->3-1, humidity:{},humidity_point:{},temperature:{},temperature_point:{},check_sum:{}'.format(humidity, humidity_point, temperature, temperature_point, check_sum))
        if check_sum is (humidity + humidity_point + temperature + temperature_point):
            return '{}.{}'.format(temperature, temperature_point), '{}.{}'.format(humidity, humidity_point)
        else:
            return None, None
        """

    def launcher(self):
        """
        启动获取传感器温湿度值,写入文件到指定目录
        :return:
        """
        conf_dht11 = SensorConf.get_aiot_sensor_conf_dict('dht11')
        if conf_dht11 is None:
            raise ValueError('tips dht11 params conf error, please check')
        time.sleep(1)

        while True:
            humidity, temperature = DHT.read_retry(DHT.DHT11, self.GPIO_PIN)
            print('dht11->temperature:{},humidity:{}'.format(temperature, humidity))
            if temperature is not None or humidity is not None:
                gather_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                origin_value = dict(productid=SenseConf.get_product_id(), edgeid=SenseConf.get_edge_id(), devicedata=[
                    dict(deviceid=conf_dht11['deviceid'], gathertime=gather_time, dataname='temperature', datavalue=temperature, datatype='float'),
                    dict(deviceid=conf_dht11['deviceid'], gathertime=gather_time, dataname='humidity', datavalue=humidity, datatype='float')
                ])
                with open(FileUtil.generate_sensor_data_file_name(), 'w') as f:
                    json.dump(origin_value, f)
            time.sleep(conf_dht11['gatherfrequency'])

    def run(self):
        print('dht11 start')
        self.launcher()
