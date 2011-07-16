include zlib.inc

PR = "${INC_PR}.0"

SRC_URI += "	file://visibility.patch \
		file://autotools.patch "

SRC_URI[md5sum] = "dee233bf288ee795ac96a98cc2e369b6"
SRC_URI[sha256sum] = "e3b9950851a19904d642c4dec518623382cf4d2ac24f70a76510c944330d28ca"

S = "${WORKDIR}/zlib-${PV}"

export CFLAGS = "-fvisibility=hidden"

EXTRA_OECONF += " --disable-shared"

do_stage() {
	install -m 0644 ${S}/zlib.h ${STAGING_INCDIR}/
	install -m 0644 ${S}/zconf.h ${STAGING_INCDIR}/

	oe_libinstall -a libz ${STAGING_LIBDIR}
}
