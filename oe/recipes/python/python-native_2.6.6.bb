require python.inc
#MobiAqua: disabled some libs, added gzip-native
#DEPENDS = "openssl-native bzip2-full-native zlib-native readline-native sqlite3-native"
DEPENDS = "zlib-native gzip-native"
PR = "${INC_PR}.0"

FILESPATHPKG .= ":python-${PV}:python"
SRC_URI = "http://www.python.org/ftp/python/${PV}/Python-${PV}.tar.bz2 \
           file://00-fix-parallel-make.patch \
           file://04-default-is-optimized.patch \
           file://05-enable-ctypes-cross-build.patch \
           file://06-ctypes-libffi-fix-configure.patch \
           file://10-distutils-fix-swig-parameter.patch \
           file://11-distutils-never-modify-shebang-line.patch \
           file://12-distutils-prefix-is-inside-staging-area.patch \
           file://debug.patch \
           file://nohostlibs.patch"
SRC_URI[md5sum] = "cf4e6881bb84a7ce6089e4a307f71f14"
SRC_URI[sha256sum] = "134c5e0736bae2e5570d0b915693374f11108ded63c35a23a35d282737d2ce83"

S = "${WORKDIR}/Python-${PV}"

inherit native

EXTRA_OECONF_append = '\
  --enable-unicode=ucs4 \
'

EXTRA_OEMAKE = '\
  BUILD_SYS="" \
  HOST_SYS="" \
  LIBC="" \
  STAGING_LIBDIR=${STAGING_LIBDIR_NATIVE} \
  STAGING_INCDIR=${STAGING_INCDIR_NATIVE} \
'

do_install() {
	oe_runmake 'DESTDIR=${D}' install
	install -d ${D}${bindir}/
	install -m 0755 Parser/pgen ${D}${bindir}/

	# Make sure we use /usr/bin/env python
	for PYTHSCRIPT in `grep -rIl ${bindir}/python ${D}${bindir}`; do
		sed -i -e '1s|^#!.*|#!/usr/bin/env python|' $PYTHSCRIPT
	done
}
