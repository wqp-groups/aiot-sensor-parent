#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 使用pzem-016传感器监控AC数据

import time
import serial
import json
import datetime
from threading import Thread
from ..common.senseconf import SenseConf
from ..common.sensorconf import SensorConf
from ..common.sensorutil import SensorUtil

__version__ = '0.0.1'


class Pzem016Gather(Thread):
    """
    交流电相关数据采集模块
    __pzem_rs485_baud_rate：波特率
    __pzem_rs485_data_bit：数据位
    __pzem_rs485_stop_bit：停止位
    __pzem_rs485_parity：校验
    __pzem_read_measurement_result：主机读取从机地址为01,指令04为读输入寄存器,寄存器地址范围0x0000-0x0009共10字节数据
    """
    __pzem_rs485_baud_rate = 9600
    __pzem_rs485_data_bit = 8
    __pzem_rs485_parity = 'N'
    __pzem_rs485_stop_bit = 1

    __pzem_read_measurement_result_command = '01040000000A700D'

    def __init__(self):
        """
        初始化
        """
        Thread.__init__(self)
        serial_port = '/dev/ttyUSB0'    # 'COM4'  # '/dev/ttyUSB1'  # '/dev/ttyAMA0'
        self.__serial_handle = serial.Serial(serial_port, baudrate=self.__pzem_rs485_baud_rate, bytesize=self.__pzem_rs485_data_bit, parity=self.__pzem_rs485_parity, stopbits=self.__pzem_rs485_stop_bit)

    def launcher(self):
        """
        启动
        主机对从机读数据操作,modbus-rtc协议：
          0x01	  03	  00 01	  00 01	     D5 CA
        从机地址	 功能号	数据地址	读取数据个数	CRC校验

        设备地址	功能代码	数据格式	CRC校验L	 CRC校验H
        8bit	8bit	N*8bit	8bit	 8bit

        从机对主机返回内容：
        0x01	03	     02	        00 17	    F8 4A
        从机地址	功能号	数据字节个数	两个字节数据	CRC校验
        :return:
        """
        if self.__serial_handle.isOpen():
            self.__serial_handle.close()
        self.__serial_handle.open()
        print('/dev/ttyUSB* open success')
        time.sleep(1)

        conf_pzem016 = SensorConf.get_aiot_sensor_conf_dict(self, 'dsl8b20')
        if conf_pzem016 is None:
            raise ValueError('pzem016 params conf error')

        while True:
            print('1')
            # 01 04 00 00 00 0A
            # write_bytes = serial.to_bytes(self.__pzem_read_measurement_result_command)
            write_bytes = bytes.fromhex(self.__pzem_read_measurement_result_command)
            print(write_bytes)
            self.__serial_handle.write(write_bytes)
            time.sleep(2)
            print('2')
            data_count = self.__serial_handle.inWaiting()
            print('3')
            print('data length:' + str(data_count))
            if data_count > 0:
                print('4')
                byte_data = self.__serial_handle.read(data_count)
                print('5')
                hex_data = byte_data.hex()
                print('接收到pzem原始数据为：' + hex_data)
                if hex_data[2:4] is '84':   # 0x84 is error code
                    continue
                dec_data = SensorUtil.hex_to_dec(hex_data)
                voltage = dec_data[6:10]       # parse voltage data 2B
                current = dec_data[10:18]      # parse current data 4B
                power = dec_data[18:26]        # parse power data 4B
                energy = dec_data[26:34]       # parse energy data 4B
                frequency = dec_data[34:38]    # parse frequency data 2B
                powerfactor = dec_data[38:42]  # parse powerfactor data 2B
                alarmstatus = dec_data[42:46]  # parse alarmstatus data 2B
                print('6')
                gather_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                origin_value = dict(productid=SenseConf.get_product_id(), edgeid=SenseConf.get_edge_id(), devicedata=[
                    dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='voltage', datavalue=voltage, datatype='float'),
                    dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='current', datavalue=current, datatype='float'),
                    dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='power', datavalue=power, datatype='float'),
                    dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='energy', datavalue=energy, datatype='float'),
                    dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='frequency', datavalue=frequency, datatype='float'),
                    dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='powerfactor', datavalue=powerfactor, datatype='float'),
                    dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='alarmstatus', datavalue=alarmstatus, datatype='int')
                ])
                print('7')
                with open(SensorUtil.generate_sensor_data_file_name(), 'w') as f:
                    print('8')
                    json.dump(origin_value, f)
                    print('9')
            self.__serial_handle.flushInput()
            time.sleep(conf_pzem016['gatherfrequency'])

    def __del__(self):
        if self.__serial_handle is not None:
            self.__serial_handle.close()

    def run(self):
        print('pzem016 start')
        self.launcher()


if __name__ == '__main__':
    Pzem016Gather().start()
