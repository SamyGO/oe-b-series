require xorg-proto-common.inc
PE = "1"
PR = "${INC_PR}.0"

SRC_URI[archive.md5sum] = "d30c5dbf19ca6dffcd9788227ecff8c5"
SRC_URI[archive.sha256sum] = "4864e12d3c5a99b0a9ee4704822455299345e6c65b23c688a4e4bf11481107bd"

BBCLASSEXTEND = "native nativesdk sdk"
