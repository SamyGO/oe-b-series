DESCRIPTION = "libusb is a library to provide userspace access to USB devices."
HOMEPAGE = "http://libusb.sf.net"
SECTION = "libs"
LICENSE = "LGPLv2.1"
PROVIDES = "virtual/libusb0"
PR = "r4"

SRC_URI = "${SOURCEFORGE_MIRROR}/libusb/libusb-${PV}.tar.gz \
	   file://configure_fix.patch"

S = "${WORKDIR}/libusb-${PV}"

inherit autotools pkgconfig binconfig lib_package

PARALLEL_MAKE = ""
EXTRA_OECONF = "--disable-build-docs"

export CXXFLAGS += "-lstdc++ -I${STAGING_INCDIR}"

do_stage() {

	autotools_stage_all
	install -m 755 ${S}/libusb-config ${STAGING_BINDIR}
	# can we get rid of that? wouldn't a sed statement do as well?
	sed -i 's:\-L${libdir} :-L${STAGING_LIBDIR} :' ${STAGING_BINDIR}/libusb-config

	if [ "${STAGING_BINDIR}" != "${STAGING_BINDIR_CROSS}" ]; then
	        install -d ${STAGING_BINDIR_CROSS}/
		mv ${STAGING_BINDIR}/libusb-config ${STAGING_BINDIR_CROSS}/libusb-config
	fi

}

PACKAGES =+ "libusbpp"

FILES_libusbpp = "${libdir}/libusbpp*.so.*"

SRC_URI[md5sum] = "caf182cbc7565dac0fd72155919672e6"
SRC_URI[sha256sum] = "37f6f7d9de74196eb5fc0bbe0aea9b5c939de7f500acba3af6fd643f3b538b44"
