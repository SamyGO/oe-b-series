DESCRIPTION = "Hash Calculator"
SECTION = "console/utils"
PV = "1.3.14"
PR = "r0"

FILESPATHPKG_prepend = "cksfv-${PV}:files:"

SRC_URI = "http://zakalwe.fi/~shd/foss/cksfv/files/cksfv-${PV}.tar.gz"
SRC_URI_append_samygo =+ " file://validinfo_format.patch"

S = "${WORKDIR}/cksfv-${PV}"

do_configure () {
	./configure	
}

do_compile () {
	oe_runmake 
}

do_install () {
	install -d ${D}/bin
	install -m 0755 src/cksfv ${D}/bin/cksfv	
}

SRC_URI[md5sum] = "2e15289753ea0b90b6ea86993f93b383"
SRC_URI[sha256sum] = "010facce85b317b7b9f952c84cd59ce03476a2b685db33a49b6ea0d1b38378ea"
