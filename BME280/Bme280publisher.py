#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
__authoer__ = 'Yoichi Tanibayashi'
__data__    = '2020'

from MqttClientServer import BeebottePublisher, BeebotteSubscriber
from BME280I2C import BME280I2C
import time
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class App:
    def __init__(self, i2c_addr=0x76, channel='', token='', debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('i2c_addr=%s', i2c_addr)
        self._log.debug('channel=%s, token=%s', channel, token)

        self._bme280 = BME280I2C(i2c_addr)
        self._bbt= BeebottePublisher(channel + '/data1',
                                     token, debug=self._dbg)
        self._bbt_mon = BeebotteSubscriber(self.monitor, [channel + '/data1'],
                                           token, debug=self._dbg)

        self._t_hist = []
        self._h_hist = []

    def main(self):
        self._log.debug('')

        self._bbt.start()
        self._bbt_mon.start()
        
        while self._bme280.meas():
            t0 = self._bme280.T
            h0 = self._bme280.H

            self._t_hist.append(t0)
            if len(self._t_hist) > 5:
                self._t_hist.pop(0)
            print('t_hist=%s' % (self._t_hist))
            

            if len(self._h_hist) > 5:
                self._h_hist.pop(0)
            self._h_hist.append(h0)
            print('h_hist=%s' % (self._h_hist))

            t = self.ave(self._t_hist)
            h = self.ave(self._h_hist)
            
            msg = '%.2f C   %.1f %%' % (t, h)
            self._log.debug('msg=%s', msg)

            self._bbt.send_data(t, 'env2/temperature')
            self._bbt.send_data(h, 'env2/humidity')
            self._bbt.send_data(msg, 'env2/data1')

            time.sleep(5)

    def end(self):
        self._log.debug('')

    def monitor(self, data, ts):
        print('%s   %s' % (self._bbt_mon.ts2datestr(ts), data))

    def ave(self, list):
        return sum(list) / len(list)

@click.command(context_settings=CONTEXT_SETTINGS, help='''
BME280 ==>[MQTT]==> Beebotte
''')
@click.argument('i2c_addr', type=str)
@click.argument('channel', type=str)
@click.argument('token', type=str)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug options')
def main(i2c_addr, channel, token, debug):
    log = get_logger(__name__, debug=debug)
    log.debug('i2c_addr=%s', i2c_addr)
    log.debug('channel=%s, token=%s', channel, token)

    app = App(int(i2c_addr, 16), channel, token, debug=debug)
    try:
        app.main()
    finally:
        app.end()
        log.info('done')
        

if __name__ == '__main__':
    main()
        
