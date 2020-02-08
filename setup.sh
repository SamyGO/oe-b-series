#!/bin/bash

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
		python_path=`whereis python2`
		if [ "$python_path" = "" ]; then
			return 1
		else
			OE_BASE=`pwd -P`
			/bin/rm -f ${OE_BASE}/oe/bin/python
			/bin/ln -s $python_path ${OE_BASE}/oe/bin/python
			return 0
		fi
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
csplit date dd df dir dircolors dirname du echo env expand expr factor false fmt fold \
groups head hostid id install join kill link ln logname ls md5sum mkdir mkfifo mknod mktemp \
mv nice nl nohup nproc numfmt od paste pathchk pinky pr printenv printf ptx pwd readlink \
realpath rm rmdir runcon sed seq sha1sum sha224sum sha256sum sha384sum sha512sum shred shuf \
sleep sort split stat stdbuf stty sum sync tac tail tee test timeout touch tr true \
truncate tsort tty uname unexpand uniq unlink uptime users vdir wc who whoami yes"

tools="perl git wget gzip patch diffstat texi2html file bison flex help2man unzip"

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
		fi
		if [ -e /usr/bin/tar ]; then
			/bin/ln -s /usr/bin/tar ${OE_BASE}/oe/bin/deftar
		fi
		for i in $gnutools; do
			/bin/rm -f ${OE_BASE}/oe/bin/$i
			if [ -e /opt/local/bin/g$i ]; then
				/bin/ln -s /opt/local/bin/g$i ${OE_BASE}/oe/bin/$i
			fi
		done

		if [ ! -e /opt/local/bin/gnutar ]; then
			echo "* ERROR *  Missing GNU tar!"
			return 1
		fi
		if [ ! -e /opt/local/bin/gsed ]; then
			echo "* ERROR *  Missing GNU sed!"
			return 1
		fi
		if [ ! -e /opt/local/bin/ginstall ]; then
			echo "* ERROR *  Missing GNU coreutils!"
			return 1
		fi
		if [ ! -e /opt/local/bin/gxargs ]; then
			echo "* ERROR *  Missing GNU findutils!"
			return 1
		fi
		;;
	Linux)
		if [ -e /bin/tar ]; then
			rm -f ${OE_BASE}/oe/bin/deftar
			/bin/ln -s /bin/tar ${OE_BASE}/oe/bin/deftar
		fi
		if [ -e /bin/readlink ]; then
			rm -f ${OE_BASE}/oe/bin/readlink
			/bin/ln -s /bin/readlink ${OE_BASE}/oe/bin/readlink
		fi
	esac

	if [ "$OS" = "Darwin" ]; then
		for i in $tools; do
			path=`whereis $i`
			if [ "$path" = "" ]; then
				/bin/rm -f ${OE_BASE}/oe/bin/$i
				if [ -e /opt/local/bin/$i ]; then
					/bin/ln -s /opt/local/bin/$i ${OE_BASE}/oe/bin/$i
				else
					echo "* ERROR *  Missing $i!"
					return 1
				fi
			fi
		done
	fi
	if [ "$OS" = "Linux" ]; then
		for i in $tools; do
			if [ ! -e /usr/bin/$i ] && [ ! -e /bin/$i ]; then
				echo "* ERROR *  Missing $i!"
				return 1
			fi
		done
	fi

	if [ "$OS" = "Darwin" ]; then
		path=`whereis desktop-file-install`
		if [ ! -e /opt/local/bin/desktop-file-install ]; then
			echo "* ERROR *  Missing desktop-file-utils package"
			return 1
		fi
	fi
	if [ "$OS" == "Linux" ] && [ ! -e /usr/bin/desktop-file-install ]; then
		echo "* ERROR *  Missing desktop-file-utils package"
		return 1
	fi

	if [ "$OS" = "Darwin" ]; then
		path=`whereis intltoolize`
		if [ ! -e /opt/local/bin/intltoolize ]; then
			echo "* ERROR *  Missing intltool package"
			return 1
		fi
	fi
	if [ "$OS" == "Linux" ] && [ ! -e /usr/bin/intltoolize ]; then
		echo "* ERROR *  Missing intltool package"
		return 1
	fi

	if [ "$OS" = "Darwin" ]; then
		path=`whereis xz`
		if [ ! -e /opt/local/bin/xz ]; then
			echo "* ERROR *  Missing xz package"
			return 1
		fi
	fi
	if [ "$OS" == "Linux" ] && [ ! -e /usr/bin/xz ]; then
		echo "* ERROR *  Missing xz-utils package"
		return 1
	fi

	if [ ! -e /usr/bin/m4 ]; then
		echo "* ERROR *  Missing m4 package"
		return 1
	fi

	if [ "$OS" = "Darwin" ]; then
		path=`whereis makeinfo`
		if [ ! -e /opt/local/bin/makeinfo ]; then
			echo "* ERROR *  Missing texinfo package"
			return 1
		fi
	fi
	if [ "$OS" == "Linux" ] && [ ! -e /usr/bin/makeinfo ]; then
		echo "* ERROR *  Missing texinfo package"
		return 1
	fi

	if [ "$OS" = "Darwin" ]; then
		path=`whereis svn`
		if [ ! -e /opt/local/bin/svn ]; then
			echo "* ERROR *  Missing subversion package"
			return 1
		fi
	fi
	if [ "$OS" == "Linux" ] && [ ! -e /usr/bin/svn ]; then
		echo "* ERROR *  Missing subversion package"
		return 1
	fi

	if [ "$OS" = "Darwin" ]; then
		path=`whereis glibtool`
		if [ ! -e /opt/local/bin/glibtool ]; then
			echo "* ERROR *  Missing glib2 package"
			return 1
		fi
	fi
	if [ "$OS" == "Linux" ] && [ ! -e /usr/bin/gapplication ]; then
		echo "* ERROR *  Missing libglib2.0-bin package"
		return 1
	fi

	if [ "$OS" = "Darwin" ]; then
		path=`whereis xargs`
		if [ "$path" = "" ]; then
			echo "* ERROR *  Missing findutils package"
			return 1
		fi
	fi
	if [ "$OS" == "Linux" ] && [ ! -e /usr/bin/xargs ]; then
		echo "* ERROR *  Missing findutils package"
		return 1
	fi

	if [ "$OS" = "Darwin" ]; then
		/bin/rm -f ${OE_BASE}/oe/bin/find
		if [ -e /opt/local/bin/gfind ]; then
			/bin/ln -s /opt/local/bin/gfind ${OE_BASE}/oe/bin/find
		else
			echo "* ERROR *  Missing findutils package"
			return 1
		fi
	fi
	if [ "$OS" == "Linux" ] && [ ! -e /usr/bin/find ]; then
		echo "* ERROR *  Missing findutils package"
		return 1
	fi

	return 0
}

setup() {
	export OE_BASE=`${OE_BASE}/oe/bin/readlink -f "$OE_BASE"`

	DISTRO=samygo
	MACHINE=ssdtv

	if [ -e ${HOME}/.samygo/oe/${DISTRO}_config ]; then
		. ${HOME}/.samygo/oe/${DISTRO}_config
		echo "Reading custom settings from file '${HOME}/.samygo/oe/${DISTRO}_config'"
	else
		echo "No custom settings file: '${HOME}/.samygo/oe/${DISTRO}_config'"
		echo "Using defaults instead."
	fi

	if [ "$1" = "-cl" ] || [ "$2" = "-cl" ]; then
		DISTRO=samygo-cl
	fi
	MA_DL_DIR=${MA_DL_DIR:="$HOME/sources"}
	export MA_TARGET_IP=${MA_TARGET_IP:="192.168.1.2"}
	export MA_TARGET_MASK=${MA_TARGET_MAASK:="255.255.255.0"}
	export MA_TARGET_MAC=${MA_TARGET_MAC:=""}
	export MA_GATEWAY_IP=${MA_GATEWAY_IP:="192.168.1.1"}
	export MA_NFS_IP=${MA_NFS_IP:="192.168.1.1"}
	export MA_NFS_PATH=${MA_NFS_PATH:="/nfsroot"}
	export MA_ROOT_PASSWORD=${MA_ROOT_PASSWORD:=""}
	export MA_DROPBEAR_KEY_FILE="$HOME/.samygo/oe/${DISTRO}_dropbear_rsa_host_key"
	export MA_ROOTFS_POSTPROCESS=${MA_ROOTFS_POSTPROCESS:="echo"}
	export BB_ENV_EXTRAWHITE="MA_TARGET_IP MA_TARGET_MASK MA_TARGET_MAC MA_GATEWAY_IP MA_NFS_IP MA_NFS_PATH \
			MA_ROOT_PASSWORD MA_DROPBEAR_KEY_FILE MA_FSTAB_FILE MA_ROOTFS_POSTPROCESS"

	echo "--- Settings:"
	echo " -  sources:     ${MA_DL_DIR}"
	echo " -  target ip:   ${MA_TARGET_IP}"
	echo " -  target mask: ${MA_TARGET_MASK}"
	echo " -  target mac:  ${MA_TARGET_MAC}"
	echo " -  gateway ip   ${MA_GATEWAY_IP}"
	echo " -  nfs ip:      ${MA_NFS_IP}"
	echo " -  nfs path:    ${MA_NFS_PATH}"
	if [ "$MA_ROOT_PASSWORD" != "" ]; then
		echo " -  root password is defined"
	else
		echo " -  root password is NOT defined"
	fi
	if [ -f ${MA_DROPBEAR_KEY_FILE} ]; then
		echo " -  target dropbear host key file found"
	else
		echo " -  target dropbear host key file NOT found"
	fi
	mkdir -p  ${OE_BASE}/build-${DISTRO}/conf

	BBF="\${OE_BASE}/oe/recipes/*/*.bb"
	if [ "${DISTRO}" = "samygo-cl" ]; then
		BBF="${BBF} \${OE_BASE}/oe/recipes/apps-cl/*/*.bb"
	fi

	DL_DIR=${MA_DL_DIR:="$HOME/sources"}

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
ASSUME_PROVIDED += \" git-native perl-native python-native desktop-file-utils-native \
linux-libc-headers-native glib-2.0-native intltool-native xz-native gzip-native \
findutils-native file-native bison-native flex-native help2man-native \
m4-native unzip-native\"
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

[ "$ERROR" != "1" ] && [ -z "$BASH_VERSION" ] && error "Script NOT running in 'bash' shell"

[ "x$0" = "x./setup.sh" ] && error "Script must run via sourcing like '. setup.sh [-cl] [-f]'"

[ "$ERROR" != "1" ] && [ $EUID -eq 0 ] && error "Script running with superuser privileges! Aborting."

[ "$ERROR" != "1" ] && python_v3_check; [ "$?" != "0" ] && error "Python v3 is not compatible please install v2"

[ "$ERROR" != "1" ] && prepare_tools; [ "$?" != "0" ] && error "Please install missing tools"

[ "$ERROR" != "1" ] && setup $1
