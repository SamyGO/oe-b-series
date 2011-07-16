DESCRIPTION = "xor files"
SECTION = "console/utils"
PV = "2.1"
PR = "2"
S = "${WORKDIR}/crypt-xor-${PV}"

SRC_URI = "http://crypt-xor.sourceforge.net/stable/crypt-xor_${PV}-${PR}.tar.gz \
	file://fix_compile.patch \
"

inherit native

do_compile() {
	${CXX} -I. -o crypt-xor crypt-XOR.c
}

do_stage() {
	install -m 0755 crypt-xor ${STAGING_BINDIR}/
}

SRC_URI[md5sum] = "cf8d2c7b188e387cbdf8da23fcc8dba3"
SRC_URI[sha256sum] = "e4864586ac220b3350fd694baa019841969c3060885de7a5e7d9266d2efb300e"
