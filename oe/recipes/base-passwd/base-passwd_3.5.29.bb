SUMMARY = "Base system master password/group files"
DESCRIPTION = "The master copies of the user database files (/etc/passwd and /etc/group).  The update-passwd tool is also provided to keep the system databases synchronized with these master files."
SECTION = "base"
LICENSE = "GPLv2+"
LIC_FILES_CHKSUM = "file://COPYING;md5=eb723b61539feef013de476e68b5c50a"

SRC_URI = "https://launchpad.net/debian/+archive/primary/+files/${BPN}_${PV}.tar.gz \
           file://add_shutdown.patch \
           file://nobash.patch \
           file://noshadow.patch \
           file://input.patch \
           file://disable-docs.patch \
          "

SRC_URI[md5sum] = "6beccac48083fe8ae5048acd062e5421"
SRC_URI[sha256sum] = "f0b66388b2c8e49c15692439d2bee63bcdd4bbbf7a782c7f64accc55986b6a36"

inherit autotools

do_install () {
	install -d -m 755 ${D}${sbindir}
	install -p -m 755 ${B}/update-passwd ${D}${sbindir}/
	install -d -m 755 ${D}${datadir}/base-passwd
	install -p -m 644 ${S}/passwd.master ${D}${datadir}/base-passwd/
	sed -i 's#:/root:#:${ROOT_HOME}:#' ${D}${datadir}/base-passwd/passwd.master
	install -p -m 644 ${S}/group.master ${D}${datadir}/base-passwd/
	#MobiAqua: added defined custom root passwd
	sed -i -e s,root::0:0:root:,root:${MA_ROOT_PASSWORD}:0:0:root:, ${D}${datadir}/base-passwd/passwd.master
	install -d -m 755 ${D}${sysconfdir}
	install -p -m 644 ${D}${datadir}/base-passwd/passwd.master ${D}${sysconfdir}/passwd
	install -p -m 644 ${D}${datadir}/base-passwd/group.master ${D}${sysconfdir}/group
}
