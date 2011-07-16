SECTION = "base"
PRIORITY = "standard"
DESCRIPTION = "Manage symlinks in /etc/rcN.d"
LICENSE = "GPL"
S = "${WORKDIR}/update-rc.d"
INHIBIT_DEFAULT_DEPS = "1"
PR = "r1"

BBCLASSEXTEND = "native"

SRC_URI = "${HANDHELDS_CVS};module=apps/update-rc.d;tag=r0_7 \
           file://add-verbose.patch"

PACKAGE_ARCH = "all"

do_compile() {
}

do_stage() {
	install -m 0755 ${S}/update-rc.d ${STAGING_BINDIR_NATIVE}/
}

do_install() {
	install -d ${D}${sbindir}
	install -m 0755 ${S}/update-rc.d ${D}${sbindir}/update-rc.d
}

NATIVE_INSTALL_WORKS = "1"
