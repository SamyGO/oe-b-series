require u-boot.inc

#SamyGO: it's custom package
PR = "r0"

DEPENDS = ""

SRC_URI = "ftp://ftp.denx.de/pub/u-boot/u-boot-1.1.6.tar.bz2 \
	file://common-fixes.patch \
	file://fat-enhance.patch \
	file://usb-enhance.patch \
	file://keypress.patch \
	file://ssdtv.patch \
"

SRC_URI[md5sum] = "5b1b1f7b3b1e06f75f5bfbd79891067b"
SRC_URI[sha256sum] = "778acb0eafe1d9b94c6f5ec5f333126c40d73704920ff8b23085c6dedecfd6e8"

do_compile () {
        unset LDFLAGS
        unset CFLAGS
        unset CPPFLAGS
        oe_runmake ssdtv_config
        oe_runmake all
        oe_runmake tools
}

do_fixup() {
        sed -i -e s,192.168.1.2,${MA_TARGET_IP},g ${WORKDIR}/u-boot-${PV}/include/configs/ssdtv.h
        sed -i -e s,255.255.255.0,${MA_TARGET_MASK},g ${WORKDIR}/u-boot-${PV}/include/configs/ssdtv.h
        sed -i -e s,00:00:00:00:00:00,${MA_TARGET_MAC},g ${WORKDIR}/u-boot-${PV}/include/configs/ssdtv.h
        sed -i -e s,192.168.1.5,${MA_GATEWAY_IP},g ${WORKDIR}/u-boot-${PV}/include/configs/ssdtv.h
        sed -i -e s,192.168.1.1,${MA_NFS_IP},g ${WORKDIR}/u-boot-${PV}/include/configs/ssdtv.h
        sed -i -e s,/nfspath,${MA_NFS_PATH},g ${WORKDIR}/u-boot-${PV}/include/configs/ssdtv.h
}

addtask fixup after do_patch before do_compile

