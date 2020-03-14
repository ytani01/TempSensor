#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
# MqttSubscriber
#  simple sample
#
from MqttClientServer import BeebotteSubscriber
import sys

argv = sys.argv

def cb_func(data, ts):
    print(data, ts)

s = BeebotteSubscriber(cb_func,
                       ['env2/temperature', 'env2/humidity', 'env2/data1'],
                       'token_fAgsMSNhR9hCJOKm', debug=False)
s.start()

while True:
    pass
