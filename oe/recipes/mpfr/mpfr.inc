DESCRIPTION = "A C library for multiple-precision floating-point computations with exact rounding"
HOMEPAGE = "http://www.mpfr.org/"
LICENSE = "GPL LGPL"
SECTION = "libs"
BBCLASSEXTEND = "native nativesdk sdk"
INC_PR = "r3"

inherit autotools

do_fixup() {
	if [ `uname -s` == "Darwin" ]; then
		rm ${S}/PATCHES || true
	fi
}

addtask fixup after do_unpack before do_patch
