require xorg-app-common.inc
DEPENDS += " xproto util-macros"
PE = "1"
PR = "${INC_PR}.0"

SRC_URI[archive.md5sum] = "44ea16cc3104de6401bc74035f642357"
SRC_URI[archive.sha256sum] = "162111c0192c8f78e99a6ee9a3df5eb149251c5800896c993399da005ec7fe95"

FILES_${PN} += "${datadir}/X11"
