DESCRIPTION = "neon is an HTTP and WebDAV client library, with a C interface."
SECTION = "libs"
LICENSE = "LGPL"
#LocalChange: do not depend on gnutls but use openssl instead
DEPENDS = "zlib libxml2 expat time openssl"

#LocalChange: use newer version, use fixed-system-target.patch
SRC_URI = "http://www.webdav.org/${PN}/${P}.tar.gz \
           file://pkgconfig.patch \
           file://fixed-system-target.patch"

inherit autotools binconfig lib_package pkgconfig

#LocalChange: do not depend on gnutls but use openssl instead
EXTRA_OECONF = "--with-libxml2 --with-expat --enable-shared"
CFLAGS_append = ' -D__USE_UNIX98'

SRC_URI[md5sum] = "516c576c0ca5c0a01ad24d018093cfee"
SRC_URI[sha256sum] = "8a29457052b73ac0139e3b2824a74323256dd7631b1691239ddb18124e231a71"
