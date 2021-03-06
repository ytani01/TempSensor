#!/usr/bin/env python3
#
# (C) 2018 Yoichi Tanibayashi
#
"""
"""
import smbus
import time
from MyLogger import get_logger


#####
SHT31_ADDR = 0x45


#####
class SHT31:
    '''
    SHT31

    Simple usage:

    obj = SHT31()
    if obj.measure():
       print('%.2f C'  % obj.temp)
       print('%.2f %%' % obj.humidity)

    # or
    obj = SHT31()
    print('%.2f C'  % obj.get_temp(measure=True)
    print('%.2f %%' % obj.get_humidity(measure=False)

    '''
    def __init__(self, i2c_bus=1, addr=SHT31_ADDR, debug=False):
        self.logger = get_logger(__class__.__name__, debug)
        self.logger.debug('i2c_bus=%d, addr=0x%02X', i2c_bus, addr)

        self.i2c_bus = i2c_bus
        self.addr    = addr

    def get_temp(self, measure=False):
        self.logger.debug('measure=%s', measure)

        if measure:
            if not self.measure():
                self.logger.warn('measure(): failed')
                return None

        return self.temp

    def get_humidity(self, measure=False):
        self.logger.debug('measure=%s', measure)

        if measure:
            if not self.measure():
                self.logger.warn('measure(): failed')
                return None

        return self.humidity

    def measure(self):
        self.logger.debug('')

        try:
            i2c = smbus.SMBus(self.i2c_bus)
            i2c.write_byte_data(self.addr, 0x24, 0x00)  # 単発測定
            time.sleep(0.03)				# >= 0.012 (12ms)
            data = i2c.read_i2c_block_data(self.addr, 0x00, 6)
            i2c.close()
        except Exception as e:
            self.logger.error('%s:%s', type(e), e)
            return False

        self.temp     = self.calc_temp(data[0], data[1])
        self.humidity = self.calc_humidity(data[3], data[4])
        return True

    def calc_temp(self, data1, data2):
        self.logger.debug('data1=0x%02X, data2=0x%02X', data1, data2)
        val = (data1 << 8) | data2
        temp = -45 + 175 * val / 65535
        self.logger.debug('val=0x%04X=%d, temp=%f', val, val, temp)
        return round(temp, 2)

    def calc_humidity(self, data1, data2):
        self.logger.debug('data1=0x%02X, data2=0x%02X', data1, data2)
        val = (data1 << 8) | data2
        humidity = 100 * val / 65535
        self.logger.debug('val=0x%04X=%d, humidity=%f', val, val, humidity)
        return round(humidity, 1)


#####
class App:
    def __init__(self, bus, addr_str, debug=False):
        self.logger = get_logger(__class__.__name__, debug)
        self.logger.debug('bus=%d, addr_str=\'%s\'', bus, addr_str)

        self.bus = bus

        if addr_str[:2] != '0x':
            self.logger.error('%s is not a valid hex value', addr_str)
            return

        self.addr = int(addr_str[2:], 16)
        self.logger.debug('addr=0x%02X', self.addr)

        self.obj = SHT31(self.bus, self.addr, debug=debug)

    def main(self):
        if self.obj.measure():
            print('%.1f C, %.1f %%' % (self.obj.temp, self.obj.humidity))
        else:
            self.logger.error('Error:(%d:%02X)', self.bus, self.addr)


#####
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--bus', '-b', 'bus', type=int, default=1,
              help='I2C bus number')
@click.option('--addr', '-a', 'addr', type=str, default='0x45',
              help='I2C address in hex (ex. \'0x45\')')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(bus, addr, debug):
    logger = get_logger(__name__, debug)
    logger.debug('bus=%d, addr=%s', bus, addr)

    App(bus, addr, debug=debug).main()


if __name__ == '__main__':
    main()
