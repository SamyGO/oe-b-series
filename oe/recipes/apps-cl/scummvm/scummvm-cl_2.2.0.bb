require scummvm-cl.inc

S = "${WORKDIR}/scummvm-${PV}"

EXTRA_OECONF += "--disable-engine=glk,sword25,bladerunner,ultima"

FILESPATHPKG_prepend = "scummvm-${PV}:"

SRC_URI[md5sum] = "046aba5930f1432a75acac2ed1aed1a0"
SRC_URI[sha256sum] = "f29d2a87bd4ca1025e55eddbfde09f9763be1b48e0a87341e39cc71fcb1be71c"
