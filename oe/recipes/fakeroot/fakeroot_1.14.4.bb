DESCRIPTION = "Gives a fake root environment"
HOMEPAGE = "http://fakeroot.alioth.debian.org/"
SECTION = "base"
LICENSE = "GPL"
# fakeroot needs getopt which is provided by the util-linux package
RDEPENDS = "util-linux"
PR = "r2"

#LocalChange: updated configure-libtool.patch
SRC_URI = "${DEBIAN_MIRROR}/main/f/fakeroot/fakeroot_${PV}.orig.tar.bz2 \
           file://configure-libtool.patch \
           file://fix-macosx.diff"

SRC_URI[md5sum] = "bea628be77838aaa7323a2f7601c2d7e"
SRC_URI[sha256sum] = "3236394b2f280637bc977515e46e66cf999e1db74ea7402048e64113b70b9660"

inherit autotools

do_stage() {
        install -d ${STAGING_INCDIR}/fakeroot
        install -m 644 *.h ${STAGING_INCDIR}/fakeroot
        autotools_stage_all
}

do_configure_prepend() {
	./bootstrap
}
