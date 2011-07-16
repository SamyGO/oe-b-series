require scummvm-cl.inc

S = "${WORKDIR}/scummvm-${PV}"

SRC_URI += "file://1.3.0-fix-default-save-path.patch;apply=yes"

SRC_URI[md5sum] = "d128f2eab28e5eb11f0483ce8aed380e"
SRC_URI[sha256sum] = "694a65a16a72c1d676e09c9af11f1ba1393d2ed731b941d82a79c50e335b58af"
