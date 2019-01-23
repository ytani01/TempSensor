#!/usr/bin/env python3
#
import sys
import time
from SHT31 import SHT31
from beebotte import *

import click

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, WARN
logger = getLogger(__name__)
logger.setLevel(INFO)
handler = StreamHandler()
handler.setLevel(DEBUG)
handler_fmt = Formatter('%(asctime)s %(levelname)s %(name)s:%(funcName)s> %(message)s',
                        datefmt='%H:%M:%S')
handler.setFormatter(handler_fmt)
logger.addHandler(handler)
logger.propagate = False
def get_logger(name, debug=False):
    l = logger.getChild(name)
    if debug:
        l.setLevel(DEBUG)
    else:
        l.setLevel(INFO)
    return l

#####
MYNAME		= sys.argv[0]
HOSTNAME 	= 'api.beebotte.com'
SHT31_ADDR	= '0x45'

DEF_OUTFILE	= 'sht31.txt'
DEF_INTERVAL	= 120  # sec

#####
class app:
    DIFF_HUMIDITY = 5	# %
    LOOP_INTERVAL = 10	# sec
    
    def __init__(self, bus, addr_str, token_str, ch_name, interval, outfile,
                 debug=False):
        self.logger = get_logger(__class__.__name__, debug)

        self.logger.debug('bus      : %d', bus)
        self.logger.debug('addr_str : \'%s\'', addr_str)
        self.logger.debug('token_str: %s', token_str)
        self.logger.debug('token_str: %s', token_str)
        self.logger.debug('ch_name  : %s', ch_name)
        self.logger.debug('interval : %d', interval)
        self.logger.debug('outfile  : %s', outfile)

        self.bus       = bus
        
        if addr_str[:2] != '0x':
            self.logger.error('%s is not a valid hex value', addr_str)
            return None
        self.addr      = int(addr_str[2:], 16)
        
        self.token_str = token_str
        self.ch_name   = ch_name
        self.interval  = interval
        self.outfile   = outfile
        
        self.bbt = BBT(token=token_str, hostname=HOSTNAME)
        self.sht31 = SHT31(self.bus, self.addr, debug=debug)

    def main(self):
        prev = {}
        prev['temp']     = 0.0
        prev['humidity'] = 0.0
        prev['sec']      = 0

        while True:
            if not self.sht31.measure():
                self.logger.error('Error')
                sys.exit(1)

            update_mark = {'temp'    : ' ',
                           'humidity': ' ',
                           'time'    : ' ' }

            ts_now = time.time()
            ts_str = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(ts_now))
            if ts_now - prev['sec'] >= self.interval:
                update_mark['time'] = '*'
            out_str =  '%d %s%s '  % (ts_now, update_mark['time'], ts_str)

            if abs(self.sht31.temp - prev['temp']) \
               >= self.DIFF_TEMP:
                update_mark['temp'] = '*'
            out_str += '%s%.1f C ' % (update_mark['temp'], self.sht31.temp)

            if abs(self.sht31.humidity - prev['humidity']) \
               >= self.DIFF_HUMIDITY:
                update_mark['humidity'] = '*'
            out_str += '%s%.1f %%' % (update_mark['humidity'],
                                      self.sht31.humidity)
            print(out_str)

            if '*' in update_mark.values():
                self.bbt.write(self.ch_name, "temp",
                               float('%.1f' % self.sht31.temp))
                self.bbt.write(self.ch_name, "humidity",
                               float('%.1f' % self.sht31.humidity))

                prev['temp']     = self.sht31.temp
                prev['humidity'] = self.sht31.humidity
                prev['sec']      = ts_now

                with open(self.outfile, mode='a') as f:
                    f.write(out_str + '\n')

            time.sleep(self.LOOP_INTERVAL)
        
#####
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS, 
               help='SHT-31 MQTT publisher (temp, humidity)')
@click.argument('token_str', default='')
@click.argument('ch_name'  , default='')
@click.option('--bus', '-b', 'i2cbus', type=int, default=1,
              help='I2C bus')
@click.option('--addr', '-a', 'i2caddr', type=str, default=SHT31_ADDR,
              help='I2C addr')
@click.option('--interval', '-i', 'interval', type=int, default=DEF_INTERVAL,
              help='interval seconds')
@click.option('--outfile', '-o', 'outfile', type=click.Path(),
              default=DEF_OUTFILE,
              help='output file name')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(i2cbus, i2caddr, token_str, ch_name, interval, outfile, debug):
    if debug:
        logger.setLevel(DEBUG)
        
    logger.debug('token_str: %s', token_str)
    logger.debug('ch_name  : %s', ch_name)
    logger.debug('interval : %d', interval)
    logger.debug('outfile  : %s', outfile)

    app(i2cbus, i2caddr, token_str, ch_name, interval, outfile,
        debug=debug).main()
            
if __name__ == '__main__':
    main()
