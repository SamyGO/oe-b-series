require xorg-proto-common.inc
PE = "1"
PR = "${INC_PR}.0"

SRC_URI[archive.md5sum] = "a5c244c36382b0de39b2828cea4b651d"
SRC_URI[archive.sha256sum] = "d93ca3c0ae710a45da6a27e1eeadfb3c9d4aee47f23657c996e1124c0d9985ca"

BBCLASSEXTEND = "nativesdk sdk"

CONFLICTS = "randrext"
