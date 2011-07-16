require mpfr.inc

DEPENDS = "gmp"
S = "${WORKDIR}/mpfr-${PV}"
NATIVE_INSTALL_WORKS = "1"
PR = "r2"
BBCLASSEXTEND = "native"

SRC_URI = "http://www.mpfr.org/mpfr-${PV}/mpfr-${PV}.tar.bz2 \
           file://p3.patch"

# fix build in thumb mode for armv4t
SRC_URI_append_thumb = " file://long-long-thumb.patch"

SRC_URI[md5sum] = "f45bac3584922c8004a10060ab1a8f9f"
SRC_URI[sha256sum] = "8f4e5f9c53536cb798a30455ac429b1f9fc75a0f8af32d6e0ac31ebf1024821f"
