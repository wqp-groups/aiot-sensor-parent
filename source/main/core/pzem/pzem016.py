#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 使用pzem-016传感器监控AC数据

import datetime
import json
import time
import serial
from threading import Thread
from common.fileutil import FileUtil
from common.sensorutil import SensorUtil
from common.senseconf import SenseConf
from common.sensorconf import SensorConf

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

    __pzem_read_input_register_command = '01040000000A700D'     # 读输入寄存器测量数据
    __pzem_calibration_command = 'F8413721B778'                 # 校准(工厂或维护内部使用命令)
    __pzem_reset_energy_command = '01428011'                    # 重置Energy

    def __init__(self):
        """
        初始化
        """
        Thread.__init__(self)
        self.__serial_handle = None
        self.serial_port = '/dev/ttyUSB0'    # 'COM4'  # '/dev/ttyUSB1'  # '/dev/ttyAMA0'
        try:
            self.__serial_handle = serial.Serial(self.serial_port, baudrate=self.__pzem_rs485_baud_rate, bytesize=self.__pzem_rs485_data_bit, parity=self.__pzem_rs485_parity, stopbits=self.__pzem_rs485_stop_bit)
        except (FileNotFoundError, serial.SerialException):
            print('{} open fail'.format(self.serial_port))

    def exec_command(self, command: str, waiting=2):
        """
        执行modbus协议指令
        :param command: 指令
        :param waiting: 指令执行后等待时间取结果
        :return: 应答返回16进制数据,否则None
        """
        write_bytes = bytes.fromhex(command)
        self.__serial_handle.write(write_bytes)
        time.sleep(waiting)
        data_count = self.__serial_handle.inWaiting()
        if data_count > 0:
            byte_data = self.__serial_handle.read(data_count)
            hex_data = byte_data.hex()
            print('pzem016 origin data->：{}'.format(hex_data))
            self.__serial_handle.flushInput()
            if len(hex_data) == 0:
                return None
            return hex_data
        return None

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
        if self.__serial_handle is None:
            print('pzem016 {} start fail, because usb port open error'.format(self.serial_port))
            return

        if self.__serial_handle.isOpen():
            self.__serial_handle.close()
        self.__serial_handle.open()
        print('/dev/ttyUSB* open success')
        time.sleep(1)

        conf_pzem016 = SensorConf.get_aiot_sensor_conf_dict('pzem016')
        if conf_pzem016 is None:
            raise ValueError('tips pzem016 params conf error, please check')

        # calibration slave
        # hex_calibration_result = self.exec_command(self.__pzem_calibration_command, 10)
        # if hex_calibration_result is not None and str(hex_calibration_result) == self.__pzem_calibration_command:
        #     print('pzem016 calibration success')
        # else:
        #     print('pzem016 calibration failure')

        # reset energy
        hex_reset_energy_result = self.exec_command(self.__pzem_reset_energy_command)
        if hex_reset_energy_result is not None and str(hex_reset_energy_result) == self.__pzem_reset_energy_command:
            print('pzem016 reset energy success')
        else:
            print('pzem016 reset energy failure')

        # 读取输入寄存器数据
        while True:
            hex_input_register_result = self.exec_command(self.__pzem_read_input_register_command)
            if hex_input_register_result is None or hex_input_register_result[2:4] is '84':
                print('pzem016 current gather data invalid')
                continue

            voltage = SensorUtil.hex_to_dec(hex_input_register_result[6:10])  # parse voltage data 2B
            current = SensorUtil.hex_to_dec(hex_input_register_result[10:18])  # parse current data 4B
            power = SensorUtil.hex_to_dec(hex_input_register_result[18:26])  # parse power data 4B
            energy = SensorUtil.hex_to_dec(hex_input_register_result[26:34])  # parse energy data 4B
            frequency = SensorUtil.hex_to_dec(hex_input_register_result[34:38])  # parse frequency data 2B
            powerfactor = SensorUtil.hex_to_dec(hex_input_register_result[38:42])  # parse powerfactor data 2B
            alarmstatus = SensorUtil.hex_to_dec(hex_input_register_result[42:46])  # parse alarmstatus data 2B

            # 格式化数据
            # if float(energy) < 10000.0:     #
            #     energy = float(energy) * 0.00001
            # print('pzem016 dec data->：voltage:{},current:{},power:{},energy:{},frequency:{},powerfactor:{},alarmstatus:{}'.format(voltage, current, power, energy, frequency, powerfactor, alarmstatus))
            voltage = '{:.1f}'.format(float(voltage) * 0.1)
            current = '{:.3f}'.format(float(current) * 0.00000001)
            power = '{:.1f}'.format(float(power) * 0.000001)
            energy = '{:.1f}'.format(float(energy) * 0.00001)  # 原数据单位是Wh,这里转换为kWh,所以乘0.00001,1kWh=1000Wh
            frequency = '{:.1f}'.format(float(frequency) * 0.1)
            powerfactor = '{:.2f}'.format(float(powerfactor) * 0.01)

            print('pzem016 dec format data->：voltage:{}V,current:{}A,power:{}W,energy:{}kWh,frequency:{}Hz,powerfactor:{},alarmstatus:{}'.format(voltage, current, power, energy, frequency, powerfactor, alarmstatus))
            # dec_data = SensorUtil.hex_to_dec(hex_data)
            # voltage = dec_data[6:10]       # parse voltage data 2B
            # current = dec_data[10:18]      # parse current data 4B
            # power = dec_data[18:26]        # parse power data 4B
            # energy = dec_data[26:34]       # parse energy data 4B
            # frequency = dec_data[34:38]    # parse frequency data 2B
            # powerfactor = dec_data[38:42]  # parse powerfactor data 2B
            # alarmstatus = dec_data[42:46]  # parse alarmstatus data 2B
            gather_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            origin_value = dict(productid=SenseConf.get_product_id(), edgeid=SenseConf.get_edge_id(), devicedata=[
                dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='voltage', datavalue=voltage,
                     datatype='float'),
                dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='current', datavalue=current,
                     datatype='float'),
                dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='power', datavalue=power,
                     datatype='float'),
                dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='energy', datavalue=energy,
                     datatype='float'),
                dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='frequency',
                     datavalue=frequency, datatype='float'),
                dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='powerfactor',
                     datavalue=powerfactor, datatype='float'),
                dict(deviceid=conf_pzem016['deviceid'], gathertime=gather_time, dataname='alarmstatus',
                     datavalue=alarmstatus, datatype='int')
            ])
            with open(FileUtil.generate_sensor_data_file_name(), 'w') as f:
                json.dump(origin_value, f)
            time.sleep(conf_pzem016['gatherfrequency'])

    def __del__(self):
        if self.__serial_handle is not None:
            self.__serial_handle.close()

    def run(self):
        print('pzem016 start')
        self.launcher()


if __name__ == '__main__':
    Pzem016Gather().start()
