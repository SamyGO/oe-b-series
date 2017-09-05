SUMMARY = "Zlib Compression Library"
DESCRIPTION = "Zlib is a general-purpose, patent-free, lossless data compression \
library which is used by many different programs."
HOMEPAGE = "http://zlib.net/"
SECTION = "libs"
LICENSE = "Zlib"
LIC_FILES_CHKSUM = "file://zlib.h;beginline=6;endline=23;md5=5377232268e952e9ef63bc555f7aa6c0"

SRC_URI = "${SOURCEFORGE_MIRROR}/libpng/${BPN}/${PV}/${BPN}-${PV}.tar.xz \
           file://remove.ldconfig.call.patch \
           file://Makefile-runtests.patch \
           file://ldflags-tests.patch \
           "
UPSTREAM_CHECK_URI = "http://zlib.net/"

SRC_URI[md5sum] = "85adef240c5f370b308da8c938951a68"
SRC_URI[sha256sum] = "4ff941449631ace0d4d203e3483be9dbc9da454084111f97ea0a2114e19bf066"

CFLAGS += "-D_REENTRANT"

do_configure() {
	uname=GNU ./configure --prefix=${prefix} --libdir=${libdir}
}

do_compile() {
	oe_runmake
}

do_install() {
	oe_runmake DESTDIR=${D} install
}

BBCLASSEXTEND = "native"
