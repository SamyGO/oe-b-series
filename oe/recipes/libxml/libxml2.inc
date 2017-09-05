DESCRIPTION = "GNOME XML Parser library"
SECTION = "libs"
PRIORITY = "optional"
LICENSE = "MIT"
DEPENDS_virtclass-native = "python-native zlib-native pkgconfig-native"

SRC_URI = "ftp://xmlsoft.org/libxml2/libxml2-${PV}.tar.gz;name=archive"
S = "${WORKDIR}/${BPN}-${PV}"

nolargefile = "${@base_contains('DISTRO_FEATURES', 'largefile', '', '-DNO_LARGEFILE_SOURCE', d)}"

INC_PR = "r1"

BBCLASSEXTEND = "native"

inherit autotools pkgconfig binconfig

EXTRA_OECONF = "\
 --without-legacy \
 --with-catalog \
 --without-docbook \
 --with-c14n \
 --without-lzma \
 --with-zlib \
"

XPY = " --without-python --enable-static"
XPY_virtclass-native = " --without-python --enable-static"

EXTRA_OECONF += "${XPY}"

export LDFLAGS += "-ldl"

do_install_append() {
	install -d ${D}${datadir}/aclocal
 	install -m 0644 libxml.m4 ${D}${datadir}/aclocal
	#this is need it by php during its install
	install -d ${STAGING_BINDIR_CROSS}
	install -m 0755 xml2-config ${STAGING_BINDIR_CROSS}/
}

do_install_append_virtclass-native() {
	:
}

DEBIANNAME_${PN} = "libxml2"

PACKAGES =+ "${PN}-utils"
FILES_${PN} = "${libexecdir}/* ${libdir}/lib*${SOLIBS} \
            ${sysconfdir} ${sharedstatedir} ${localstatedir} \
            ${base_libdir}/*${SOLIBS} \
            ${datadir}/${PN} ${libdir}/${PN}/* \
            ${datadir}/pixmaps ${datadir}/applications \
            ${datadir}/idl ${datadir}/omf ${datadir}/sounds \
            ${libdir}/bonobo/servers"

FILES_${PN}-dev += "${bindir}/*-config"
FILES_${PN}-utils = "${bindir}/xmllint ${bindir}/xmlcatalog ${libdir}/*.sh"
