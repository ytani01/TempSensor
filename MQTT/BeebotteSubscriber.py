#!/usr/bin/env python3
#
# (C) 2019 Yoichi Tanibayashi
#
from MqttSubscriber import MqttSubscriber

from MyLogger import get_logger


class BeebotteSubscriber(MqttSubscriber):
    HOSTNAME = 'mqtt.beebotte.com'
    PORT = 1883

    def __init__(self, token, topic, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('token=%s, topic=%s', token, topic)

        self.token = 'token:' + token
        self.logger.debug('token=%s', self.token)

        self.topic = topic

        super().__init__(self.HOSTNAME, self.PORT, self.token, '', topic,
                         debug=self.debug)


class App:
    def __init__(self, token, topic, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('topic=%s, token=%s', topic, token)

        self.subscriber = BeebotteSubscriber(token, topic,
                                             debug=self.debug)

    def main(self):
        self.logger.debug('')

        self.subscriber.start()
        
        """
        msg_type, msg_data = self.subscriber.wait_connect(timeout=3)
        if msg_type != self.subscriber.MSG_CONNECT:
            print('Connect failed:%s:%s' % (msg_type, msg_data))
            return
        """
        
        while True:
            msg_type, msg_data = self.subscriber.get()

            if msg_type == self.subscriber.MSG_DATA:
                datestr = self.subscriber.ts2datestr(msg_data['ts'])
                print('%s %s %s' % (datestr,
                                    msg_data['topic'], msg_data['value']))
            else:
                print('[%s]%s' % (msg_type, msg_data))

    def end(self):
        self.logger.debug('')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS,
               help='''
Beebotte MQTT subscriber

TOKEN_STR := \'token_xxxx\'

TOPIC := \'channel/resouce\' (default: \'env1/temp\')
''')
@click.argument('token_str')
@click.argument('topic', nargs=-1)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(token_str, topic, debug):
    logger = get_logger(__name__, debug=debug)
    logger.debug('token_str=%s, topic_str=%s', token_str, topic)

    app = App(token_str, topic, debug=debug)
    try:
        app.main()
    finally:
        logger.info('finally')
        app.end()


if __name__ == '__main__':
    main()
