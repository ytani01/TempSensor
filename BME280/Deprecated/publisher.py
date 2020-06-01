#!/usr/bin/env python3
#
import sys
import time
import json
import paho.mqtt.client as mqtt
from BME280I2C import BME280I2C

#####
MYNAME		= sys.argv[0]
HOSTNAME 	= 'mqtt.beebotte.com'
PORT		= 8883
CACERT		= '/home/pi/mqtt.beebotte.com.pem'
BME280_ADDR	= 0x76

DEF_OUT_FILE	= 'out.csv'

DEF_INTERVAL_SEC= 300  # sec

#####
def print_usage():
    print()
    print('usage: %s token_str channel resource [interval [out_file]]' % (MYNAME))
    print()

#####
def mqtt_publish(client, topic, data_json):
    client.connect(HOSTNAME, port=PORT, keepalive=60)
    client.publish(topic, data_json)
    time.sleep(1)
    client.disconnect()

#####
def main():
    interval_sec = DEF_INTERVAL_SEC
    out_file = DEF_OUT_FILE
    
    if len(sys.argv) < 4 or len(sys.argv) > 6:
        print_usage()
        sys.exit(1)

    token_str = sys.argv[1]
    ch_name = sys.argv[2]
    res_name = sys.argv[3]
    if len(sys.argv) >= 5:
        interval_sec = int(sys.argv[4])
    if len(sys.argv) >= 6:
        out_file = sys.argv[5]
    print('token_str: %s' % token_str)
    print('ch_name: %s' % ch_name)
    print('res_name: %s' % res_name)
    print('interval_sec: %d' % interval_sec)
    print('out_file: %s' % out_file)

    topic = ch_name + '/' + res_name
    print('topic: ' + topic)

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set('token:%s' % token_str)
    client.tls_set(CACERT)

    #data_val = {'data': {'temp': 0, 'humidity': 0, 'pressure': 0}, 'ispublic': True, 'ts': 0}
    data_val = {'data': {'temp': 0, 'humidity': 0, 'pressure': 0}, 'ts': 0}

    bme280 = BME280I2C(BME280_ADDR)

    prev_temp = 0.0
    prev_sec = 0
    while True:
        if not bme280.meas():
            print('Error: BME280')
            sys.exit(1)

        ts_now = time.time()
        ts_str = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(ts_now))
        print("%s %5.2f" % (ts_str, bme280.T))
        
        if ( abs( bme280.T - prev_temp ) >= 0.5 ) or ( ts_now - prev_sec >= 3600 ):
            prev_temp = bme280.T
            prev_sec = ts_now
            
        
            ## write csv data
            out_str = '%d, %s, %.1f,C, %.1f,%%, %d,hPa' % (ts_now, ts_str, bme280.T, bme280.H, bme280.P)
            print(out_str)
            with open(out_file, mode='a') as f:
                f.write(out_str + '\n')

            ## publish json data
            data_val['data']['temp']	= int(bme280.T * 100) / 100
            data_val['data']['humidity']	= int(bme280.H * 100) / 100
            data_val['data']['pressure']	= int(bme280.P)
            data_val['ts'] = int(ts_now * 1000)
            #print(data_val)
            data_json = json.dumps(data_val)
            print(data_json)
            mqtt_publish(client, topic, data_json)

        time.sleep(interval_sec)
            
if __name__ == '__main__':
    main()
