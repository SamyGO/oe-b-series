require xorg-proto-common.inc
PE = "1"
PR = "${INC_PR}.0"

SRC_URI[archive.md5sum] = "0f7acbc14a082f9ae03744396527d23d"
SRC_URI[archive.sha256sum] = "472f57f7928ab20a1303a25982c4091db9674c2729bbd692c9a7204e23ea1af4"

BBCLASSEXTEND = "native nativesdk sdk"
