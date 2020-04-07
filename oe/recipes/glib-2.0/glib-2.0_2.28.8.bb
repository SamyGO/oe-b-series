DESCRIPTION = "GLib is a general-purpose utility library, \
which provides many useful data types, macros, \
type conversions, string utilities, file utilities, a main \
loop abstraction, and so on. It works on many \
UNIX-like platforms, Windows, OS/2 and BeOS."
LICENSE = "LGPLv2+"
SECTION = "libs"
PRIORITY = "optional"
#MobiAqua: added gettext
DEPENDS = "gettext glib-2.0-native gtk-doc zlib"
DEPENDS_virtclass-native = "gettext-native gtk-doc-native \
                            pkgconfig-native"

PR = "r2"

SRC_URI = "${GNOME_MIRROR}/glib/2.28/glib-${PV}.tar.bz2 \
           file://configure-libtool.patch \
           file://60_wait-longer-for-threads-to-die.patch \
           file://g_once_init_enter.patch \
           file://0003-gatomic-proper-pointer-get-cast.patch.patch \
           file://0005-glib-mkenums-interpreter.patch.patch \
          "
SRC_URI[md5sum] = "789e7520f71c6a4bf08bc683ec764d24"
SRC_URI[sha256sum] = "222f3055d6c413417b50901008c654865e5a311c73f0ae918b0a9978d1f9466f"

EXTRA_OECONF_append = " --enable-dtrace=no"

noipv6 = "${@base_contains('DISTRO_FEATURES', 'ipv6', '', '-DDISABLE_IPV6', d)}"
EXTRA_OEMAKE_append = "'CFLAGS=${CFLAGS} ${noipv6}'"

SRC_URI[archive.md5sum] = "6a7db81c9a2cffe6a34dadb57d7ba2d2"
SRC_URI[archive.sha256sum] = "014c3da960bf17117371075c16495f05f36501db990851ceea658f15d2ea6d04"

inherit autotools

S = "${WORKDIR}/glib-${PV}"

EXTRA_OECONF = "--disable-debug "

# Add and entry for your favourite arch if your (g)libc has a sane printf
EXTRA_OECONF_append_glibc_arm = "  --enable-included-printf=no "

do_install_append() {
	sed -i -e s:${STAGING_BINDIR_NATIVE}:${bindir}:g ${D}${bindir}/glib-mkenums || true
}

EXTRA_OECONF_virtclass-native = ""

do_configure_prepend_virtclass-native() {
    if [ -e ${S}/${TARGET_SYS}-libtool ] ; then
                echo "${TARGET_SYS}-libtool already present"
    else
        cp ${STAGING_BINDIR}/${TARGET_SYS}-libtool ${S}
    fi

}

BBCLASSEXTEND = "native"

PACKAGES =+ "gobject-2.0 gmodule-2.0 gthread-2.0 gio-2.0 glib-2.0-utils "
LEAD_SONAME = "libglib-2.0.*"
FILES_glib-2.0-utils = "${bindir}/*"
FILES_${PN} = "${libdir}/lib*so.* ${libdir}/gio/modules/*.so"
FILES_${PN}-dev += "${libdir}/glib-2.0 ${datadir}/glib-2.0 ${libdir}/gio/modules/*.la"
FILES_${PN}-dbg += "${libdir}/gio/modules/.debug"
FILES_gmodule-2.0 = "${libdir}/libgmodule-2.0.so.*"
FILES_gobject-2.0 = "${libdir}/libgobject-2.0.so.*"
FILES_gio-2.0 = "${libdir}/libgio-2.0.so.*"
FILES_gthread-2.0 = "${libdir}/libgthread-2.0.so.*"

# Let various glib components end up in glib package
# for compatibility (with binary packages from Maemo).
FILES_gthread-2.0_chinook-compat = ""
FILES_gmodule-2.0_chinook-compat = ""
FILES_gobject-2.0_chinook-compat = ""
FILES_gio-2.0_chinook-compat = ""
