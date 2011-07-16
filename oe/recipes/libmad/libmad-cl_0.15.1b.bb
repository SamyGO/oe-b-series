DESCRIPTION = "MPEG Audio Decoder Library"
SECTION = "libs"
PRIORITY = "optional"
LICENSE = "GPL"
PR = "r0"

SRC_URI = "${SOURCEFORGE_MIRROR}/mad/libmad-${PV}.tar.gz \
           file://add-pkgconfig.patch \
	   file://mad.diff \
	   file://mad-mips-h-constraint.patch"

SRC_URI[md5sum] = "1be543bc30c56fb6bea1d7bf6a64e66c"
SRC_URI[sha256sum] = "bbfac3ed6bfbc2823d3775ebb931087371e142bb0e9bb1bee51a76a6e0078690"

S = "${WORKDIR}/libmad-${PV}"

inherit autotools pkgconfig

EXTRA_OECONF = "--enable-speed --disable-shared"
EXTRA_OECONF_append_arm = " --enable-fpm=arm"

do_configure_prepend () {
	touch NEWS AUTHORS ChangeLog
}

do_stage() {
	oe_libinstall -a libmad ${STAGING_LIBDIR}
	install -m 0644 mad.h ${STAGING_INCDIR}
}

ARM_INSTRUCTION_SET = "arm"
