#!/bin/sh
#
# (C) 2019 Yoichi Tanibayashi
#
MYNAME=`basename $0`

TOKEN=token_QDg59iYFLCUqeZLc
CHNAME=env1
PUBLISHER=sht31_beebotte_publisher.py
ENV_OUT=${HOME}/tmp/env.txt

exec ${PUBLISHER} ${TOKEN} ${CHNAME} -o ${ENV_OUT}
