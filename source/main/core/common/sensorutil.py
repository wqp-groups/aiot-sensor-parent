#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 传感设备工具类

import datetime
import os
import platform
import crcmod
from source.main.core.common.senseconf import SenseConf


class SensorUtil:
    """
    传感设备工具类
    __count_sequence_number：计数下标编号,默认从0开始,累加至999循环
    """
    __count_sequence_number = 0

    def __generate_count_sequence(self) -> str:
        """
        生成序号编码
        :return: 序列编码
        """
        if self.__count_sequence_number > 999:
            self.__count_sequence_number = 1
        else:
            self.__count_sequence_number += 1
        return "{0}".format(self.__count_sequence_number).zfill(3)

    @staticmethod
    def generate_sensor_data_file_name(self) -> str:
        """
        统一生成传感设备数据文件名称
        :return: 新文件名称(绝对路径)
        """
        postfix = SenseConf.get_product_id() + '_' + SenseConf.get_edge_id() + '_GD_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_' + self.__generate_count_sequence() + '.json'
        if not os.path.exists(SenseConf.get_sensor_data_storage_directory()):
            os.makedirs(SenseConf.get_sensor_data_storage_directory())
        return os.path.join(SenseConf.get_sensor_data_storage_directory(), postfix)

    @staticmethod
    def get_system_root_path():
        """
        获取当前系统业务根路径
        :return:
        """
        if platform.platform().lower().startswith('windows'):
            return 'd:\\'
        else:
            return '/'

    @staticmethod
    def hex_to_dec(hex_data: str = None):
        """
        十六进制数据转十进制数据
        :param hex_data:
        :return:
        """
        if hex_data is None: return None
        return int(hex_data, 16)

    @staticmethod
    def dec_to_hex(dec_data: str = None):
        """
        十进制数据转十六进制数据
        :param dec_data:
        :return:
        """
        if dec_data is None: return None
        return dec_data
        pass

    @staticmethod
    def hex_to_bin(hex_data: str = None):
        """
        十六进制转二进制
        :param hex_data:
        :return:
        """
        if hex_data is None: return None

        pass

    @staticmethod
    def crc_16_compute_modbus_trc(hex_str_data: str = None):
        """
        modbus-rtc协议下计算16位CRC校验和,多项式X16+X15+X2+1
        :param hex_str_data:
        :return:
        """
        if hex_str_data is None:
            return None
        crc16_func = crcmod.mkCrcFun(0x18005, 0xFFFF, True, 0x0000)
        return hex(crc16_func(bytes.fromhex(hex_str_data)))
