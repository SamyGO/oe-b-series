require scummvm-cl.inc

S = "${WORKDIR}/scummvm-${PV}"

FILESPATHPKG_prepend = "scummvm-${PV}:"

SRC_URI =+ "file://compilation_fix.patch"

SRC_URI[md5sum] = "5d173afa0fae21d455e8c20fc040eb3a"
SRC_URI[sha256sum] = "952f67fb887b9203d4db34ac1191248b29c7f767c69d11ebe5546c197afc37ed"
