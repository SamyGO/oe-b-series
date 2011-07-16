#LocalChange: keep old support

require gzip_${PV}.bb
inherit native

do_stage() {
	install -m 755 gzip ${STAGING_BINDIR}
}

do_install() {
	true
}
