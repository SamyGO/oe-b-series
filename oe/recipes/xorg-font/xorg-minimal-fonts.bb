HOMEPAGE = "http://www.x.org"
SECTION = "x11/fonts"
LICENSE = "MIT-X"

PR = "1"

SRC_URI = "file://misc"

do_install() {
	install -d ${D}/${datadir}/fonts/X11/misc
	install -m 0644 ${WORKDIR}/misc/* ${D}/${datadir}/fonts/X11/misc/
	install -d ${D}/${libdir}/X11
	#LocalChange: fixed redunand -s at the and of command
	ln -sf ${datadir}/fonts/X11/ ${D}/${libdir}/X11/fonts

}

PACKAGE_ARCH = "all"
FILES_${PN} = "${libdir}/X11/ ${datadir}/fonts/X11/"
