DESCRIPTION = "Lossless data compression library"
HOMEPAGE = "http://www.oberhumer.com/opensource/lzo/"
SECTION = "libs"
LICENSE = "GPLv2+"
PR = "r1"

SRC_URI = "http://www.oberhumer.com/opensource/lzo/download/lzo-${PV}.tar.gz \
           file://acinclude.m4 \
           "

SRC_URI[md5sum] = "95380bd4081f85ef08c5209f4107e9f8"
SRC_URI[sha256sum] = "ff79e6f836d62d3f86ef6ce893ed65d07e638ef4d3cb952963471b4234d43e73"

inherit autotools

EXTRA_OECONF = "--enable-shared"

do_configure_prepend () {
	cp ${WORKDIR}/acinclude.m4 ${S}/
}

do_configure() {
	gnu-configize --force
	oe_runconf
}

BBCLASSEXTEND = "native nativesdk"
