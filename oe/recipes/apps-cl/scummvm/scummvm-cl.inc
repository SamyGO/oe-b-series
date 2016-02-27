DESCRIPTION = "Virtual Machine for several classic graphical point-and-click adventure games"
HOMEPAGE = "http://www.scummvm.org"
SECTION = "games"
PRIORITY = "optional"
LICENSE = "GPL"
DEPENDS = "libsdl-cl libmad-cl flac-cl tremolo-cl fluidsynth-cl zlib-cl freetype-cl"
PR = "r0"

SRC_URI = "http://www.scummvm.org/frs/scummvm/${PV}/scummvm-${PV}.tar.bz2"

inherit autotools

CCACHE = ""

PACKAGES = "${PN}"
FILES_${PN} = "/scummvm"

EXTRA_OECONF = "--host=samsungtv \
		--backend=sdl \
		--disable-alsa \
		--prefix=${prefix} \
		--with-ogg-prefix=${STAGING_LIBDIR}/.. \
		--with-tremor-prefix=${STAGING_LIBDIR}/.. \
		--enable-release --disable-debug \
		--enable-verbose-build \
		"

EXTRA_OEMAKE = "MANDIR=${mandir}"

do_configure() {
	./configure ${EXTRA_OECONF}
	# Workaround, because some env variables aren't recognised correctly
	sed -i "s/AS := as/AS := ${AS}/" ${S}/config.mk
	sed -i "s/AR := ar cru/AR := ${AR} cru/" ${S}/config.mk
	sed -i "s/STRIP := strip/STRIP := ${STRIP}/" ${S}/config.mk
	sed -i "s/RANLIB := ranlib/RANLIB := ${RANLIB}/" ${S}/config.mk
}

do_install() {
	install -d ${D}/scummvm
	install -m 0644 ${S}/scummvm.so ${D}/scummvm/libscummvm.so
	install -m 0644 ${S}/dists/engine-data/*.dat ${D}/scummvm/
	install -m 0644 ${S}/dists/engine-data/queen.tbl ${D}/scummvm/
	install -m 0644 ${S}/dists/engine-data/sky.cpt ${D}/scummvm/
	install -m 0644 ${S}/dists/pred.dic ${D}/scummvm/
	install -m 0644 ${S}/gui/themes/scummmodern.zip ${D}/scummvm/
	install -m 0644 ${S}/gui/themes/translations.dat ${D}/scummvm/
	install -m 0644 ${S}/backends/vkeybd/packs/vkeybd_default.zip ${D}/scummvm/
	install -m 0644 ${S}/AUTHORS ${D}/scummvm/
	install -m 0644 ${S}/COPYING ${D}/scummvm/
	install -m 0644 ${S}/COPYING.BSD ${D}/scummvm/
	install -m 0644 ${S}/COPYING.LGPL ${D}/scummvm/
	install -m 0644 ${S}/COPYING.FREEFONT ${D}/scummvm/
	install -m 0644 ${S}/COPYRIGHT ${D}/scummvm/
	install -m 0644 ${S}/NEWS ${D}/scummvm/
	install -m 0644 ${S}/README ${D}/scummvm/
	install -m 0644 ${S}/dists/samsungtv/clmeta.dat ${D}/scummvm/
	install -m 0644 ${S}/dists/samsungtv/scummvm.dat ${D}/scummvm/
	install -m 0644 ${S}/dists/samsungtv/scummvm.png ${D}/scummvm/
	install -m 0644 ${S}/dists/samsungtv/README-SamsungTV ${D}/scummvm/
}
