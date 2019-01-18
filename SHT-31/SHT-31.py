#!/usr/bin/env python3
#
# (C) 2018 Yoichi Tanibayashi
#
import smbus
import time

import click

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, WARN
logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = StreamHandler()
handler.setLevel(DEBUG)
handler_fmt = Formatter('%(asctime)s %(levelname)s %(name)s:%(funcName)s> %(message)s',
                        datefmt='%H:%M:%S')
handler.setFormatter(handler_fmt)
logger.addHandler(handler)
logger.propagate = False

#####
class SHT31:
    '''SHT31

    Simple usage:

    obj = SHT31()
    if obj.measure():
       print('%.2f C'  % obj.temp)
       print('%.2f %%' % obj.humidity)
    '''
    def __init__(self, i2c_bus=1, addr=0x45):
        self.logger = logger.getChild(__class__.__name__)
        self.logger.debug('i2c_bus=%d, addr=0x%02X', i2c_bus, addr)
        
        self.i2c_bus = 1
        self.addr    = addr

    def measure(self):
        self.logger.debug('')
        
        try:
            i2c = smbus.SMBus(self.i2c_bus)
            i2c.write_byte_data(self.addr, 0x24, 0x00)	# 単発測定
            time.sleep(0.02)				# >= 0.012 (12ms)
            data = i2c.read_i2c_block_data(self.addr, 0x00, 6)
            i2c.close()
        except Exception as e:
            self.logger.error('%s:%s', type(e), e)
            return False

        self.temp     = self.calc_temp(data[0], data[1])
        self.humidity = self.calc_humidity(data[3], data[4])
        return True

    def calc_temp(self, data1, data2):
        self.logger.debug('0x%02X, 0x%02X', data1, data2)
        val = (data1 << 8) | data2
        temp = -45 + 175 * val / 65535
        self.logger.debug('val = 0x%04X = %d, temp=%f', val, val, temp)
        return round(temp, 1)

    def calc_humidity(self, data1, data2):
        self.logger.debug('0x%02X, 0x%02X', data1, data2)
        val = (data1 << 8) | data2
        humidity = 100 * val / 65535
        self.logger.debug('0x%04X = %d, humidity=%f', val, val, humidity)
        return round(humidity, 1)
    
#####
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--bus', '-b', 'bus', type=int, default=1,
              help='I2C bus number')
@click.option('--addr', '-a', 'addr', type=str, default='0x45',
              help='I2C address in hex (ex. \'0x45\')')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(bus, addr, debug):
    logger.setLevel(INFO)
    if debug:
        logger.setLevel(DEBUG)

    logger.debug('bus=%d, addr=%s', bus, addr)

    if addr[:2] != '0x':
        logger.error('%s is not a valid hex value', addr)
        return
    addr_val = int(addr[2:], 16)
    logger.debug('addr_val=0x%02X', addr_val)
    
    obj = SHT31(bus, addr_val)
    if obj.measure():
        print('%.1f C, %.1f %%' % (obj.temp, obj.humidity))
    else:
        logger.error('Error(%d:%02X)', bus, addr_val)

if __name__ == '__main__':
    main()
