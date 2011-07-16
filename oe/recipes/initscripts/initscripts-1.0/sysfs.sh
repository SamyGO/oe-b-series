#!/bin/sh

if [ -e /proc ] && ! [ -e /proc/mounts ]; then
  mount -t proc proc /proc
fi

if [ -e /sys ] && ! [ -e /sys/kernel ] && grep -q sysfs /proc/filesystems; then
  mount sysfs /sys -t sysfs
fi

exit 0
