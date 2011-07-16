DESCRIPTION = "Simple DirectMedia Layer (Samsung Content Library framebuffer support)"
SECTION = "libs"
PRIORITY = "optional"
LICENSE = "LGPL"
DEPENDS = ""
PR = "r0"

SRC_URI = " \
  http://www.libsdl.org/release/SDL-${PV}.tar.gz \
  file://sdl.m4 \
  file://samygo-cl.patch \
"

SRC_URI[md5sum] = "e52086d1b508fa0b76c52ee30b55bec4"
SRC_URI[sha256sum] = "5d927e287034cb6bb0ebccfa382cb1d185cb113c8ab5115a0759798642eed9b6"

S = "${WORKDIR}/SDL-${PV}"

inherit autotools binconfig pkgconfig

CFLAGS = "-O2 -fvisibility=hidden"

EXTRA_OECONF = " \
  --disable-shared --disable-debug --enable-threads --enable-timers --enable-endian \
  --enable-file --disable-oss --disable-alsa --disable-esd --disable-arts \
  --disable-diskaudio --disable-nas --disable-esd-shared --disable-esdtest \
  --disable-mintaudio --disable-nasm --disable-video-x11 --disable-video-dga \
  --disable-video-fbcon --disable-video-directfb --disable-video-ps2gs \
  --disable-video-xbios --disable-video-gem --enable-video-dummy \
  --disable-video-opengl --enable-input-events --enable-pthreads \
  --disable-video-picogui --disable-video-qtopia --enable-dlopen \
  --disable-input-tslib --disable-video-ps3 \
"

do_configure() { 
  oe_runconf
}

do_configure_append () {
  cd ${S}

  # prevent libtool from linking libs against libstdc++, libgcc, ...
  cat ${TARGET_PREFIX}libtool | sed -e 's/postdeps=".*"/postdeps=""/' > ${TARGET_PREFIX}libtool.tmp
  mv ${TARGET_PREFIX}libtool.tmp ${TARGET_PREFIX}libtool

  # copy new sdl.m4 macrofile to the dir for installing
  cp ${WORKDIR}/sdl.m4 ${S}/
}

do_stage() {
  install -d ${STAGING_INCDIR}/SDL
  install -m 0644 ${S}/include/*.h ${STAGING_INCDIR}/SDL

  oe_libinstall -C build -a libSDL ${STAGING_LIBDIR}
}

FILES_${PN} = "${libdir}/lib*.a"
FILES_${PN}-dev += "${bindir}/*config"
