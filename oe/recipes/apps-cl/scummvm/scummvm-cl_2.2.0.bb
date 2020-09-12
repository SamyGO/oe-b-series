require scummvm-cl.inc

S = "${WORKDIR}/scummvm-${PV}"

EXTRA_OECONF += "--disable-engine=glk,sword25,bladerunner,ultima"

SRCREV = "8916c3df576126f4f773a273a36a4f909ab0106a"
SRC_URI = "git://github.com/scummvm/scummvm.git;protocol=git;branch=branch-2-2"
S = "${WORKDIR}/git"

FILESPATHPKG_prepend = "scummvm-${PV}:"

#SRC_URI[md5sum] = "79f8c12fa7a82f2b9331ef3969f07819"
#SRC_URI[sha256sum] = "c5616fec60bd4004006ecbd1f79878edc9f1e6040ca6afc0461ed832505c4b50"
