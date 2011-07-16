DESCRIPTION = "Fluidsynth is a software synthesizer"
HOMEPAGE = "http://www.fluidsynth.org/"
SECTION = "libs/multimedia"
LICENSE = "GPLv2"

SRC_URI = "http://savannah.nongnu.org/download/fluid/fluidsynth-${PV}.tar.gz"

SRC_URI[md5sum] = "e2abfd2e69fd8b28d965df968d7d44ee"
SRC_URI[sha256sum] = "45e7c9967d0fb0344f4da539ab343fb979384b36a429a8594c94cf466dff4320"

inherit autotools pkgconfig lib_package

S = "${WORKDIR}/fluidsynth-${PV}"

EXTRA_OECONF += " --disable-shared"

#Has broken libtool usage
do_configure() {
	gnu-configize
	oe_runconf
}

do_stage() {
	install -d ${STAGING_INCDIR}/fluidsynth
	install -m 0644 ${S}/include/fluidsynth.h ${STAGING_INCDIR}/
	install -m 0644 ${S}/include/fluidsynth/*.h ${STAGING_INCDIR}/fluidsynth

	oe_libinstall -C src -a libfluidsynth ${STAGING_LIBDIR}
}

