include zlib.inc

PR = "${INC_PR}.0"

SRC_URI += "	file://visibility.patch \
		file://autotools.patch "

SRC_URI[md5sum] = "debc62758716a169df9f62e6ab2bc634"
SRC_URI[sha256sum] = "1795c7d067a43174113fdf03447532f373e1c6c57c08d61d9e4e9be5e244b05e"

S = "${WORKDIR}/zlib-${PV}"

export CFLAGS = "-fvisibility=hidden"

EXTRA_OECONF += " --disable-shared"

do_configure_prepend() {
	touch ${S}/NEWS
	touch ${S}/AUTHORS
}

do_stage() {
	install -m 0644 ${S}/zlib.h ${STAGING_INCDIR}/
	install -m 0644 ${S}/zconf.h ${STAGING_INCDIR}/

	oe_libinstall -a libz ${STAGING_LIBDIR}
}
