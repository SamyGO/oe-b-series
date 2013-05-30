require python.inc
DEPENDS = "python-native db gdbm openssl readline sqlite3 tcl zlib\
           ${@base_contains('DISTRO_FEATURES', 'tk', 'tk', '', d)}"
DEPENDS_sharprom = "python-native db readline zlib gdbm openssl"
# set to .0 on every increase of INC_PR
PR = "${INC_PR}.4"

#LocalChange: added fixed-system.patch
SRC_URI = "\
  http://www.python.org/ftp/python/${PV}/Python-${PV}.tar.bz2 \
  file://00-fix-parallel-make.patch \
  file://01-use-proper-tools-for-cross-build.patch \
  file://02-remove-test-for-cross.patch \
  file://03-fix-tkinter-detection.patch \
  file://04-default-is-optimized.patch \
  file://05-enable-ctypes-cross-build.patch \
  file://06-ctypes-libffi-fix-configure.patch \
  file://07-linux3-regen-fix.patch \
  file://ipv6-cross.patch \
  file://python-module-rpath-fix.patch \
  file://sitecustomize.py \
  file://pkgconfig-support.patch \
  file://fixed-system.patch \
"
SRC_URI[md5sum] = "cf4e6881bb84a7ce6089e4a307f71f14"
SRC_URI[sha256sum] = "134c5e0736bae2e5570d0b915693374f11108ded63c35a23a35d282737d2ce83"

S = "${WORKDIR}/Python-${PV}"

inherit autotools

# The 3 lines below are copied from the libffi recipe, ctypes ships its own copy of the libffi sources
#Somehow gcc doesn't set __SOFTFP__ when passing -mfloatabi=softp :(
TARGET_CC_ARCH_append_armv6 = " -D__SOFTFP__"
TARGET_CC_ARCH_append_armv7a = " -D__SOFTFP__"

do_configure_prepend() {
	autoreconf -Wcross --verbose --install --force --exclude=autopoint Modules/_ctypes/libffi || oenote "_ctypes failed to autoreconf"
}

#
# Copy config.h and an appropriate Makefile for distutils.sysconfig,
# which laters uses the information out of these to compile extensions
#
do_compile_prepend() {
	install -d ${STAGING_INCDIR}/python${PYTHON_MAJMIN}/
	install -d ${STAGING_LIBDIR}/python${PYTHON_MAJMIN}/config/
	install -m 0644 pyconfig.h ${STAGING_INCDIR}/python${PYTHON_MAJMIN}/
	install -m 0644 Makefile Makefile.orig
	install -m 0644 Makefile Makefile.backup
	sed -e 's,${includedir},${STAGING_INCDIR},' < Makefile.backup > Makefile
	install -m 0644 Makefile Makefile.backup
	sed -e 's,${libdir},${STAGING_LIBDIR},' < Makefile.backup > Makefile
	install -m 0644 Makefile ${STAGING_LIBDIR}/python${PYTHON_MAJMIN}/config/
}

do_compile() {
	oe_runmake HOSTPGEN=${STAGING_BINDIR_NATIVE}/pgen \
		HOSTPYTHON=${STAGING_BINDIR_NATIVE}/python \
		STAGING_LIBDIR=${STAGING_LIBDIR} \
		STAGING_INCDIR=${STAGING_INCDIR} \
		BUILD_SYS=${BUILD_SYS} HOST_SYS=${HOST_SYS} \
		OPT="${CFLAGS}" libpython${PYTHON_MAJMIN}.so

	oe_libinstall -so libpython${PYTHON_MAJMIN} ${STAGING_LIBDIR}

	oe_runmake HOSTPGEN=${STAGING_BINDIR_NATIVE}/pgen \
		HOSTPYTHON=${STAGING_BINDIR_NATIVE}/python \
		STAGING_LIBDIR=${STAGING_LIBDIR} \
		STAGING_INCDIR=${STAGING_INCDIR} \
		BUILD_SYS=${BUILD_SYS} HOST_SYS=${HOST_SYS} \
		RUNSHARED= OPT="${CFLAGS}"
}

do_install() {
	install -m 0644 Makefile.orig Makefile
	
	oe_runmake HOSTPGEN=${STAGING_BINDIR_NATIVE}/pgen \
		HOSTPYTHON=${STAGING_BINDIR_NATIVE}/python \
		STAGING_LIBDIR=${STAGING_LIBDIR} \
		STAGING_INCDIR=${STAGING_INCDIR} \
		BUILD_SYS=${BUILD_SYS} HOST_SYS=${HOST_SYS} \
		DESTDIR=${D} LIBDIR=${libdir} RUNSHARED= install

	install -m 0644 ${WORKDIR}/sitecustomize.py ${D}/${libdir}/python${PYTHON_MAJMIN}

	# remove hardcoded ccache, see http://bugs.openembedded.net/show_bug.cgi?id=4144
	sed -i -e s,ccache,'$(CCACHE)', ${D}/${libdir}/python${PYTHON_MAJMIN}/config/Makefile
}

do_install_append() {
	# remove unecessary files from python-distutils' packages
	rm ${D}/${libdir}/python${PYTHON_MAJMIN}/config/libpython2.6.a
	rm ${D}/${libdir}/python${PYTHON_MAJMIN}/distutils/command/win*
}

require python-${PYTHON_MAJMIN}-manifest.inc

# manual dependency additions
RPROVIDES_${PN}-core = "${PN}"
RRECOMMENDS_${PN}-core = "${PN}-readline"
RRECOMMENDS_${PN}-crypt = "openssl"

# add sitecustomize
FILES_${PN}-core += "${libdir}/python${PYTHON_MAJMIN}/sitecustomize.py"
# ship 2to3
FILES_${PN}-core += "${bindir}/2to3"

# package libpython2
PACKAGES =+ "lib${PN}2"
FILES_lib${PN}2 = "${libdir}/libpython*.so.*"

# additional stuff -dev

FILES_${PN}-dev += "\
  ${includedir} \
  ${libdir}/lib*${SOLIBSDEV} \
  ${libdir}/*.la \
  ${libdir}/*.a \
  ${libdir}/*.o \
  ${libdir}/pkgconfig \
  ${base_libdir}/*.a \
  ${base_libdir}/*.o \
  ${datadir}/aclocal \
  ${datadir}/pkgconfig \
"

# catch debug extensions (isn't that already in python-core-dbg?)
FILES_${PN}-dbg += "${libdir}/python${PYTHON_MAJMIN}/lib-dynload/.debug"

# catch all the rest (unsorted)
PACKAGES += "${PN}-misc"
FILES_${PN}-misc = "${libdir}/python${PYTHON_MAJMIN}"

# catch manpage
PACKAGES += "${PN}-man"
FILES_${PN}-man = "${datadir}/man"
