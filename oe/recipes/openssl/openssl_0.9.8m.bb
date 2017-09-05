inherit pkgconfig

require openssl.inc
SRC_URI[src.md5sum] = "898bf125370926d5f692a2201124f8ec"
SRC_URI[src.sha256sum] = "36037160281cf4977d964e403d2bc0680fbca0a7ff9f65e33136d75fae12cb5b"

PR = "${INC_PR}.1"

export OE_LDFLAGS="${LDFLAGS}"

SRC_URI += "file://configure-targets.patch \
            file://shared-libs.patch \
            file://debian.patch \
            file://oe-ldflags.patch \
            file://no-docs.patch \
            file://find.pl"

SRC_URI_append_nios2 += "file://Configure-nios2.patch"

PARALLEL_MAKE = ""

do_configure_prepend() {
	cp ${WORKDIR}/find.pl ${S}/util/find.pl
}