#!/usr/bin/env python3
#
# (C) 2018 Yoichi Tanibayashi
#
from SHT31 import SHT31
from OledClient import OledClient

import time

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
class SHT31_OLED:
    def __init__(self, bus, addr_str, server, port, oled_part, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('bus=%d, addr_str=\'%s\'', bus, addr_str)

        if addr_str[:2] != '0x':
            self.logger.error('%s is not a valid hex value', addr_str)
            return
        
        addr = int(addr_str[2:], 16)
        self.logger.debug('addr=0x%02X', addr)

        self.sensor    = SHT31(bus, addr, debug=self.debug)
        self.server    = server
        self.port      = port
        self.oled_part = oled_part


    def out_oled(self):
        if self.sensor.measure():
            out_str = '%.1f C, %.1f %%' % (self.sensor.temp,
                                           self.sensor.humidity)
            self.logger.debug('%s', out_str)

            with OledClient(self.server, self.port, debug=self.debug) as oc:
                oc.part(self.oled_part)
                oc.zenkaku(True)
                oc.crlf(True)
                oc.send(out_str)
        else:
            self.logger.error('Error:(%d:%02X)', bus, addr_val)

    def loop(self):
        while True:
            self.out_oled()
            time.sleep(5)
            
#####
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--bus', '-b', 'bus', type=int, default=1,
              help='I2C bus number')
@click.option('--addr', '-a', 'addr', type=str, default='0x45',
              help='I2C address in hex (ex. \'0x45\')')
@click.option('--server', '-s', 'server', type=str, default='localhost',
              help='OLED server host name or IP address')
@click.option('--port', '-p', 'port', type=int, default=12345,
              help='OLED server port numbe')
@click.option('--oled_part', '-o', 'oled_part', type=str, default='body',
              help='OLED part')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(bus, addr, server, port, oled_part, debug):
    if debug:
        logger.setLevel(DEBUG)

    SHT31_OLED(bus, addr, server, port, oled_part, debug=debug).loop()

if __name__ == '__main__':
    main()
