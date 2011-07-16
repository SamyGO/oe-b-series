DESCRIPTION = "XZ Utils is free general-purpose data compression software with high compression ratio.  XZ Utils are the successor to LZMA Utils."
SECTION = "console/utils"
LICENSE = "Public Domain"
INC_PR = "r0"
S ?= "${WORKDIR}/xz-${PV}"
#LocalChange: disable assembler
EXTRA_OECONF = "--enable-shared --disable-assembler"
BBCLASSEXTEND = "native"

inherit autotools
