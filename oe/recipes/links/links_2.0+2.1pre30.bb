require links.inc

#LocalChange: do not depend on gpm
#DEPENDS += "gpm"
RCONFLICTS_${PN} = "links-x11"
PR = "r2"

#LocalChange: without fb, gpm; disable graphics
EXTRA_OECONF = "--enable-javascript --with-libfl --enable-graphics \
	        --with-ssl=${STAGING_LIBDIR}/.. --with-libjpeg \
	        --without-libtiff --without-svgalib --without-fb \
	        --without-directfb --without-pmshell --without-atheos \
	        --without-x --without-sdl --without-gpm --disable-graphics"

SRC_URI[md5sum] = "f0f107cc824b71e43f0c6ab620209daf"
SRC_URI[sha256sum] = "f32314d851e86ec463967ddce78d051e3953b529878cbaeecf882c625ad29c75"
