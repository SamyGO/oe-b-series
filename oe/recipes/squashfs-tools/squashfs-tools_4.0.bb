
#LocalChange: remove SRC_URI, S, updated checksums to keep 4.0 version
require squashfs-tools.inc
PR = "${INC_PR}.0"

EXTRA_OEMAKE += "LZMA_SUPPORT=1 LZMA_DIR=../.."
TARGET_CC_ARCH += "${LDFLAGS}"

# the COMP_DEFAULT macro should result in a string including quotes: "gzip"
COMP_DEFAULT = gzip
CFLAGS_append = ' -I. -I../../C -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE \
 -D_GNU_SOURCE -DLZMA_SUPPORT -DCOMP_DEFAULT=\\"${COMP_DEFAULT}\\" '

SRC_URI[md5sum] = "a3c23391da4ebab0ac4a75021ddabf96"
SRC_URI[sha256sum] = "18948edbe06bac2c4307eea99bfb962643e4b82e5b7edd541b4d743748e12e21"
