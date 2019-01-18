# BME280 温度・湿度・気圧センサー

I2C

## 1 bbt_python library

### 1.1 インストール

```bash
$ sudo pip3 install -U beebotte
```

### 1.2 Usage

https:/https://github.com/beebotte/bbt_python


# DEPRECATED?
## 1. 準備

### 1.1 Beebotte の証明書のダウンロード

https://beebotte.com/certs/mqtt.beebotte.com.pem

### 1.2 Beebotte のトークン取得

Channel Tokenの文字列をコピー

### 1.3 ライブラリのインストール

```bash
$ sudo pip3 install -U paho-mqtt
```

## 2 Publish

```
#!/usr/bin/env python3

import paho.mqtt.client as mqtt

HOSTNAME = "mqtt.beebotte.com"
PORT = 8883
TOPIC = "channel/resource"
TOKEN = "token_..."
CACERT = "mqtt.bebotte.com.pem"

client = mqtt.Client(protocol=mqtt.MQTTv311)

client.username_pw_set('token:%s' % TOKEN)
client.tls_set(CACERT)

client.connect(HOST, port=PORT, keepalive=60)
client.publish(topic, data)
client.disconnect()
```

## 3. Subscribe

```
#!/usr/bin/env python3

import paho.mqtt.client as mqtt

HOSTNAME = "mqtt.beebotte.com"
PORT = 8883
TOPIC = "channel/resource"
TOKEN = "token_..."
CACERT = "mqtt.bebotte.com.pem"
def on_connect(client, userdata, flags, response_code):
    client.subscribe(topic)

def on_message(client, userdata, msg):
    print(msg.topc + ' ' + str(msg.pyload, 'utf-8))

if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set('token:%s' % TOKEN)
    client.tls_set(CACERT)

    client.connect(HOST, port=PORT, keepalive=60)
    client.loop_forever()
```

