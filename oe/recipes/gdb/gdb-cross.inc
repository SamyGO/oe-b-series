require gdb-common.inc

DEPENDS = "expat-native ncurses-native readline-native"

EXTRA_OECONF += "--without-python"

do_compile_prepend() {
    export BUILD_SYS="${BUILD_SYS}"
    export HOST_SYS="${HOST_SYS}"
    export STAGING_LIBDIR="${STAGING_LIBDIR_NATIVE}"
    export STAGING_INCDIR="${STAGING_INCDIR_NATIVE}"
}

#EXTRA_OEMAKE += "LDFLAGS='${BUILD_LDFLAGS}'"

GDBPROPREFIX = ""

inherit cross
inherit gettext
