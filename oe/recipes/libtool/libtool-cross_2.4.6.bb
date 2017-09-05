require libtool-${PV}.inc

PACKAGES = ""
SRC_URI += "file://prefix.patch"
SRC_URI += "file://fixinstall.patch"

do_configure_prepend () {
	# Remove any existing libtool m4 since old stale versions would break
	# any upgrade
	rm -f ${STAGING_DATADIR}/aclocal/libtool.m4
	rm -f ${STAGING_DATADIR}/aclocal/lt*.m4
}

do_install () {
	install -d ${D}${bindir}/
	install -m 0755 ${HOST_SYS}-libtool ${D}${bindir}/${HOST_SYS}-libtool
	sed -e 's@^\(predep_objects="\).*@\1"@' \
	    -e 's@^\(postdep_objects="\).*@\1"@' \
	    -i ${D}${bindir}/${HOST_SYS}-libtool
	sed -i '/^archive_cmds=/s/\-nostdlib//g' ${D}${bindir}/${HOST_SYS}-libtool
	sed -i '/^archive_expsym_cmds=/s/\-nostdlib//g' ${D}${bindir}/${HOST_SYS}-libtool
	GREP='/bin/grep' SED='sed' ${S}/build-aux/inline-source libtoolize > ${D}${bindir}/libtoolize
	chmod 0755 ${D}${bindir}/libtoolize
	install -d ${D}${datadir}/libtool/build-aux/
	install -d ${D}${datadir}/aclocal/
	install -c ${S}/build-aux/compile ${D}${datadir}/libtool/build-aux/
	install -c ${S}/build-aux/config.guess ${D}${datadir}/libtool/build-aux/
	install -c ${S}/build-aux/config.sub ${D}${datadir}/libtool/build-aux/
	install -c ${S}/build-aux/depcomp ${D}${datadir}/libtool/build-aux/
	install -c ${S}/build-aux/install-sh ${D}${datadir}/libtool/build-aux/
	install -c ${S}/build-aux/missing ${D}${datadir}/libtool/build-aux/
	install -c -m 0644 ${S}/build-aux/ltmain.sh ${D}${datadir}/libtool/build-aux/
	install -c -m 0644 ${S}/m4/*.m4 ${D}${datadir}/aclocal/
}

SYSROOT_PREPROCESS_FUNCS += "libtoolcross_sysroot_preprocess"

libtoolcross_sysroot_preprocess () {
	install -d ${SYSROOT_DESTDIR}${STAGING_BINDIR_CROSS}/
	install -m 755 ${D}${bindir}/${HOST_SYS}-libtool ${SYSROOT_DESTDIR}${STAGING_BINDIR_CROSS}/${HOST_SYS}-libtool
}

SYSROOT_DIRS += "${bindir} ${datadir}"

SSTATE_SCAN_FILES += "libtoolize *-libtool"
