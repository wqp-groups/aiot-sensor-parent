#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

# Note: 字符工具类

import operator

class CharUtil:

    @staticmethod
    def equal(str1: str, str2: str):
        """
        判断两个字符串是否相等
        :param str1: 第1个字符串
        :param str2: 第2个字符串
        :return: Ture表示相等,否则False
        """
        if len(str1) != len(str2):
            return False
        str1_list = list(str1)
        str2_list = list(str2)
        for x1, x2 in zip(str1_list, str2_list):
            if x1 == x2:
                continue
            else:
                return False

        return True





