DESCRIPTION = "SDL VNC client"
LICENSE = "GPL"
SECTION = "base"
PRIORITY = "optional"
DEPENDS = "libsdl-cl"

SRC_URI = "file://clmeta-story.dat file://clmeta.dat file://telnet.png file://telnet.c file://telnet.sh "

S = "${WORKDIR}/telnet-enabler-cl-${PV}"

PR = "r0"

do_configure() {
	install -m 0644 ${WORKDIR}/*.c ${S}/
}

do_compile() {
	${CC} ${S}/telnet.c -shared ${CFLAGS} ${LDFLAGS} -o ${S}/telnet.so
}

FILES_${PN} = "/telnet-enabler"

do_install() {
	install -d ${D}/telnet-enabler
	install -m 0644 ${WORKDIR}/clmeta-story.dat ${D}/telnet-enabler/clmeta.dat
	install -m 0644 ${WORKDIR}/telnet.png ${D}/telnet-enabler/trojan.png

	install -d ${D}/telnet-enabler/telnet
	install -m 0644 ${S}/telnet.so ${D}/telnet-enabler/telnet/telnet.so
	install -m 0644 ${WORKDIR}/clmeta.dat ${D}/telnet-enabler/telnet/clmeta.dat
	install -m 0644 ${WORKDIR}/telnet.png ${D}/telnet-enabler/telnet/telnet.png
	install -m 0755 ${WORKDIR}/telnet.sh ${D}/telnet-enabler/telnet/telnet.sh
}

