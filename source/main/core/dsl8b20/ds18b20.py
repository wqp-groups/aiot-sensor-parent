#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: ds18b20 data pin must be connected to gpio4

import datetime
import json
import os
import re
import time
from threading import Thread
from common.fileutil import FileUtil
from common.sensorutil import SensorUtil
from common.sensorconf import SensorConf
from common.edgeconf import EdgeConf

__version__ = '0.0.1'


class Ds18b20Gather(Thread):
    """
    __ds18b20_data_files：ds18b20数据路径(支持多设备)
    """
    __ds18b20_data_files = []

    def __init__(self):
        """
        初始化
        """
        Thread.__init__(self)
        path = os.path.join(SensorUtil.get_system_root_path(), 'sys', 'bus', 'w1', 'devices')
        for p in os.listdir(path):
            if re.match('28-\\w+', p):
                self.__ds18b20_data_files.append(os.path.join(path, p, 'w1_slave'))

    @staticmethod
    def gather_data(data_file) -> float:
        """
        传感器采集数据
        :return: 实际温度值
        """
        with open(data_file) as f:
            data = f.read()
            f.close()
            if data.find('YES'):
                index = data.find('t=')
                return float(data[index + 2:]) / 1000
            else:
                return None

    def launcher(self):
        """
        启动获取传感器温度值,写入文件到指定目录
        :return:
        """

        conf_ds18b20 = SensorConf.get_aiot_sensor_conf_dict('ds18b20')
        if conf_ds18b20 is None:
            raise ValueError('tips dsl8b20 params conf error, please check')

        while True:
            for df in self.__ds18b20_data_files:
                value = self.gather_data(df)
                if value:
                    origin_value = dict(productid=EdgeConf.get_product_id(), edgeid=EdgeConf.get_edge_id(), devicedata=[
                        dict(deviceid=conf_ds18b20['deviceid'], gathertime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), dataname='temperature', datavalue=value, datatype='float')
                    ])
                    with open(FileUtil.generate_sensor_data_file_name(), 'w') as f:
                        json.dump(origin_value, f)
            time.sleep(conf_ds18b20['gatherfrequency'])

    def run(self):
        print('ds18b20 start')
        self.launcher()
