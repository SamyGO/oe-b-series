SECTION = "libs"
PRIORITY = "optional"
DESCRIPTION = "tremolo is arm assembly optimized tremor version of library."
LICENSE = "GPL,BSD"
PROVIDES = "tremor"
PR = "r0"

ARM_INSTRUCTION_SET = "arm"

SRC_URI = "http://wss.co.uk/pinknoise/tremolo/Tremolo${PV}.zip \
	file://build-fix.patch"

SRC_URI[md5sum] = "f2ab7a9c3230417c31174912cc2ba4d5"
SRC_URI[sha256sum] = "0ecfbdc0b3b84f7195c7f17eefa8dc1ca39bfc1c734d56e11a32ad002f9a0260"

S = "${WORKDIR}"

do_compile() {
	oe_runmake
}

do_install() {
	install -d ${D}${includedir}/tremor
	install -m 0644 config_types.h ${D}${includedir}/tremor
	install -m 0644 ivorbiscodec.h ${D}${includedir}/tremor
	install -m 0644 ivorbisfile.h ${D}${includedir}/tremor
	install -m 0644 ogg.h ${D}${includedir}/tremor
	install -m 0644 os_types.h ${D}${includedir}/tremor
	install -d ${D}${libdir}/tremor
	install -m 0644 libTremolo006.lib ${D}${libdir}/libvorbisidec.a
}

do_stage() {
	install -d ${STAGING_INCDIR}/tremor/
	install -m 0644 config_types.h ${STAGING_INCDIR}/tremor/
	install -m 0644 ivorbiscodec.h ${STAGING_INCDIR}/tremor/
	install -m 0644 ivorbisfile.h ${STAGING_INCDIR}/tremor/
	install -m 0644 ogg.h ${STAGING_INCDIR}/tremor/
	install -m 0644 os_types.h ${STAGING_INCDIR}/tremor/
	install -m 0644 libTremolo006.lib ${STAGING_LIBDIR}/libvorbisidec.a
}
