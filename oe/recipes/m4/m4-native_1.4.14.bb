require m4_${PV}.bb
inherit native

INHIBIT_AUTOTOOLS_DEPS = "1"
DEPENDS += "gnu-config-native"

do_configure ()  {
	install -m 0644 ${STAGING_DATADIR_NATIVE}/gnu-config/config.sub .
	install -m 0644 ${STAGING_DATADIR_NATIVE}/gnu-config/config.guess .
	oe_runconf
}
