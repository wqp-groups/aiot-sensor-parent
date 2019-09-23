#!/usr/bin/python3
# _*_ coding: UTF-8 _*_


from .dsl8b20.ds18b20 import Ds18b20Gather
from .dht11.dht11 import Dht11Gather
from .pzem.pzem016 import Pzem016Gather

if __name__ == '__main__':
    Ds18b20Gather().start()
    Dht11Gather().start()
    Pzem016Gather().start()
