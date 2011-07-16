require gcc-common.inc

DEPENDS = "mpfr gmp"
NATIVEDEPS = "mpfr-native gmp-native"

INC_PR = "r0"

S = "${WORKDIR}/gcc-4.2.0"

SRC_URI = "${GNU_MIRROR}/gcc/gcc-4.2.0/gcc-4.2.0.tar.bz2 \
	file://300-libstdc++-pic.patch \
	file://304-index_macro.patch \
	file://305-libmudflap-susv3-legacy.patch \
	file://307-locale_facets.patch \
	file://402-libbackend_dep_gcov-iov.h.patch \
	file://602-sdk-libstdc++-includes.patch \
	file://800-arm-bigendian.patch \
	file://904-flatten-switch-stmt-00.patch \
	file://arm-nolibfloat.patch \
	file://arm-softfloat.patch \
	file://gcc41-configure.in.patch \
	file://arm-thumb.patch \
	file://arm-thumb-cache.patch \
	file://zecke-xgcc-cpp.patch \
	file://cache-amnesia.patch \
	file://pr34130.patch \
	file://Makefile.in.patch \
"

SRC_URI[md5sum] = "4798c23548dc791ea12a139e18940684"
SRC_URI[sha256sum] = "7b6c56ec37e52d24745a07bcf37e416b22141b0d0f1e80f71f9b1fe375e83268"

# Language Overrides
FORTRAN = ""
JAVA = ""

EXTRA_OECONF_BASE = "--disable-libssp --disable-bootstrap --disable-libgomp --disable-libmudflap"
EXTRA_OECONF_INITIAL = "--disable-libmudflap --disable-libgomp --disable-libssp"
EXTRA_OECONF_INTERMEDIATE = "--disable-libmudflap --disable-libgomp --disable-libssp"

ARM_INSTRUCTION_SET = "arm"

BINV = "4.2.0"
