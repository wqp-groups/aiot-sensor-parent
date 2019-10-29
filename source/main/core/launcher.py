#!/usr/bin/python3
# _*_ coding: UTF-8 _*_

from common.sensorconf import SensorConf
from dsl8b20.ds18b20 import Ds18b20Gather
from pzem.pzem016 import Pzem016Gather
from dht11.dht11 import Dht11Gather
from wristband.wristband import ScannerDevice
if __name__ == '__main__':
    conf_ds18b20 = SensorConf.get_aiot_sensor_conf_dict('ds18b20')
    if conf_ds18b20 is not None:
        if conf_ds18b20['devicerun'] is True:
            Ds18b20Gather().start()
        else:
            print('ds18b20设备未开启')

    conf_pzem016 = SensorConf.get_aiot_sensor_conf_dict('pzem016')
    if conf_pzem016 is not None:
        if conf_pzem016['devicerun'] is True:
            Pzem016Gather().start()
        else:
            print('pzem016设备未开启')

    conf_dht11 = SensorConf.get_aiot_sensor_conf_dict('dht11')
    if conf_dht11 is not None:
        if conf_dht11['devicerun'] is True:
            Dht11Gather().start()
        else:
            print('tdh11设备未开启')

    conf_wristband = SensorConf.get_aiot_sensor_conf_dict('wristband')
    if conf_wristband is not None:
        if conf_wristband['devicerun'] is True:
            ScannerDevice().start()
        else:
            print('wristband设备未开启')





