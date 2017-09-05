DESCRIPTION = "The GNU internationalization library."
HOMEPAGE = "http://www.gnu.org/software/gettext/gettext.html"
SECTION = "libs"
LICENSE = "GPLv3"
PR = "r6"
DEPENDS = "libxml2 gettext-native virtual/libiconv ncurses expat"
DEPENDS_virtclass-native = "libxml2-native"
PROVIDES = "virtual/libintl"
PROVIDES_virtclass-native = "virtual/libintl-native"
RCONFLICTS_gettext-libintl = "proxy-libintl"

BBCLASSEXTEND = "native nativesdk"

SRC_URI = "${GNU_MIRROR}/gettext/gettext-${PV}.tar.gz \
	   file://parallel.patch \
	  "

SRC_URI_append_libc-uclibc = " file://gettext-error_print_progname.patch"

nolargefile = "${@base_contains('DISTRO_FEATURES', 'largefile', '', '-DNO_LARGEFILE_SOURCE', d)}"
EXTRA_OEMAKE_append_libc-uclibc = "'CFLAGS=${CFLAGS} ${nolargefile}'"

PARALLEL_MAKE = ""

inherit autotools

NATIVECONF = "--disable-rpath"
#MobiAqua: removed "--enable-relocatable", added "--with-included-gettext --enable-nls"
NATIVECONF_virtclass-native += "--disable-curses --with-included-gettext --enable-nls"

EXTRA_OECONF += "--without-lispdir \
		 --disable-csharp \
		 --disable-libasprintf \
		 --disable-java \
		 --disable-native-java \
		 --disable-openmp \
		 --disable-acl \
		 --with-included-glib \
		 --without-emacs \
		 --without-cvs \
		 --without-git \
		 --with-included-libcroco \
		 ${NATIVECONF} \
	        "

acpaths = '-I ${S}/gnulib-local/m4/ \
	   -I ${S}/gettext-runtime/m4 \
	   -I ${S}/gettext-tools/m4'


# these lack the .x behind the .so, but shouldn't be in the -dev package
# Otherwise you get the following results:
# 7.4M    glibc/images/ep93xx/Angstrom-console-image-glibc-ipk-2008.1-test-20080104-ep93xx.rootfs.tar.gz
# 25M     uclibc/images/ep93xx/Angstrom-console-image-uclibc-ipk-2008.1-test-20080104-ep93xx.rootfs.tar.gz
# because gettext depends on gettext-dev, which pulls in more -dev packages:
# 15228   KiB /ep93xx/libstdc++-dev_4.2.2-r2_ep93xx.ipk
# 1300    KiB /ep93xx/uclibc-dev_0.9.29-r8_ep93xx.ipk
# 140     KiB /armv4t/gettext-dev_0.14.1-r6_armv4t.ipk
# 4       KiB /ep93xx/libgcc-s-dev_4.2.2-r2_ep93xx.ipk

PACKAGES =+ "gettext-libintl libgettextlib libgettextsrc"

FILES_gettext-libintl = "${libdir}/libintl*.so.*"
FILES_libgettextlib = "${libdir}/libgettextlib-*.so*"
FILES_libgettextsrc = "${libdir}/libgettextsrc-*.so*"

SRC_URI[md5sum] = "0c86e5af70c195ab8bd651d17d783928"
SRC_URI[sha256sum] = "516a6370b3b3f46e2fc5a5e222ff5ecd76f3089bc956a7587a6e4f89de17714c"
