INHIBIT_AUTOTOOLS_DEPS = "1"
require gawk_${PV}.bb

inherit native

#LocalChange: added autoconf-native, gettext-native
DEPENDS = "autoconf-native gettext-native"
PATCHTOOL = "patch"

S = "${WORKDIR}/gawk-${PV}"

do_stage() {
	install -d ${STAGING_BINDIR}
	install -m 755 gawk ${STAGING_BINDIR}
	#LocalChange:
	ln ${STAGING_BINDIR}/gawk ${STAGING_BINDIR}/awk
}
