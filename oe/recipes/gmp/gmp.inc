SECTION = "libs"
DESCRIPTION = "GNU multiprecision arithmetic library"
HOMEPAGE = "http://www.swox.com/gmp/"
LICENSE = "GPL LGPL"
INC_PR = "r2"

#MobiAqua: fixed configure.patch by replace echo -n with printf
SRC_URI = "${GNU_MIRROR}/gmp/gmp-${PV}.tar.bz2;name=gmp \
	   file://configure.patch \
            file://configure-sdk.patch \
            file://configure-no-doc.patch \
	   file://amd64.patch"

inherit autotools 

ARM_INSTRUCTION_SET = "arm"


EXTRA_OECONF_append_virtclass-native = " --enable-static"

#SamyGO: disable BBCLASSEXTEND and NATIVE_INSTALL_WORKS, and added separate native package
#BBCLASSEXTEND = "native nativesdk sdk"
#NATIVE_INSTALL_WORKS = "1"

acpaths = ""

CFLAGS_EXTRA_virtclass-sdk = ""
