DESCRIPTION = "Common X11 Keyboard layouts"
LICENSE = "MIT"
#LocalChange: added glib-2.0
DEPENDS = "intltool xkbcomp-native glib-2.0"
RDEPENDS_${PN} = "xkbcomp"
PR = "r5"

SRC_URI = "http://xlibs.freedesktop.org/xkbdesc/xkeyboard-config-${PV}.tar.bz2 \
           file://abnt2-fixes.patch"

inherit autotools

do_install_append () {
    install -d ${D}/usr/share/X11/xkb/compiled
    cd ${D}${datadir}/X11/xkb/rules && ln -sf base xorg
}

FILES_${PN} += "${datadir}/X11/xkb"

SRC_URI[md5sum] = "a9fe7efbc67a6966c4d4501f0cf88073"
SRC_URI[sha256sum] = "921a857dcf90a59df7feb26da5aabcf0bbfb749c46e2a46c3bc7a0280b83b0e1"
