DESCRIPTION = "Linux Kernel for Samsung TV's"
LICENSE = "GPLv2"
DEPENDS = "binutils-cross u-boot-mkimage-native fakeroot-native"

SRC_URI = "${KERNELORG_MIRROR}/pub/linux/kernel/v2.6/linux-${PV}.tar.bz2 \
	file://arm-mm-2.6.19.patch \
	file://rt-2.6.18.8-stripped.patch \
	file://fix_nonlinux_compile.patch \
	file://ignore-mod-magic-version.patch \
	file://selp-arm.patch \
	file://selp-core.patch \
	file://selp-disk.patch \
	file://selp-div64.patch \
	file://selp-fs.patch \
	file://selp-irq.patch \
	file://selp-mm.patch \
	file://selp-net.patch \
	file://selp-ntfs.patch \
	file://selp-scsi.patch \
	file://selp-usb.patch \
	file://selp-vfp.patch \
	file://squashfs.patch \
	file://debian.patch \
	file://gadget.patch \
	file://pegasus.patch \
	file://ssdtv-platform.patch \
"

FILESPATHPKG_prepend = "linux-ssdtv-2.6.18.8:"

SRC_URI[md5sum] = "dce47badc1faf34b355a10b97ae5d391"
SRC_URI[sha256sum] = "945b3014f8048cd87fdff90014afa4ff241f134bceafbfdbd42dba1be8df2ba8"

S = "${WORKDIR}/linux-2.6.18.8"

KERNEL_VERSION = "2.6.18.8"
inherit kernel siteinfo

COMPATIBLE_HOST = "arm.*-linux"
COMPATIBLE_MACHINE = "ssdtv"

export ARCH = "arm"
export OS = "Linux"

UBOOT_ENTRYPOINT = "0x60008000"

do_install_append() {
	oe_runmake headers_install INSTALL_HDR_PATH=${D}${exec_prefix}/src/linux-${KERNEL_VERSION} ARCH=$ARCH
}

PACKAGES =+ "kernel-headers"
FILES_kernel-headers = "${exec_prefix}/src/linux*"

KERNEL_IMAGETYPE = "uImage"
