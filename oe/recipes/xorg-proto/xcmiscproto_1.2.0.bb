require xorg-proto-common.inc
PE = "1"
PR = "${INC_PR}.0"

SRC_URI[archive.md5sum] = "7b83e4a7e9f4edc9c6cfb0500f4a7196"
SRC_URI[archive.sha256sum] = "de17c06b7005c5e9ab469e324e76c5c3b8baa2dfc3c1dc7e93438c197facf68e"

BBCLASSEXTEND = "native nativesdk sdk"
