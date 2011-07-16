require xorg-lib-common.inc
DESCRIPTION = "X11 toolkit intrinsics library"
DEPENDS += "libsm virtual/libx11 kbproto"
PE = "1"
PR = "${INC_PR}.0"

SRC_URI[archive.md5sum] = "fb7d2aa5b24cd5fe9b238a26d88030e7"
SRC_URI[archive.sha256sum] = "70f52c81258661811c8eae86a7a6dc910d0bf84cd48aeeed85ba430ad6b2037c"

EXTRA_OECONF += "--disable-install-makestrs --disable-xkb"

#LocalChange: fix build makestrs
do_compile() {
        (
                unset CC LD CXX CCLD
                oe_runmake -C util 'XT_CFLAGS=' 'CC=${BUILD_CC}' 'CPPFLAGS=' 'CFLAGS=-D_GNU_SOURCE' 'LDFLAGS='  makestrs
        ) || exit 1
        oe_runmake
}

BBCLASSEXTEND = "native"

XORG_PN = "libXt"
