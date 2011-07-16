require linux-libc-headers.inc

INHIBIT_DEFAULT_DEPS = "1"
DEPENDS += "unifdef-native"
PR = "r0"

COMPATIBLE_TARGET_SYS = "."

SRC_URI = "${KERNELORG_MIRROR}/pub/linux/kernel/v2.6/linux-2.6.18.8.tar.bz2 \
           file://arm-syscall-define.patch"

S = "${WORKDIR}/linux-2.6.18.8"

SRC_URI[md5sum] = "dce47badc1faf34b355a10b97ae5d391"
SRC_URI[sha256sum] = "945b3014f8048cd87fdff90014afa4ff241f134bceafbfdbd42dba1be8df2ba8"

do_configure() {
	oe_runmake allnoconfig ARCH=${ARCH}
}

do_compile () {
}

do_install() {
	oe_runmake headers_install INSTALL_HDR_PATH=${D}${exec_prefix} ARCH=${ARCH}
	#LocalChange: remove includes conflict with libc6
	rm -rf ${D}${exec_prefix}/include/scsi
}

do_install_append_arm() {
	cp include/asm-arm/procinfo.h ${D}${includedir}/asm
}

