
inherit native

PR = "r0"

SRC_URI = "file://mkimage.c file://image.h file://crc32.c"

do_configure() {
	install -m 0644 ${WORKDIR}/mkimage.c ${S}/
	install -m 0644 ${WORKDIR}/image.h ${S}/
	install -m 0644 ${WORKDIR}/crc32.c ${S}/
}

do_compile () {
	${CC} ${CFLAGS} ${LDFLAGS} -I. -o ${S}/mkimage ${S}/mkimage.c ${S}/crc32.c
}

do_stage () {
	install -m 0755 mkimage ${STAGING_BINDIR}/uboot-mkimage
	ln -sf ${STAGING_BINDIR}/uboot-mkimage ${STAGING_BINDIR}/mkimage
}

do_deploy () {
	:
}

