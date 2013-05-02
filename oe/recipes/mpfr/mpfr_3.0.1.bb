require mpfr.inc

DEPENDS = "gmp"
S = "${WORKDIR}/mpfr-${PV}"
NATIVE_INSTALL_WORKS = "1"
PR = "${INC_PR}.1"

#MobiAqua: fixed p1.patch
SRC_URI = "http://www.mpfr.org/mpfr-${PV}/mpfr-${PV}.tar.bz2 \
           file://p1.patch"

# fix build in thumb mode for armv4t
SRC_URI_append_thumb = " file://long-long-thumb.patch"

EXTRA_OECONF_append_virtclass-native = " --enable-static"

#MobiAqua: added DYLD_LIBRARY_PATH path for conftest with gmp library
do_configure_prepend_build-darwin () {
    export DYLD_LIBRARY_PATH="${DYLD_LIBRARY_PATH}:${STAGING_LIBDIR}"
}

SRC_URI[md5sum] = "bfbecb2eacb6d48432ead5cfc3f7390a"
SRC_URI[sha256sum] = "e1977099bb494319c0f0c1f85759050c418a56884e9c6cef1c540b9b13e38e7f"
