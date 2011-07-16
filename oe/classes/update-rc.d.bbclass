DEPENDS_append = " update-rc.d update-rc.d-native"
RDEPENDS_${PN}_append = " ${@base_conditional("ONLINE_PACKAGE_MANAGEMENT", "none", "", "update-rc.d", d)}"

INITSCRIPT_PARAMS ?= "defaults"

INIT_D_DIR = "${sysconfdir}/init.d"

updatercd_postinst() {
if test "x$D" != "x"; then
	OPT="-r $D"
else
	OPT="-s"
fi
update-rc.d $OPT ${INITSCRIPT_NAME} ${INITSCRIPT_PARAMS}
}

updatercd_prerm() {
if test "x$D" = "x"; then
	if test "$1" = "upgrade" -o "$1" = "remove"; then
		${INIT_D_DIR}/${INITSCRIPT_NAME} stop
	fi
fi
}

# Note: to be Debian compliant, we should only invoke update-rc.d remove
# at the "purge" step, but opkg does not support it. So instead we also
# run it at the "remove" step if the init script no longer exists.

updatercd_postrm() {
if test "x$D" != "x"; then
	OPT="-r $D"
else
	OPT=""
fi
if test "$1" = "remove" -o "$1" = "purge"; then
	if ! test -e "${INIT_D_DIR}/${INITSCRIPT_NAME}"; then
		update-rc.d $OPT ${INITSCRIPT_NAME} remove
	fi
fi
}


def update_rc_after_parse(d):
    if bb.data.getVar('INITSCRIPT_PACKAGES', d) == None:
        if bb.data.getVar('INITSCRIPT_NAME', d) == None:
            raise bb.build.FuncFailed, "%s inherits update-rc.d but doesn't set INITSCRIPT_NAME" % bb.data.getVar('FILE', d)
        if bb.data.getVar('INITSCRIPT_PARAMS', d) == None:
            raise bb.build.FuncFailed, "%s inherits update-rc.d but doesn't set INITSCRIPT_PARAMS" % bb.data.getVar('FILE', d)

python __anonymous() {
    update_rc_after_parse(d)
}

python populate_packages_prepend () {
	def update_rcd_package(pkg):
		bb.debug(1, 'adding update-rc.d calls to postinst/postrm for %s' % pkg)
		localdata = bb.data.createCopy(d)
		overrides = bb.data.getVar("OVERRIDES", localdata, 1)
		bb.data.setVar("OVERRIDES", "%s:%s" % (pkg, overrides), localdata)
		bb.data.update_data(localdata)

		postinst = '#!/bin/sh\n'
		postinst += bb.data.getVar('updatercd_postinst', localdata, 1)
		try:
			postinst += bb.data.getVar('pkg_postinst', localdata, 1)
		except:
			pass
		bb.data.setVar('pkg_postinst_%s' % pkg, postinst, d)
		prerm = bb.data.getVar('pkg_prerm', localdata, 1)
		if not prerm:
			prerm = '#!/bin/sh\n'
		prerm += bb.data.getVar('updatercd_prerm', localdata, 1)
		bb.data.setVar('pkg_prerm_%s' % pkg, prerm, d)
	        postrm = bb.data.getVar('pkg_postrm', localdata, 1)
	        if not postrm:
	                postrm = '#!/bin/sh\n'
                postrm += bb.data.getVar('updatercd_postrm', localdata, 1)
		bb.data.setVar('pkg_postrm_%s' % pkg, postrm, d)

	pkgs = bb.data.getVar('INITSCRIPT_PACKAGES', d, 1)
	if pkgs == None:
		pkgs = bb.data.getVar('PN', d, 1)
		packages = (bb.data.getVar('PACKAGES', d, 1) or "").split()
		if not pkgs in packages and packages != []:
			pkgs = packages[0]
	for pkg in pkgs.split():
		update_rcd_package(pkg)
}
