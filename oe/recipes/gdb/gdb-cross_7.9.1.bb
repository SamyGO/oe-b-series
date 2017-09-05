require gdb-cross.inc

SRC_URI += "file://0001-make-man-install-relative-to-DESTDIR.patch"

PR = "${INC_PR}.0"

S = "${WORKDIR}/${BPN}-${PV}"
