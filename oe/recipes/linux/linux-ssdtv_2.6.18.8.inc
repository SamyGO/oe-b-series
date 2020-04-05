DESCRIPTION = "Linux Kernel for Samsung TV's"
LICENSE = "GPLv2"
DEPENDS = "binutils-cross u-boot-mkimage-native fakeroot-native"

SRC_URI = "\
	${KERNELORG_MIRROR}/linux/kernel/v2.6/linux-2.6.18.tar.bz2;name=kernel \
	${SAMYGO_MIRROR}/SamyGO%20Open%20Embedded/sources/linux-patch-2.6.18.8.patch;name=patch \
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

SRC_URI[kernel.md5sum] = "296a6d150d260144639c3664d127d174"
SRC_URI[kernel.sha256sum] = "c95280ff6c5d2a17788f7cc582d23ae8a9a7ba3f202ec6e4238eaadfce7c163d"
SRC_URI[patch.md5sum] = "183ac24904495fe023249f7b14b27350"
SRC_URI[patch.sha256sum] = "3310bc6e1a1afdafdbcd0aa86482aa8b95a7e955cbe444337668f4cbce92b9f2"

S = "${WORKDIR}/linux-2.6.18"

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
