PV = "5.0.2"
require gmp-native.inc
PR = "${INC_PR}.1"

SRC_URI[gmp.md5sum] = "0bbaedc82fb30315b06b1588b9077cd3"
SRC_URI[gmp.sha256sum] = "dbc2db76fdd4e99f85d5e35aa378ed62c283e0d586b91bd8703aff75a7804c28"

#MobiAqua: added patches from MacPorts: patch-config.guess.i7.diff, patch-gmp-h.in.diff
SRC_URI += " \
	   file://patch-config.guess.i7.diff;striplevel=0 \
	   file://patch-gmp-h.in.diff;striplevel=0"

LICENSE = "GPLv3 LGPLv3"
