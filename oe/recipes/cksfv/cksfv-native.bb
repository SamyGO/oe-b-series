DESCRIPTION = "Hash Calculator"
SECTION = "console/utils"
PV = "1.3.14"
PR = "r0"

FILESPATH = "${@base_set_filespath([ '${FILE_DIRNAME}/cksfv-${PV}', '${FILE_DIRNAME}/files' ], d)}"

SRC_URI = "http://zakalwe.fi/~shd/foss/cksfv/files/cksfv-${PV}.tar.gz"
SRC_URI_append_samygo =+ " file://validinfo_format.patch"

S = "${WORKDIR}/cksfv-${PV}"

inherit native

do_configure () {
	./configure	
}

do_compile () {
	oe_runmake 
}

do_stage () {
	install -m 0755 src/cksfv ${STAGING_BINDIR}/
}

SRC_URI[md5sum] = "2e15289753ea0b90b6ea86993f93b383"
SRC_URI[sha256sum] = "010facce85b317b7b9f952c84cd59ce03476a2b685db33a49b6ea0d1b38378ea"
