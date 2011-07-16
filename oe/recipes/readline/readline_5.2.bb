DESCRIPTION = "The GNU Readline library provides a set of functions for use by applications that allow users to edit \
command lines as they are typed in. Both Emacs and vi editing modes are available. The Readline library includes  \
additional functions to maintain a list of previously-entered command lines, to recall and perhaps reedit those   \
lines, and perform csh-like history expansion on previous commands."
SECTION = "libs"
PRIORITY = "optional"
LICENSE = "GPLv2"
DEPENDS += "ncurses"
RPROVIDES_${PN} += "readline"
LEAD_SONAME = "libreadline.so"
PR = "r6"

SRC_URI = "\
  ftp://ftp.gnu.org/gnu/readline/readline-${PV}.tar.gz \
  file://fix-includes.patch \
  file://configure_fix.patch \
  file://acinclude.m4 \
"
S = "${WORKDIR}/readline-${PV}"

inherit autotools

do_configure () {
	install -m 0644 ${WORKDIR}/acinclude.m4 ${S}/
	autotools_do_configure
}

do_install () {
	autotools_do_install
	# Make install doesn't properly install these
	oe_libinstall -so -C shlib libhistory ${D}${libdir}
	oe_libinstall -so -C shlib libreadline ${D}${libdir}
}
NATIVE_INSTALL_WORKS = 1
BBCLASSEXTEND = "native"


SRC_URI[md5sum] = "e39331f32ad14009b9ff49cc10c5e751"
SRC_URI[sha256sum] = "12e88d96aee2cd1192500356f0535540db499282ca7f76339fb4228c31249f45"
