DESCRIPTION = "OPKG Package Manager Utilities"
SECTION = "base"
HOMEPAGE = "http://wiki.openmoko.org/wiki/Opkg"
LICENSE = "GPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=94d55d512a9ba36caa9b7df079bae19f \
                     file://opkg.py;beginline=1;endline=18;md5=15917491ad6bf7acc666ca5f7cc1e083"
RDEPENDS_${PN} = "python"
RDEPENDS_${PN}_virtclass-native = ""
SRCREV = "423ecd36b4782327c16f516885d1248249c7724a"
PV = "0.1.8+git${SRCPV}"
PR = "r1"

#MobiAqua: added fix-for-cutoff-filenames.patch, remove_f_from_ar.patch, fix_call.patch
SRC_URI = "git://git.yoctoproject.org/opkg-utils;protocol=git \
           file://fix-for-cutoff-filenames.patch \
           file://remove_f_from_ar.patch \
           file://fix_call.patch \
           "

S = "${WORKDIR}/git"

do_install() {
	oe_runmake PREFIX=${prefix} DESTDIR=${D} install
}

BBCLASSEXTEND = "native"
TARGET_CC_ARCH += "${LDFLAGS}"
