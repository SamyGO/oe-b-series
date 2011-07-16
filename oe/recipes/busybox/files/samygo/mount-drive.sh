#!/bin/sh

if [ `cat /proc/cmdline | grep -c root=/dev/$MDEV` != 0 ]; then
	exit 0
fi
DEV=`echo $MDEV | cut -c 1-3 -`
if [ ! -f /sys/block/$DEV/device/model ]; then
	exit 0
fi
MODEL=`cat /sys/block/$DEV/device/model`
SERIAL=`cat /sys/block/$DEV/device/serial`
VENDOR=`cat /sys/block/$DEV/device/vendor`
DEVPATH=`cat /sys/block/$DEV/device/usbdevpath`
LUN=`cat /sys/block/$DEV/device/logicalnumber`

case "$ACTION" in
	add | "")
		/bin/mkdir /dtv/usb/$MDEV
		/bin/mount -o sync -t auto /dev/$MDEV /dtv/usb/$MDEV
		if [ $? != 0 ]; then
			/bin/rmdir /dtv/usb/$MDEV
			exit 0
		fi
		echo "[$MDEV]
Vendor : $VENDOR
Product : $MODEL
Serial : $SERIAL
Devpath : $DEVPATH
Lun : $LUN
MountDir : /dtv/usb/$MDEV
FileSystem : vfat" > /dtv/usb/log
		;;
	remove)
		echo "[$MDEV]
Vendor : $VENDOR
Product : $MODEL
Serial : $SERIAL
Devpath : $DEVPATH
Lun : $LUN
" > /dtv/usb/log
		/bin/umount -lf /dev/$MDEV
		/bin/rmdir /dtv/usb/$MDEV
		;;
esac
