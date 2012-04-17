DESCRIPTION = "Interpreter for several 3D games"
HOMEPAGE = "http://www.residualvm.org"
SECTION = "games"
PRIORITY = "optional"
LICENSE = "GPL"
DEPENDS = "libsdl-cl libmad-cl zlib-cl freetype-cl"
PR = "r0"

SRC_URI = "${SOURCEFORGE_MIRROR}/residualvm/residualvm-${PV}.tar.bz2"

inherit autotools 

CCACHE = ""

PACKAGES = "${PN}"
FILES_${PN} = "/residualvm"

EXTRA_OECONF = "--host=samsungtv \
		--backend=sdl \
		--disable-alsa \
		--prefix=${prefix} \
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
	install -d ${D}/residualvm
	install -m 0644 ${S}/residualvm.so ${D}/residualvm/libresidualvm.so
	install -m 0644 ${S}/dists/engine-data/*.lab ${D}/residualvm/
	install -m 0644 ${S}/gui/themes/residualmodern.zip ${D}/residualvm/
	install -m 0644 ${S}/backends/vkeybd/packs/vkeybd_default.zip ${D}/residualvm/
	install -m 0644 ${S}/AUTHORS ${D}/residualvm/
	install -m 0644 ${S}/COPYING ${D}/residualvm/
	install -m 0644 ${S}/COPYING.BSD ${D}/residualvm/
	install -m 0644 ${S}/COPYING.LGPL ${D}/residualvm/
	install -m 0644 ${S}/COPYING.FREETYPE ${D}/residualvm/
	install -m 0644 ${S}/COPYRIGHT ${D}/residualvm/
	install -m 0644 ${S}/NEWS ${D}/residualvm/
	install -m 0644 ${S}/README ${D}/residualvm/
	install -m 0644 ${S}/dists/samsungtv/clmeta.dat ${D}/residualvm/
	install -m 0644 ${S}/dists/samsungtv/residualvm.dat ${D}/residualvm/
	install -m 0644 ${S}/dists/samsungtv/residualvm.png ${D}/residualvm/
}
