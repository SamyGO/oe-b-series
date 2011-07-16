DESCRIPTION = "FLAC is a Free Lossless Audio Codec."
HOMEPAGE = "http://flac.sourceforge.net"
LICENSE = "BSD GPL"
SECTION = "libs"

SRC_URI = "${SOURCEFORGE_MIRROR}/flac/flac-${PV}.tar.gz \
	   file://xmms.m4"

S = "${WORKDIR}/flac-${PV}"

inherit autotools

EXTRA_OECONF = "--disable-ogg --disable-id3libtest \
                --disable-xmms-plugin \
		--disable-shared \
		--without-xmms-prefix \
		--without-xmms-exec-prefix \
		--without-libiconv-prefix \
		--without-id3lib"

do_configure () {
	install -d ${S}/m4
	install -m 0644 ${WORKDIR}/xmms.m4 ${S}/m4/
	autotools_do_configure
}

do_stage () {
	autotools_stage_includes
	oe_libinstall -a libFLAC ${STAGING_LIBDIR}/
	oe_libinstall -a libFLAC++ ${STAGING_LIBDIR}/
}

PACKAGES += "libflac-cl libflac++-cl"
FILES_${PN} = "${bindir}/*"
FILES_libflac-cl = "${libdir}/libFLAC.so.*"
FILES_libflac++-cl = "${libdir}/libFLAC++.so.*"
