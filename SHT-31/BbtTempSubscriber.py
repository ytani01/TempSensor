#!/usr/bin/env python3
#
# (C) 2019 Yoichi Tanibayashi
#
from BeebotteSubscriber import BeebotteSubscriber
import time

from MyLogger import get_logger


class BbtTempSubscriber:
    DEF_TOPIC = 'env1/temp'

    def __init__(self, token, topic, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('token=%s, topic=%s', token, topic)

        self.token = token
        self.topic = topic

        self.subscriber = BeebotteSubscriber(token, (topic,), debug=self.debug)

    def start(self):
        self.logger.debug('')
        self.subscriber.start()

        msg_type, msg_data = self.subscriber.wait_connect(timeout=3)
        if msg_type == self.subscriber.MSG_CONNECT:
            self.logger.debug('connected')
            return True
        else:
            self.logger.error('[%s]%s', msg_type, msg_data)
            return False

    def get_temp(self, timeout=None):
        self.logger.debug('')

        msg_type, msg_data = self.subscriber.get(timeout=timeout)
        self.logger.debug('msg_type=%s, msg_data=%s', msg_type, msg_data)

        if msg_type == BeebotteSubscriber.MSG_DATA:
            ts_msec = msg_data['ts']
            topic = msg_data['topic']
            temp = msg_data['value']

            if topic != self.topic:
                self.logger.warning('topic=%s ??', topic)
                return (0, 0)

            return (ts_msec, temp)
        else:
            return (0, 0)

    def end(self):
        self.logger.debug('')

    def ts2datestr(self, ts_msec):
        self.logger.debug('ts_msec=%d', ts_msec)

        return self.subscriber.ts2datestr(ts_msec)

class App:
    OLD_SEC = 3600
    TIMEOUT_SEC = 60

    def __init__(self, token, topic, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('token=%s, topic=%s', token, topic)

        self.subscriber = BbtTempSubscriber(token, topic, debug=self.debug)

    def main(self):
        self.logger.debug('')

        if not self.subscriber.start():
            print('start():failed')
            return

        while True:
            ts_msec, temp = self.subscriber.get_temp(timeout=self.TIMEOUT_SEC)
            self.logger.debug('ts_msec=%d, temp=%f', ts_msec, temp)
            if ts_msec == 0:
                self.logger.warning('ignored')
                continue
            
            date_str = self.subscriber.ts2datestr(ts_msec)

            ts_sec = ts_msec / 1000
            ts_now = time.time()
            if ts_now - ts_sec > self.OLD_SEC:
                print('[old]', end='')

            print('%s %.2f' % (date_str, temp))

    def end(self):
        self.logger.debug('')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS,
               help='''
Beebotte MQTT subscriber (temperature only)

TOPIC := \'channel/resouce\' (default: \'env1/temp\')

TOKEN_STR := \'token_xxxx\'
''')
@click.argument('token_str', default='')
@click.argument('topic', default=BbtTempSubscriber.DEF_TOPIC)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(token_str, topic, debug):
    logger = get_logger(__name__, debug=debug)
    logger.debug('token_str=%s, topic=%s', token_str, topic)

    app = App(token_str, topic, debug=debug)
    try:
        app.main()
    finally:
        logger.info('finally')
        app.end()


if __name__ == '__main__':
    main()
