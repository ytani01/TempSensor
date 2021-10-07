#!/usr/bin/env python3
#
# (c) 2020,2021 Yoichi Tanibayashi
#
__authoer__ = 'Yoichi Tanibayashi'
__data__    = '2021/08'
__version__ = '0.1.0'

from Mqtt import BeebottePublisher, BeebotteSubscriber
from BME280I2C import BME280I2C
import time
from MyLogger import get_logger
import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class App:
    def __init__(self, i2c_addr=0x76, channel='', token='',
                 interval=2, count=20, ave_n=5, diff_t=0.05, diff_h=1.0,
                 offset_t=0.0, offset_h=0.0, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('i2c_addr=%s', i2c_addr)
        self._log.debug('channel=%s, token=%s', channel, token)
        self._log.debug('interval=%s, ave_n=%s, count=%s',
                        interval, count, ave_n)
        self._log.debug('diff_t=%s, diff_h=%s', diff_t, diff_h)
        self._log.debug('offset_t=%s, offset_h=%s', offset_t, offset_h)

        self._i2c_addr = i2c_addr
        self._channel = channel
        self._token = token
        self._interval = interval
        self._count = count
        self._ave_n = ave_n
        self._diff_t = diff_t
        self._diff_h = diff_h
        self._offset_t = offset_t
        self._offset_h = offset_h

        self._bme280 = BME280I2C(self._i2c_addr)

        self._topic_t = channel + '/temperature'
        self._topic_h = channel + '/humidity'
        self._topic_mon = channel + '/data1'

        self._bbt_pub = BeebottePublisher(self._token, debug=self._dbg)
        self._bbt_mon = BeebotteSubscriber(self.monitor, [ self._topic_mon ],
                                           self._token, debug=self._dbg)

        self._t_hist = []
        self._h_hist = []

        self._reported_t = -100
        self._reported_h = -100
        self._i = 0

        self.up_down = 0

    def main(self):
        """
        """
        self._log.debug('')

        self._bbt_mon.start()
        time.sleep(1)
        self._bbt_pub.start()

        t = 0
        prev_t = 0
        updown_t = 0
        prev_updown_t = 0
        while self._bme280.meas():
            t0 = self._bme280.T + self._offset_t
            h0 = self._bme280.H + self._offset_h

            self._t_hist.append(t0)
            while len(self._t_hist) > self._ave_n:
                self._t_hist.pop(0)
            self._log.debug('t_hist=%s', self._t_hist)

            self._h_hist.append(h0)
            while len(self._h_hist) > self._ave_n:
                self._h_hist.pop(0)
            self._log.debug('h_hist=%s', self._h_hist)

            prev_t = t
            t = self.ave(self._t_hist)
            h = self.ave(self._h_hist)

            if t != prev_t:
                prev_updown_t = updown_t
                updown_t = (t - prev_t) / abs(t-prev_t)
                self._log.debug('updown_t=%d, prev_updown_t=%d',
                                updown_t, prev_updown_t)

            mon_data = '%.2f C   %.1f %%' % (t, h)

            self._i += 1
            self._log.info('[%2d/%2d] %.3f C (%+d) : %.3f C , %.1f %% : %.1f %%',
                           self._i, self._count,
                           t, updown_t, self._reported_t,
                           h, self._reported_h)
            if self._i >= self._count or \
               abs(t - self._reported_t) >= self._diff_t or \
               abs(h - self._reported_h) >= self._diff_h or \
               updown_t * prev_updown_t < 0:

                # if ("%.2f" % t) != ("%.2f" % self._reported_t):
                    self._bbt_pub.send_data(t, [ self._topic_t])
                    self._bbt_pub.send_data(h, [ self._topic_h])
                    self._bbt_mon.send_data(mon_data, [ self._topic_mon])

                    self._reported_t = t
                    self._reported_h = h
                    self._log.debug('reported_t=%s, reported_h=%s',
                                    self._reported_t, self._reported_h)

                    self._i = 0

            time.sleep(self._interval)

    def end(self):
        self._log.debug('')

    def monitor(self, data, topic, ts):
        mon_data = self._bbt_mon.ts2datestr(ts)
        self._log.info('%s[%s]   %s', mon_data, topic, data)

    def ave(self, list):
        return sum(list) / len(list)


@click.command(context_settings=CONTEXT_SETTINGS, help='''
BME280 ==>[MQTT]==> Beebotte
''')
@click.argument('i2c_addr', type=str)
@click.argument('channel', type=str)
@click.argument('token', type=str)
@click.option('--interval', '-i', 'interval', type=int, default=5,
              help='interval sec')
@click.option('--count', '-c', 'count', type=int, default=20,
              help='count')
@click.option('--ave_n', '-n', 'ave_n', type=int, default=5,
              help='average n')
@click.option('--diff_t', '-dt', 'diff_t', type=float, default=0.1,
              help='difference .. temperature')
@click.option('--diff_h', '-dh', 'diff_h', type=float, default=1.0,
              help='difference .. humidity')
@click.option('--offset_t', '-ot', 'offset_t', type=float, default=0.0,
              help='temperature offset')
@click.option('--offset_h', '-oh', 'offset_h', type=float, default=0.0,
              help='humidity offset')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug options')
def main(i2c_addr, channel, token, interval, count, ave_n, diff_t, diff_h,
         offset_t, offset_h, debug):
    log = get_logger(__name__, debug=debug)
    log.debug('i2c_addr=%s', i2c_addr)
    log.debug('channel=%s, token=%s', channel, token)
    log.debug('interval=%s, count=%s, ave_n=%s', interval, count, ave_n)
    log.debug('diff_t=%s, diff_h=%s', diff_t, diff_h)
    log.debug('offset_t=%s, offset_h=%s', offset_t, offset_h)

    app = App(int(i2c_addr, 16), channel, token, interval, count, ave_n,
              diff_t, diff_h, offset_t, offset_h, debug=debug)
    try:
        app.main()
    finally:
        app.end()
        log.info('done')


if __name__ == '__main__':
    main()
