DESCRIPTION = "Export your X session on-the-fly via VNC"
HOMEPAGE = "http://www.karlrunge.com/x11vnc/"
AUTHOR = "Karl Runge"
SECTION = "x11/utils"
LICENSE = "GPL"
#LocalChange: do not depend on avahi; added avoid-pointer-conflict.patch
DEPENDS = "libxinerama openssl virtual/libx11 libxtst libxext jpeg zlib"
#DEPENDS = "libxinerama openssl virtual/libx11 libxtst libxext avahi jpeg zlib"

SRC_URI = "${SOURCEFORGE_MIRROR}/libvncserver/x11vnc-${PV}.tar.gz \
	file://avoid-pointer-conflict.patch"

inherit autotools

SRC_URI[md5sum] = "874008821a0588a73ec7fbe09b747bb0"
SRC_URI[sha256sum] = "6b960267b1f842efe5fb76b5d36fbee79ca8ea31528ee83877623e1cca0fbbe9"
