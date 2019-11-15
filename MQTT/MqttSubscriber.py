#!/usr/bin/env python3
#
# (C) 2019 Yoichi Tanibayashi
#
import paho.mqtt.client as mqtt
import threading
import queue
import json
import time

from MyLogger import get_logger


class MqttSubscriber(threading.Thread):
    """
    msg := {'type': msg_type, 'data': msg_data}
    """
    DEF_PORT = 1883
    DEF_QOS = 2

    MSG_OK = 'OK'
    MSG_ERR = 'Error'
    MSG_DATA = 'Data'
    MSG_CONNECT = 'Connect'
    MSG_DISCONNECT = 'Disconnect'

    def __init__(self, host, port, user, pw, topic, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('host=%s, port=%d, user=%s, pw=%s, topic=%s',
                          host, port, user, pw, topic)

        self.svr_host = host

        if port == 0:
            self.svr_port = self.DEF_PORT
        else:
            self.svr_port = port

        self.user = user
        self.password = pw

        self.topic = topic
        self.user = user
        self.password = pw

        self.msgq = queue.Queue()

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.enable_logger()
        self.mqtt_client.on_log = self.on_log
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message

        self.connection = False

        super().__init__()
        self.daemon = True

    def run(self):
        self.logger.debug('')

        self.mqtt_client.username_pw_set(self.user, password=self.password)
            
        try:
            self.mqtt_client.connect(self.svr_host, self.svr_port,
                                     keepalive=60)
        except Exception as e:
            msg_data = 'connect(): %s:%s' % (type(e), e)
            self.logger.error(msg_data)
            self.put(self.MSG_ERR, msg_data)
            return

        try:
            self.mqtt_client.loop_forever()
        except Exception as e:
            msg_data = 'loop_forever(): %s:%s' % (type(e), e)
            self.logger.error(msg_data)
            self.put(self.MSG_ERR, msg_data)

    def end(self):
        self.logger.debug('')

    def put(self, msg_type, msg_data):
        self.logger.debug('msg_type=%s, msg_data=%s', msg_type, msg_data)

        self.msgq.put({'type': msg_type, 'data': msg_data})

    def get(self, timeout=None):
        self.logger.debug('timeout=%s', timeout)

        try:
            msg = self.msgq.get(timeout=timeout)
            self.logger.debug('msg=%s', msg)
            msg_type = msg['type']
            msg_data = msg['data']
        except queue.Empty:
            self.logger.warning('timeout')
            msg_type = self.MSG_ERR
            msg_data = 'get():timeout'
        except Exception as e:
            msg_type = self.MSG_ERR
            msg_data = type(e) + ':' + str(e)

        return (msg_type, msg_data)

    def on_connect(self, client, userdata, flag, rc):
        self.logger.debug('userdata=%s, flag=%s, rc=%s', userdata, flag, rc)

        if rc != 0:
            self.put(self.MSG_ERR, 'on_connect():rc=' + str(rc))
            return

        for t in self.topic:
            self.logger.debug('t=%s', t)
            client.subscribe(t, qos=self.DEF_QOS)

        self.connection = True
        self.put(self.MSG_CONNECT, 'connected(' + str(rc) + ')')

    def on_disconnect(self, client, userdata, rc):
        self.logger.debug('userdata=%s, rc=%s', userdata, rc)

        self.connection = False
        self.put(self.MSG_DISCONNECT, 'disconnected(' + str(rc) + ')')

    def on_message(self, client, userdata, msg):
        self.logger.debug('userdata=%s', userdata)

        # topic
        topic = msg.topic
        self.logger.debug('topic=%s', topic)

        (channel, resource) = topic.split('/')
        self.logger.debug('channel=%s, resouce=%s', channel, resource)

        # payload
        payload_raw = msg.payload
        self.logger.debug('payload_raw=%s', payload_raw)

        payload = json.loads(payload_raw.decode('utf-8'))
        self.logger.debug('payload=%s', payload)

        # time stamp and value
        ts = int(payload['ts'])
        self.logger.debug('ts=%d', ts)

        val = float(payload['data'])
        self.logger.debug('val=%.2f', val)

        msg_data = {'ts': ts, 'topic': topic, 'value': val}
        self.put(self.MSG_DATA, msg_data)

    def on_log(self, client, userdata, level, buf):
        self.logger.debug('userdata=%s, level=%d, buf=%s',
                          userdata, level, buf)

        if level <= mqtt.MQTT_LOG_WARNING:
            msg_data = 'level=%d, buf=%s' % (level, buf)
            self.logger.warning(msg_data)
            self.put(self.MSG_ERR, msg_data)

    def wait_connect(self, timeout=10):
        self.logger.debug('timeout=%s', timeout)

        msg_type, msg_data = self.get(timeout=timeout)
        self.logger.debug('msg_type=%s, msg_data=%s', msg_type, msg_data)

        if msg_type != self.MSG_CONNECT:
            self.logger.error('Failed:%s,%s' % (msg_type, msg_data))

        return (msg_type, msg_data)

    def ts2datestr(self, ts_msec):
        self.logger.debug('ts_msec=%d', ts_msec)

        datestr = time.strftime('%Y/%m/%d,%H:%M:%S',
                                time.localtime(ts_msec/1000))
        return datestr


class App:
    def __init__(self, host, port, topic, user, pw, debug=False):
        self.debug = debug
        self.logger = get_logger(__class__.__name__, self.debug)
        self.logger.debug('host=%s, port=%d', host, port)
        self.logger.debug('topic=%s', topic)
        self.logger.debug('user=%s, pw=%s', user, pw)

        self.subscriber = MqttSubscriber(host, port, topic, user, pw,
                                         debug=self.debug)

    def main(self):
        self.logger.debug('')

        self.subscriber.start()

        # wait connection
        msg_type, msg_data = self.subscriber.wait_connect(timeout=5)
        self.logger.debug('msg_type=%s, msg_data=%s', msg_type, msg_data)
        if msg_type != self.subscriber.MSG_CONNECT:
            print('Connect failed:%s:%s' % (msg_type, msg_data))
            return

        # wait data
        while True:
            msg_type, msg_data = self.subscriber.get()
            self.logger.debug('msg_type=%s, msg_data=%s',
                              msg_type, msg_data)

            if msg_type == self.subscriber.MSG_DATA:
                datestr = self.subscriber.ts2datestr(msg_data['ts'])
                print('%s %s %s' % (datestr,
                                    msg_data['topic'],
                                    msg_data['value']))
                continue

            if msg_type == self.subscriber.MSG_CONNECT:
                print(msg_type, msg_data)
                continue

            if msg_type == self.subscriber.MSG_DISCONNECT:
                print(msg_type, msg_data)
                continue

            print('!?')
            break

    def end(self):
        self.logger.debug('')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS,
               help='''
MQTT subscriber
''')
@click.argument('server_host')
@click.argument('user_name')
@click.argument('topic', nargs=-1)
@click.option('--password', '--pw', 'password', default='',
              help='password')
@click.option('--server_port', '--port', '-p', 'server_port', type=int,
              default=MqttSubscriber.DEF_PORT,
              help='server port')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(server_host, server_port, user_name, password, topic, debug):
    logger = get_logger(__name__, debug=debug)

    app = App(server_host, server_port, user_name, password, topic,
              debug=debug)
    try:
        app.main()
    finally:
        logger.info('finally')
        app.end()


if __name__ == '__main__':
    main()
