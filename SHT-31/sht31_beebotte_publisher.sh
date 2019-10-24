#!/bin/sh
#
# (C) 2019 Yoichi Tanibayashi
#
MYNAME=`basename $0`

TOKEN=token_QDg59iYFLCUqeZLc
CHNAME=env1
PUBLISHER="${HOME}/bin/sht31_beebotte_publisher.py"
ENV_OUT=${HOME}/tmp/env.txt

COUNT=0
while true; do
    COUNT=`expr ${COUNT} + 1`
    echo "start:${COUNT} ..."
    ${PUBLISHER} ${TOKEN} ${CHNAME} -o ${ENV_OUT}
    sleep 5
done
