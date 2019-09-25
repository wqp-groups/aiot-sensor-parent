#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 文件工具类

import os
import datetime
from common.senseconf import SenseConf


class FileUtil:
    """
    文件工具类
    __count_sequence_number：计数下标编号,默认从0开始,累加至999循环
    """
    __count_sequence_number = 0

    @staticmethod
    def __generate_count_sequence() -> str:
        """
        生成序号编码
        :return: 序列编码
        """
        if FileUtil.__count_sequence_number > 999:
            FileUtil.__count_sequence_number = 1
        else:
            FileUtil.__count_sequence_number += 1
        return "{0}".format(FileUtil.__count_sequence_number).zfill(3)

    @staticmethod
    def generate_sensor_data_file_name() -> str:
        """
        统一生成传感设备数据文件名称
        :return: 新文件名称(绝对路径)
        """
        postfix = SenseConf.get_product_id() + '_' + SenseConf.get_edge_id() + '_GD_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_' + FileUtil.__generate_count_sequence() + '.json'
        if not os.path.exists(SenseConf.get_sensor_data_storage_directory()):
            os.makedirs(SenseConf.get_sensor_data_storage_directory())
        return os.path.join(SenseConf.get_sensor_data_storage_directory(), postfix)
