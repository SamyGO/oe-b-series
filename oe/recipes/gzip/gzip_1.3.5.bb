#LocalChange: keep old support
LICENSE = "GPL"
SECTION = "console/utils"
PRIORITY = "required"
DESCRIPTION = "gzip (GNU zip) is a compression utility designed \
to be a replacement for 'compress'. The GNU Project uses it as \
the standard compression program for its system."
PR = "r1"

SRC_URI = "${DEBIAN_MIRROR}/main/g/gzip/gzip_${PV}.orig.tar.gz \
	   file://configure.patch"

S = "${WORKDIR}/gzip-${PV}"

inherit autotools

do_install () {
	autotools_do_install
	# Rename and move files into /bin (FHS)
	install -d ${D}${base_bindir}
	mv ${D}${bindir}/gunzip ${D}${base_bindir}/gunzip.${PN}
	mv ${D}${bindir}/gzip ${D}${base_bindir}/gzip.${PN}
	mv ${D}${bindir}/zcat ${D}${base_bindir}/zcat.${PN}
}

pkg_postinst_${PN} () {
	update-alternatives --install ${base_bindir}/gunzip gunzip gunzip.${PN} 100
	update-alternatives --install ${base_bindir}/gzip gzip gzip.${PN} 100
	update-alternatives --install ${base_bindir}/zcat zcat zcat.${PN} 100
}

pkg_prerm_${PN} () {
	update-alternatives --remove gunzip gunzip.${PN}
	update-alternatives --remove gzip gzip.${PN}
	update-alternatives --remove zcat zcat.${PN}
}

SRC_URI[md5sum] = "3d6c191dfd2bf307014b421c12dc8469"
SRC_URI[sha256sum] = "631820e566353eafc4bdc0d9d8221c26c7ef6b5d10a254783dbe9bcac88caa07"
