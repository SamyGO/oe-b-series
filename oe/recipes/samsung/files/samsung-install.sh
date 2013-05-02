#!/bin/sh

# - SamyGO -
#
# Copyright (C) 2010-2013 Pawel Kolodziejski (aquadran at users.sourceforge.net)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


echo
echo " --- Installer of Original Samsung Software ---"
echo " --- SamyGO http://www.samygo.tv ---"
echo

while true; do
	echo
	echo "Select proper firmware for your TV:"
	echo
	echo "1. T-CHL7DEUC"
	echo "2. T-CHEAUSC"
	echo "3. T-CHL7DAUC"
	echo

	read -p "Choice: " sel

	if [ $sel -ge "1" ] && [ $sel -le "3" ]; then
		break
	else
		echo "Wrong choice !"
	fi
done

case $sel in
1)	URL="http://downloadcenter.samsung.com/content/FM/200910/20091030222802906/T-CHL7DEUC.exe" # 2005.0
	FILENAME="T-CHL7DEUC.exe"
	MD5SUM="2cdfe576c619c9ebf6698b22e9965127"
	TYPE="T-CHL7DEUC"
	UNCOMP="unrar x -c- "
	;;
2)	URL="http://downloadcenter.samsung.com/content/FM/200909/20090922132250765/2009_DTV_1G_firmware.exe" # 1012.3
	FILENAME="2009_DTV_1G_firmware.exe"
	MD5SUM="4d6618255c5528b18dd4ef3d49e9aa51"
	TYPE="T-CHEAUSC"
	UNCOMP="unzip -qq "
	;;
3)	URL="http://downloadcenter.samsung.com/content/FM/200911/20091127101733312/T-CHL7DAUC.exe" # 2001.1
	FILENAME="T-CHL7DAUC.exe"
	MD5SUM="e2412b2771556c3a77e9601275d283ab"
	TYPE="T-CHL7DAUC"
	UNCOMP="unzip -qq "
	;;
*)
	echo "Unknown firmware type!"
	echo "Exiting..."
	exit 1
	;;
esac

echo
echo "Selected firmware: $TYPE"
echo

MTD_EXE="/mtd_exe"
MTD_APPDATA="/mtd_appdata"
MTD_TLIB="/mtd_tlib"
INFO="/.info"
START="/sbin/samsung-start.sh"

download_firmware() {
	echo
	echo "Downloading $URL ..."
	echo
	wget -c $URL
	if [ $? != 0 ]; then
		echo "Error downloading: $URL!"
		echo "Exiting..."
		exit 1
	fi
	sum=`md5sum $FILENAME | cut -c1-32`
	if [ "$MD5SUM" != $sum ]; then
		echo "MD5 checksum is wrong for downloaded file: $FILENAME!"
		echo "Exiting..."
		exit 1
	fi
}

if [ ! -e $FILENAME ]; then
	echo "Firmware file '$FILENAME' not found in current directory."
	echo "To prevent download file from Samsung site, copy '$FILENAME'"
	echo "file to current directory ($PWD)."
	echo
	echo "You can quit script here or continue to download file."
	while true; do
		read -p "Choice ('q' - quite, 'd' - download): " sel
		if [ $sel == "q" ]; then
			echo "Exiting..."
			exit 1;
		fi
		if [ $sel == "d" ]; then
			download_firmware
			if [ ! -e $FILENAME ]; then
				echo "Unexpected missing file: $FILENAME after download!"
				echo "Exiting..."
			fi
			break;
		fi
	done
fi

while true; do
	sum=`md5sum $FILENAME | cut -c1-32`
	if [ "$MD5SUM" != $sum ]; then
		echo "MD5 checksum is wrong for $FILENAME in current directory!"
		echo "d) delete file and exit script,"
		echo "c) try continue download,"
		echo "r) delete and download file,"
		read -p "Select: " sel
		if [ $sel == "d" ]; then
			rm -f $FILENAME
			echo "Exiting..."
			exit 1
		fi
		if [ $sel == "r" ]; then
			rm -f $FILENAME
		fi
		download_firmware
		if [ ! -e $FILENAME ]; then
			echo "Unexpected missing file: $FILENAME after download!"
			echo "Exiting..."
			exit 1
		fi
	else
		break
	fi
done

case $TYPE in
T-CHEAUSC|T-CHL7DAUC|T-CHL7DEUC)
	if [ ! -e LaunchCLManager.zip ]; then
		echo "Downloading custom T_Library.swf ..."
		wget -O LaunchCLManager.zip -c http://sourceforge.net/projects/samygo/files/SamyGO%20OE/LaunchCLManager.zip/download 2> /dev/null
		if [ $? != 0 ]; then
			echo "Error downloading: LaunchCLManager.zip!"
			echo "Copy LaunchCLManager.zip to current directory."
			echo "Exiting..."
			exit 1
		fi
	fi
	;;
*)
	;;
esac

rm -rf tmp-work
mkdir -p tmp-work
cd tmp-work

echo "Decompressing Firmware package..."
$UNCOMP ../$FILENAME 1> /dev/null
if [ $? != 0 ]; then
	echo "Error uncompress file: $FILENAME!"
	echo "Exiting..."
	exit 1
fi

echo
echo "Decoding Firmware package..."
echo
for i in exe.img appdata.img ; do
	crypt-xor -f "${TYPE}/image/$i.enc" -K "${TYPE}" -force -q -outfile "${TYPE}/image/$i"
	if [ $? != 0 ]; then
		echo "Error decode file: $TYPE/image/$i.enc!"
		echo "Exiting..."
		exit 1
	fi
	rm -f "${TYPE}/image/$i.enc"
done

rm -rf $MTD_EXE
rm -rf $MTD_APPDATA

echo
echo "Unpacking mtd_exe..."
echo

case $TYPE in
T-CHEAUSC|T-CHL7DAUC|T-CHL7DEUC)
	mkdir -p ${MTD_EXE}
	mcopy -sQnv -i ${TYPE}/image/exe.img ::* ${MTD_EXE} 2> /dev/null
	if [ $? != 0 ]; then
		echo "Error unpack from exe.img!"
		echo "Exiting..."
		exit 1
	fi
	rm ${MTD_EXE}/\$RFS_LOG.LO\$
	rm -f ${MTD_EXE}/rc.local*
	rm -f ${MTD_EXE}/prelink.*
	chmod +x ${MTD_EXE}/exeDSP
	chmod +x ${MTD_EXE}/JadeTarget
	chmod +x ${MTD_EXE}/ddr_margin
	if [ -f ${MTD_EXE}/memalloc ]; then
		chmod +x ${MTD_EXE}/memalloc
	fi
	;;
*)
	;;
esac
rm -f ${TYPE}/image/exe.img

echo
echo "Unpacking mtd_appdata..."
echo

unsquashfs -da 32 -fr 32 -dest ${MTD_APPDATA} ${TYPE}/image/appdata.img 1> /dev/null
if [ $? != 0 ]; then
	echo "Error unpack from appdata.img!"
	echo "Exiting..."
	exit 1
fi
rm -rf ${MTD_APPDATA}/lib

rm -rf ${TYPE}

echo "${TYPE}" > ${INFO}
echo "SamyGO ${TYPE}" > /.version

case $TYPE in
T-CHEAUSC|T-CHL7DAUC|T-CHL7DEUC)
	echo
	echo "Creating minimal mtd_tlib..."
	echo
	unzip -qq ../LaunchCLManager.zip
	mkdir -p ${MTD_TLIB}/swf
	mv T_Library.swf ${MTD_TLIB}/swf/
	;;
*)
	;;
esac

echo "#! /bin/sh

PATH=/sbin:/bin:/usr/sbin:/usr/bin

firmware=\`cat \"/.info\"\`

case \$firmware in
|T-CHE7AUSC|T-CHEAUSC|T-CHL7DAUC|T-CHL7DEUC|T-CHU7DAUC|T-CHU7DEUC)
	mkdir -p /mtd_appdata /mtd_boot /mtd_contents /mtd_down /mtd_exe /mtd_ram /mtd_rwarea /mtd_swu /mtd_tlib /mtd_wiselink
	mkdir -p /mtd_exe/Java

	if [ ! -e /Java ]; then
		ln -s /mtd_exe/Java ${D}/Java
	fi

	for i in mtd_chmap mtd_epg mtd_factory mtd_pers mtd_acap ; do
		if [ ! -e /\$i ]; then
			ln -s /mtd_rwarea /\$i
		fi
	done

	for i in mtd_cmmlib mtd_drv ; do
		if [ ! -e /\$i ]; then
			ln -s /mtd_exe /\$i
		fi
	done

	CMMLIB=/mtd_cmmlib/InfoLink/lib
	export MAPLE_DEFAULT_PATH=\$CMMLIB
	export MAPLE_PLUGIN_DATA_PATH=\$CMMLIB

	WIDGETS=/mtd_down/widgets
	export MAPLE_MANAGER_WIDGET_PATH=\$WIDGETS/manager
	export MAPLE_NORMAL_WIDGET_PATH=\$WIDGETS/normal
	export MAPLE_WIDGET_DATA_PATH=/mtd_down
	export MAPLE_WIDGET_INCLUDE_PATH=\$WIDGETS/inc

	export KF_SLEEP_READ=-2
	export KF_NO_INTERACTIVE=1
	export KF_LOG=/dev/null

	echo 30000 > /mtd_rwarea/DelayValue.txt

	cd /mtd_exe/

	echo \"32\" > /proc/sys/kernel/msgmni

	mkdir -p /dev/sam
	if [ \`mount | grep -c /dev/sam\` == 0 ]; then
		mount -t tmpfs none /dev/sam -o size=1K,mode=1777
	fi

	if [ \`mount | grep -c /mtd_ram\` == 0 ]; then
		mount -t tmpfs none /mtd_ram -o size=10M,mode=1777
	fi

	if [ ! \"\`lsmod | grep samdrv\`\" ]; then
		insmod /mtd_drv/samdrv.ko
	fi
	sync

	export LD_LIBRARY_PATH=\"/lib:/Java/lib:/mtd_cmmlib/Comp_LIB:/mtd_cmmlib/InfoLink/lib:/mtd_cmmlib/GAME_LIB:/mtd_cmmlib/DRM_LIB:/mtd_cmmlib/YWidget_LIB\"

	echo \"*** Starting exeDSP ***\"
	./exeDSP
	echo \"*** Finished exeDSP ***\"
	;;

*)
	echo \"samsung-start.sh: Failed, unknown device!\"
	;;
esac

" > ${START}

chmod +x ${START}

cd ..

echo "Removing temporary files..."
rm -rf tmp-work

sync

echo "Finished."
