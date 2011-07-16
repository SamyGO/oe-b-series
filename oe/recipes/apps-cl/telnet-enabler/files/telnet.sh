#!/bin/sh

cd $1

mount -t devpts devpts /dev/pts

./busybox telnetd

