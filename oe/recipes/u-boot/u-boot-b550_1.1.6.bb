require u-boot_1.1.6.bb

DEFAULT_PREFERENCE = "-1"

SRC_URI += "file://b550.patch "

S = ${WORKDIR}/u-boot-1.1.6/

PROVIDES = ""
