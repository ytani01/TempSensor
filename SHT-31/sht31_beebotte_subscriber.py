#!/usr/bin/env python3
#
# (C) 2019 Yoichi Tanibayashi
#
import paho.mqtt.client as mqtt
import time
import json

from MyLogger import get_logger

DEF_HOSTNAME = 'mqtt.beebotte.com'
DEF_PORT = 1883
DEF_CHANNEL = 'env1'
DEF_RESOURCES = ['temp', 'humidity']
DEF_TOKEN = 'token_QDg59iYFLCUqeZLc'


class App:
    def __init__(self, host, port, channel, res, token, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('host=%s, port=%d, channel=%s, token=%s',
                          host, port , channel, token)

        self.svr_host = host
        self.svr_port = port
        self.channel = channel
        self.resource = res
        self.token = 'token:' + token
        self.logger.debug('token=%s', self.token)

        self.client = mqtt.Client()
        self.client.enable_logger()
        self.client.on_log = self.on_log

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def main(self):
        self.logger.debug('')

        self.client.username_pw_set(self.token)
        self.client.connect(self.svr_host, self.svr_port, 60)
        self.logger.debug('connected')

        self.client.loop_forever()

    def end(self):
        self.logger.debug('')

    def on_connect(self, client, userdata, flag, rc):
        self.logger.debug('userdata=%s, flag=%s, rc=%s', userdata, flag, rc)

        for res in self.resource:
            topic = self.channel + '/' + res
            self.logger.debug('topic=%s', topic)
            client.subscribe(topic)

    def on_disconnect(self, client, userdata, flag, rc):
        self.logger.debug('userdata=%s, flag=%s, rc=%s', userdata, flag, rc)

    def on_message(self, client, userdata, msg):
        self.logger.debug('userdata=%s, msg=%s', userdata, msg)

        topic = msg.topic
        self.logger.debug('topic=%s', topic)

        payload = json.loads(msg.payload.decode('utf-8'))
        self.logger.debug('payload=%s', payload)

        resource = topic.replace(self.channel + '/', '')
        self.logger.debug('resouce=%s', resource)

        ts = int(payload['ts'])
        self.logger.debug('ts=%d', ts)

        val = float(payload['data'])
        self.logger.debug('val=%.2f', val)

        date_str = time.strftime('%Y/%m/%d(%a),%H:%M:%S',
                                 time.localtime(round(ts/1000)))

        print('%s %s %.2f' % (date_str, resource, val))

    def on_log(self, client, userdata, level, buf):
        self.logger.debug('userdata=%s, level=%s, buf=%s',
                          userdata, level, buf)

        if level >= self.client.MQTT_LOG_WARNING:
            self.logger.warn('level=%d, buf=%s', level, buf)


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS,
               help='SHT-31 MQTT subscriber (temp, humidity)')
@click.argument('channel_name', default=DEF_CHANNEL)
@click.argument('token_str', default=DEF_TOKEN)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(channel_name, token_str, debug):
    logger = get_logger(__name__, debug=debug)
    logger.debug('token_str=%s', token_str)

    res = DEF_RESOURCES
    app = App(DEF_HOSTNAME, DEF_PORT,
              channel_name, res, token_str,
              debug=debug)
    try:
        app.main()
    finally:
        logger.info('finally')
        app.end()


if __name__ == '__main__':
    main()
