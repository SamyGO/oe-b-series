DESCRIPTION = "GNU C Library"
SECTION = "libs"
PRIORITY = "required"
LICENSE = "LGPL"
INC_PR = "r21"
# nptl needs unwind support in gcc, which can't be built without glibc.
DEPENDS = "virtual/${TARGET_PREFIX}gcc-intermediate linux-libc-headers"
#this leads to circular deps, so lets not add it yet
#RDEPENDS_ldd += " bash"
# nptl needs libgcc but dlopens it, so our shlibs code doesn't detect this
#RDEPENDS_${PN} += "${@['','libgcc']['nptl' in '${GLIBC_ADDONS}']}"
PROVIDES = "virtual/libc virtual/${TARGET_PREFIX}libc-for-gcc"
PROVIDES += "virtual/libintl virtual/libiconv"
PACKAGES_DYNAMIC = "libc6*"
RPROVIDES_${PN}-dev = "libc6-dev virtual-libc-dev"
PROVIDES_${PN}-dbg = "glibc-dbg"

inherit autotools
require glibc-options.inc

LEAD_SONAME = "libc.so"

GLIBC_EXTRA_OECONF ?= ""
INHIBIT_DEFAULT_DEPS = "1"

ARM_INSTRUCTION_SET = "arm"
# PARALLEL_MAKE into PARALLELMFLAGS and empty out PARALLEL_MAKE
EXTRA_OEMAKE := "PARALLELMFLAGS="${PARALLEL_MAKE}""
PARALLEL_MAKE = ""

GLIBC_EXTRA_OECONF += "${@get_libc_fpu_setting(bb, d)}"

OE_FEATURES := "${@features_to_glibc_settings(d)}"
do_configure_prepend() {
	echo '${OE_FEATURES}' > ${B}/option-groups.config
}

# Work around issues with pstage package install order and intermediate steps
# in the toolchain build.
do_setscene[deptask] = "do_setscene"
