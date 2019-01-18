#!/bin/sh

MYNAME=`basename $0`

if [ "$1" = "" ]; then
	echo
	echo "usage: ${MYNAME} outfile"
	echo
	exit 1
fi

OUTFILE=$1

if [ -s ${OUTFILE} ]; then
	cp -vf ${OUTFILE} ${OUTFILE}.old
	echo -n > ${OUTFILE}
fi
