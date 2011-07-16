DESCRIPTION = "The Subversion (svn) client"
SECTION = "console/network"
DEPENDS = "apr-util neon sqlite3"
RDEPENDS_${PN} = "neon"
LICENSE = "Apache BSD"
HOMEPAGE = "http://subversion.tigris.org/"

PR = "r1"

SRC_URI = "http://subversion.tigris.org/downloads/${P}.tar.bz2 \
	   file://disable-revision-install.patch"

EXTRA_OECONF = "--without-berkeley-db --without-apxs --without-apache \
                --without-swig --with-apr=${STAGING_BINDIR_CROSS} \
                --with-apr-util=${STAGING_BINDIR_CROSS}"


inherit autotools

acpaths = "-I build/ac-macros"

# FIXME: Ugly hack!
do_configure_append() {
	if ! test -f libtool ; then cp -a *-libtool libtool ; fi
}

SRC_URI[md5sum] = "1a53a0e72bee0bf814f4da83a9b6a636"
SRC_URI[sha256sum] = "64331bda459e984b8d369b449eec89daa2f3cd288186f1d2a9ad8011badd4dad"
