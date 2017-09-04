#!/bin/sh

error() {
	echo
	echo "* ERROR * " $1
	echo
	[ "x$0" = "x./setup.sh" ] && exit 1
	ERROR=1
}

python_v3_check() {
	ver=`/usr/bin/env python --version 2>&1 | grep "Python 3"`
	if [ "${ver}" != "" ]; then
		return 1
	else
		return 0
	fi
}

get_os() {
	if [ -e /bin/uname ]; then
		OS=`/bin/uname -s`
	elif [ -e /usr/bin/uname ]; then
		OS=`/usr/bin/uname -s`
	else
		OS=`uname -s`
	fi
	export $OS
}

gnutools="[ awk b2sum base32 base64 basename cat chcon chgrp chmod chown chroot cksum comm cp \
csplit cut date dd df dir dircolors dirname du echo env expand expr factor false fmt fold \
groups head hostid id install join kill link ln logname ls md5sum mkdir mkfifo mknod mktemp \
mv nice nl nohup nproc numfmt od paste pathchk pinky pr printenv printf ptx pwd readlink \
realpath rm rmdir runcon sed seq sha1sum sha224sum sha256sum sha384sum sha512sum shred shuf \
sleep sort split stat stdbuf stty sum sync tac tail tee test timeout touch tr true \
truncate tsort tty uname unexpand uniq unlink uptime users vdir wc who whoami yes"

prepare_tools() {
	OE_BASE=`pwd -P`
	/bin/rm -f ${OE_BASE}/oe/bin/deftar
	/bin/rm -f ${OE_BASE}/oe/bin/tar
	/bin/rm -f ${OE_BASE}/oe/bin/\]
	/bin/rm -f ${OE_BASE}/oe/bin/\[

	get_os
	case $OS in
	Darwin)
		if [ -e /opt/local/bin/gnutar ]; then
			/bin/ln -s /opt/local/bin/gnutar ${OE_BASE}/oe/bin/tar
		elif [ -e /sw/bin/gtar ]; then
			/bin/ln -s /sw/bin/gtar ${OE_BASE}/oe/bin/tar
		fi
		if [ -e /usr/bin/tar ]; then
			/bin/ln -s /usr/bin/tar ${OE_BASE}/oe/bin/deftar
		fi
		for i in $gnutools; do
			/bin/rm -f ${OE_BASE}/oe/bin/$i
			if [ -e /opt/local/bin/g$i ]; then
				/bin/ln -s /opt/local/bin/g$i ${OE_BASE}/oe/bin/$i
			elif [ -e /sw/sbin/g$i ]; then
				/bin/ln -s /sw/sbin/g$i ${OE_BASE}/oe/bin/$i
			fi
		done

		if [ ! -e /opt/local/bin/gnutar ] && [ ! -e /sw/bin/gtar ]; then
			echo "* ERROR *  Missing GNU tar!"
			return 1
		fi
		if [ ! -e /opt/local/bin/gsed ] && [ ! -e /sw/bin/gsed ]; then
			echo "* ERROR *  Missing GNU sed!"
			return 1
		fi
		if [ ! -e /opt/local/bin/ginstall ] && [ ! -e /sw/bin/ginstall ]; then
			echo "* ERROR *  Missing GNU coreutils!"
			return 1
		fi
		;;
	Linux)
		if [ -e /bin/tar ]; then
			/bin/ln -s /bin/tar ${OE_BASE}/oe/bin/deftar
		fi
	esac

	return 0
}

setup() {
	export OE_BASE=`${OE_BASE}/oe/bin/readlink -f "$OE_BASE"`

	DISTRO=samygo
	MACHINE=ssdtv

	if [ "$1" = "-cl" ] || [ "$2" = "-cl" ]; then
		DISTRO=samygo-cl
	fi
	DL_DIR=${DL_DIR:="$HOME/sources"}

	mkdir -p  ${OE_BASE}/build-${DISTRO}/conf

	BBF="\${OE_BASE}/oe/recipes/*/*.bb"
	if [ "${DISTRO}" = "samygo-cl" ]; then
		BBF="${BBF} \${OE_BASE}/oe/recipes/apps-cl/*/*.bb"
	fi

	if [ ! -f ${OE_BASE}/build-${DISTRO}/conf/local.conf ] || [ ! -f ${OE_BASE}/build-${DISTRO}/env.source ] || [ "$1" = "-f" ] || [ "$2" = "-f" ]; then
		PATH_TO_TOOLS="build-${DISTRO}/tmp/sysroots/`uname -m`-`uname -s | awk '{print tolower($0)}'`/usr"
		echo "DL_DIR = \"${DL_DIR}\"
OE_BASE = \"${OE_BASE}\"
BBFILES = \"${BBF}\"
MACHINE = \"${MACHINE}\"
TARGET_OS = \"linux-gnueabi\"
DISTRO = \"${DISTRO}\"
INHERIT = \"rm_work\"
IMAGE_KEEPROOTFS = \"1\"
CACHE = \"${OE_BASE}/build-${DISTRO}/cache/oe-cache.\${USER}\"
ASSUME_PROVIDED += \" git-native perl-native python-native desktop-file-utils-native linux-libc-headers-native glib-2.0-native intltool-native xz-native\"
PARALLEL_MAKE = \"-j 4\"
BB_NUMBER_THREADS = \"3\"
" > ${OE_BASE}/build-${DISTRO}/conf/local.conf



		echo "OE_BASE=\"${OE_BASE}\"
export BBPATH=\"\${OE_BASE}/oe/:\${OE_BASE}/bb/:\${OE_BASE}/build-${DISTRO}/\"
if [ ! \`echo \${PATH} | grep \${OE_BASE}/bb/bin\` ]; then
	export PATH=\${OE_BASE}/bb/bin:\${OE_BASE}/oe/bin:\${PATH}
fi
unset LD_LIBRARY_PATH
export LD_LIBRARY_PATH=
export PYTHONPATH=${OE_BASE}/bb/lib
export LANG=C
unset TERMINFO
unset GCONF_SCHEMA_INSTALL_SOURCE
" > ${OE_BASE}/build-${DISTRO}/env.source



		echo "source ${OE_BASE}/build-${DISTRO}/env.source
if [ ! \`echo \${PATH} | grep armv6/bin\` ]; then
	export PATH=${OE_BASE}/${PATH_TO_TOOLS}/armv6/bin:${OE_BASE}/${PATH_TO_TOOLS}/bin:\${PATH}
fi
export CROSS_COMPILE=arm-linux-gnueabi-
" > ${OE_BASE}/build-${DISTRO}/crosstools-setup



		echo "--- Created:"
		echo " -  ${OE_BASE}/build-${DISTRO}/conf/local.conf,"
		echo " -  ${OE_BASE}/build-${DISTRO}/env.source,"
		echo " -  ${OE_BASE}/build-${DISTRO}/crosstools-setup ---"
	fi

	if [ "${DISTRO}" = "samygo-cl" ]; then
		COMMAND="scummvm-cl"
		RESULT_DIR="ipk/armv6"
	else
		COMMAND="externalboot-base"
		RESULT_DIR="images"
	fi

	echo
	echo "--- SamyGO OE configuration finished ---"
	echo
	echo "--- Usage example: bitbake ${COMMAND} ---"
	echo
	echo "--- After building all tools, results are at build-${DISTRO}/tmp/deploy/${RESULT_DIR} directory. ---"
	echo
}

bitbake() {
	cd ${OE_BASE}/build-${DISTRO} && source env.source && ${OE_BASE}/bb/bin/bitbake $@
}

ERROR=
[ "x$0" = "x./setup.sh" ] && error "Script must run via sourcing like '. setup.sh [-cl] [-f]'"

[ "$ERROR" != "1" ] && [ $EUID -eq 0 ] && error "Script running with superuser privileges! Aborting."

[ "$ERROR" != "1" ] && [ -z "$BASH_VERSION" ] && error "Script NOT running in 'bash' shell"

[ "$ERROR" != "1" ] && python_v3_check; [ "$?" != "0" ] && error "Python v3 is not compatible please install v2"

[ "$ERROR" != "1" ] && prepare_tools; [ "$?" != "0" ] && error "Please install missing tools"

[ "$ERROR" != "1" ] && setup $1
