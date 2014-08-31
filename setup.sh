#!/bin/sh

is_root=`id | grep root`
if [ "$is_root" ]; then
	echo
	echo "* ERROR * You are with 'root' privileges ! Aborting."
	echo
	exit 1
fi

if [ $0 = "./setup.sh" ]; then
	echo
	echo "* ERROR * You must run via '. setup.sh [-cl] [-f]'"
	echo
	exit 1
fi

export OE_BASE=`pwd -P`

if [ -e /bin/uname ]; then
	os=`/bin/uname -s`
elif [ -e /usr/bin/uname ]; then
	os=`/usr/bin/uname -s`
else
	os=`uname -s`
fi

rm -f ${OE_BASE}/oe/bin/deftar
rm -f ${OE_BASE}/oe/bin/tar
rm -f ${OE_BASE}/oe/bin/sed
rm -f ${OE_BASE}/oe/bin/readlink
case $os in
Darwin)
	if [ -e /opt/local/bin/gnutar ]; then
		ln -s /opt/local/bin/gnutar ${OE_BASE}/oe/bin/tar
	elif [ -e /sw/bin/gtar ]; then
		ln -s /sw/bin/gtar ${OE_BASE}/oe/bin/tar
	fi
	if [ -e /usr/bin/tar ]; then
		ln -s /usr/bin/tar ${OE_BASE}/oe/bin/deftar
	fi
	if [ -e /opt/local/bin/gsed ]; then
		ln -s /opt/local/bin/gsed ${OE_BASE}/oe/bin/sed
	elif [ -e /sw/bin/gsed ]; then
		ln -s /sw/bin/gsed ${OE_BASE}/oe/bin/sed
	fi
	if [ -e /opt/local/bin/greadlink ]; then
		ln -s /opt/local/bin/greadlink ${OE_BASE}/oe/bin/readlink
	elif [ -e /sw/sbin/greadlink ]; then
		ln -s /sw/sbin/greadlink ${OE_BASE}/oe/bin/readlink
	fi
	;;
Linux)
	if [ -e /bin/tar ]; then
		ln -s /bin/tar ${OE_BASE}/oe/bin/deftar
	fi
esac

OE_BASE=`${OE_BASE}/oe/bin/readlink -f "$OE_BASE"`

MACHINE=ssdtv
DISTRO=samygo
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
ASSUME_PROVIDED += \" git-native perl-native python-native desktop-file-utils-native linux-libc-headers-native \"
PARALLEL_MAKE = \"-j 2\"
BB_NUMBER_THREADS = \"2\"" > ${OE_BASE}/build-${DISTRO}/conf/local.conf

	echo "OE_BASE=\"${OE_BASE}\"
export BBPATH=\"\${OE_BASE}/oe/:\${OE_BASE}/bb/:\${OE_BASE}/build-${DISTRO}/\"
if [ ! \`echo \${PATH} | grep \${OE_BASE}/bb/bin\` ]; then
	export PATH=\${OE_BASE}/bb/bin:\${OE_BASE}/oe/bin:\${PATH}
fi
export LD_LIBRARY_PATH=
export PYTHONPATH=${OE_BASE}/bb/lib
export LANG=C" > ${OE_BASE}/build-${DISTRO}/env.source

echo "
source ${OE_BASE}/build-${DISTRO}/env.source
if [ ! \`echo \${PATH} | grep armv6/bin\` ]; then
	export PATH=${OE_BASE}/${PATH_TO_TOOLS}/armv6/bin:${OE_BASE}/${PATH_TO_TOOLS}/bin:\${PATH}
fi
" > ${OE_BASE}/build-${DISTRO}/crosstools-setup


echo "--- Created ${OE_BASE}/build-${DISTRO}/conf/local.conf, ${OE_BASE}/build-${DISTRO}/env.source and ${OE_BASE}/build-${DISTRO}/crosstools-setup ---"

fi

bitbake() {
	cd ${OE_BASE}/build-${DISTRO} && source env.source && ${OE_BASE}/bb/bin/bitbake $@
}

echo
echo "--- SamyGO OE configuration finished ---"
echo
if [ "${DISTRO}" = "samygo-cl" ]; then
echo "--- Usage example: bitbake scummvm-cl ---"
else
echo "--- Usage example: bitbake externalboot-base ---"
fi
echo

