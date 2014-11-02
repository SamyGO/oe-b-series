require coreutils-${PV}.inc
require coreutils-native.inc

PR = "r0"

SRC_URI += "file://fix-osx-stpncpy.patch \
            file://fix-gets-stdio.patch \
            "
