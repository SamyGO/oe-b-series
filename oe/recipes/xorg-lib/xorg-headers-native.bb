PR = "r2"

SRC_URI = "file://X11"

inherit native

do_install() {
        install -d ${D}${includedir}
        cp -pPfR ${WORKDIR}/X11 ${D}${includedir}
}

NATIVE_INSTALL_WORKS = "1"
