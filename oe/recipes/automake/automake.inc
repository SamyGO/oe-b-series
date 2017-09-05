DESCRIPTION = "A tool for automatically generating Makefiles."
LICENSE = "GPL"
HOMEPAGE = "http://www.gnu.org/software/automake/"
SECTION = "devel"
DEPENDS_virtclass-native = "autoconf-native perl-native"
RDEPENDS_automake-native = "autoconf-native perl-native"
SRC_URI = "${GNU_MIRROR}/automake/automake-${PV}.tar.gz;name=automake"
INC_PR = "r1"
AUTOMAKE_API = "${@".".join(bb.data.getVar("PV",d,1).split(".")[0:2])}"

inherit autotools

FILES_${PN} += "${datadir}/automake* ${datadir}/aclocal*"

do_configure() {
	# We can end up patching macros, which would then mean autoreconf
	# Cheat by saying everything is up to date.
	touch ${S}/aclocal.m4 ${S}/Makefile.in ${S}/configure
	oe_runconf
}

BBCLASSEXTEND = "native"
