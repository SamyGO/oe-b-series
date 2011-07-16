PR = "${INC_PR}.0"

require gcc-${PV}.inc
require gcc-configure-target.inc
require gcc-package-target.inc

ARCH_FLAGS_FOR_TARGET += "-isystem${STAGING_INCDIR}"

export CPP="gcc -E"
export BUILD_LDFLAGS = "-L${STAGING_LIBDIR_NATIVE}"

SRC_URI += "file://workaround-bad-stdc++-build.patch \
	file://workaround-missing-auto-build.patch \
	file://auto-build.h \
	file://workaround-wrong-native-ldflags.patch \
"
