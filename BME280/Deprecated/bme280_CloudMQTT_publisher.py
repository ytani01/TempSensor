#!/usr/bin/env python3

import sys
import time
from BME280I2C import BME280I2C
import click
import paho.mqtt.client as mqtt

#####
MYNAME		= sys.argv[0]

# BME280 senser
BME280_ADDR	= 0x76

# CloudMQTT service
HOSTNAME 	= 'm15.cloudmqtt.com'
PORT		= 26028
CA_CERT		= '/etc/ssl/certs/ca-certificates.crt'

DEF_OUTFILE	= 'out.csv'
DEF_INTERVAL	= 3600  # sec

#####
@click.command(help='BME280 MQTT publisher for CloudMQTT (temp, humidiy, pressure)')
@click.argument('user', default='')
@click.argument('pw', default='')
@click.option('--interval', '-i', type=int, default=0,
              help='interval seconds')
@click.option('--outfile', '-o', type=click.Path(), default='',
              help='output file name')
def main(user, pw, interval, outfile):
    if interval == 0:
        interval = DEF_INTERVAL
    if outfile == '':
        outfile = DEF_OUTFILE
    print('user: %s' % user)
    print('interval: %d' % interval)
    print('outfile: %s' % outfile)

    cl= mqtt.Client()
    cl.tls_set("/etc/ssl/certs/ca-certificates.crt")
    cl.username_pw_set("user1", "user1")
    cl.connect("m15.cloudmqtt.com", 26028)

    bme280 = BME280I2C(BME280_ADDR)

    prev_temp = 0.0
    prev_humidity = 0.0
    prev_pressure = 0
    prev_sec = 0
    while True:
        if not bme280.meas():
            print('Error: BME280')
            sys.exit(1)

        ts_now = time.time()
        ts_str = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(ts_now))

        update_flag = {
            'temp':	False,
            'humidity':	False,
            'pressure':	False,
            'time':	False	}
        
        if abs(bme280.T - prev_temp) >= 0.5:
            update_flag['temp'] = True
            prev_temp = bme280.T
        
            cl.publish('env1/temp', bme280.T, 0)

        if abs(bme280.H - prev_humidity) >= 5:
            update_flag['humidity'] = True
            prev_humidity = bme280.H

            cl.publish('env1/humidity', bme280.H, 0)

        if abs(bme280.P - prev_pressure) >= 2:
            update_flag['pressure'] = True
            prev_pressure = bme280.P

            cl.publish('env1/pressure', bme280.P, 0)

        if ts_now - prev_sec > interval:
            update_flag['time'] = True

            cl.publish("env1/temp", bme280.T)
            cl.publish("env1/humidity", bme280.H)
            cl.publish("env1/pressure", bme280.P)
            
        out_str = '%d ' % ts_now

        if update_flag['time']:
            out_str += '*'
        else:
            out_str += ' '
        out_str += '%s ' % ts_str

        if update_flag['temp']:
            out_str += '*'
        else:
            out_str += ' '
        out_str += '%.1f C ' % bme280.T

        if update_flag['humidity']:
            out_str += '*'
        else:
            out_str += ' '
        out_str += '%.1f %% ' % bme280.H

        if update_flag['pressure']:
            out_str += '*'
        else:
            out_str += ' '
        out_str += '%d hPa ' % bme280.P

        print(out_str)

        if True in update_flag.values():
            prev_sec = ts_now

            with open(outfile, mode='a') as f:
                f.write(out_str + '\n')

        time.sleep(5)
            
if __name__ == '__main__':
    main()
