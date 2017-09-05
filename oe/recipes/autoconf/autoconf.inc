SUMMARY = "A GNU tool that procude shell scripts to automatically configure software"
DESCRIPTION = "Autoconf is an extensible package of M4 macros that produce shell scripts to automatically \ 
configure software source code packages. Autoconf creates a configuration script for a package from a template \
file that lists the operating system features that the package can use, in the form of M4 macro calls."
LICENSE = "GPLv3"
HOMEPAGE = "http://www.gnu.org/software/autoconf/"
SECTION = "devel"
DEPENDS += "m4-native"
DEPENDS_class-native = "m4-native gnu-config-native"
RDEPENDS_${PN}_class-native = "m4-native gnu-config-native"

SRC_URI = "${GNU_MIRROR}/autoconf/autoconf-${PV}.tar.gz \
	   file://program_prefix.patch"

inherit autotools texinfo

CACHED_CONFIGUREVARS += "ac_cv_path_PERL=${USRBINPATH}/perl"

do_configure() {
	oe_runconf
}

do_install_append() {
    rm -rf ${D}${datadir}/emacs
}
