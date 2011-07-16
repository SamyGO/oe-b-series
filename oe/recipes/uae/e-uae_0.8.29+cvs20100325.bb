DESCRIPTION = "Amiga Emulator based on SDL"
SECTION = "base"
PRIORITY = "optional"
DEPENDS = "libsdl-x11 zlib"
LICENSE = "GPL"
PR = "r0"

#LocalChange: added remove-libscg.patch
SRC_URI = "cvs://anonymous@uaedev.cvs.sourceforge.net/cvsroot/uaedev;module=uae \
           file://configure.patch \
           file://remove-libscg.patch \
"

inherit autotools

export SDL_CONFIG = "${STAGING_BINDIR_CROSS}/sdl-config"

EXTRA_OECONF = "--with-hostcc=gcc --disable-ui --without-x --with-sdl --with-sdl-gfx --with-sdl-sound \
		--without-gtk --without-alsa --with-zlib=${STAGING_LIBDIR}/.."

CFLAGS_append = " -DSTAT_STATFS2_BSIZE=1 "
CXXFLAGS_append = " -DSTAT_STATFS2_BSIZE=1 "
PARALLEL_MAKE = ""

export S = "${WORKDIR}/uae"

export PKG_CONFIG="${STAGING_BINDIR_NATIVE}/pkg-config"

do_configure_prepend () {
	sed -i -e s:getline:etline:g ./src/gui-none/nogui.c
	touch NEWS AUTHORS ChangeLog
}
