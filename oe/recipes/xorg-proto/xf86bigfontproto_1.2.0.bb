require xorg-proto-common.inc
PE = "1"
PR = "${INC_PR}.0"

SRC_URI[archive.md5sum] = "120e226ede5a4687b25dd357cc9b8efe"
SRC_URI[archive.sha256sum] = "ba9220e2c4475f5ed2ddaa7287426b30089e4d29bd58d35fad57ba5ea43e1648"

BBCLASSEXTEND = "native nativesdk sdk"
