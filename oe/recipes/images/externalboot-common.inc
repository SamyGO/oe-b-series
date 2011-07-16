DESCRIPTION = "<description>"

PV = "0.0.1"
PR = "r0"

DEPENDS_append=" virtual/kernel "

INSTALL_PKGS = "\
	base-files base-passwd busybox kernel-modules sysvinit sysvinit-pidof libc6 libstdc++6 \
	netbase modutils-initscripts tinylogin initscripts tinylogin busybox-telnetd update-alternatives \
	e2fsprogs e2fsprogs-mke2fs util-linux-ng dosfstools tar gzip bzip2 module-init-tools-depmod ifupdown \
	modutils-collateral unzip unrar samsung-apps squashfs-tools mtools crypt-xor cksfv glibc-gconv-ibm850 \
"

RRECOMMENDS = ""

inherit image

