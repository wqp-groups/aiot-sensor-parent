#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 传感设备工具类

import platform
import crcmod


class SensorUtil:
    """
    传感设备工具类
    """

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
        if hex_data is None:
            return None
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


if __file__ == '__main__':
    params = '01041408970000000000000000001e000001f300000000a8c5'
    print(int(params, 16))
