require xorg-lib-common.inc
DESCRIPTION = "FreeType-based font drawing library for X"
DEPENDS += "libxrender freetype fontconfig"
PE = "1"
PR = "${INC_PR}.0"

SRC_URI += "file://autotools.patch"
SRC_URI[archive.md5sum] = "254e62a233491e0e1251636536163e20"
SRC_URI[archive.sha256sum] = "700e9d594b81cad3dfd5fac4a5cfd0c4cf7780c812507ef04eb40139ebf5175e"

FILES_${PN} = "${libdir}/lib*${SOLIBS}"
FILES_${PN}-dev = "${includedir} ${libdir}/lib*${SOLIBSDEV} ${libdir}/*.la \
                ${libdir}/*.a ${libdir}/pkgconfig \
                ${datadir}/aclocal ${bindir} ${sbindir}"

python do_package() {
        if bb.data.getVar('DEBIAN_NAMES', d, 1):
            bb.data.setVar('PKG_${PN}', 'libxft2', d)
        bb.build.exec_func('package_do_package', d)
}

XORG_PN = "libXft"
