
require externalboot-common.inc

IMAGE_FSTYPES = "tar.gz"
IMAGE_BASENAME = "externalboot-base"
IMAGE_LINGUAS = ""
IMAGE_INSTALL = "${INSTALL_PKGS} "

ROOTFS_POSTPROCESS_COMMAND += "rm -f ${IMAGE_ROOTFS}/boot/*;${MA_ROOTFS_POSTPROCESS};"
