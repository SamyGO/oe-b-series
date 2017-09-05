DESCRIPTION = "Opkg Package Manager"
DESCRIPTION_libopkg = "Opkg Package Manager Library"
SECTION = "base"
LICENSE = "GPLv2"
SRCREV = "609"
PV = "0.1.8+svnr${SRCPV}"
CONFLICTS = "ipkg"
INC_PR = "r5"
SRCREV = "b71b378dc4580dc8773d8b065c2dbc4f9e701028"

SRC_URI = "git://github.com/shr-project/opkg.git;protocol=git;branch=master \
	   file://remove-ACLOCAL_AMFLAGS-I-shave-I-m4.patch \
	   file://configure \
"

S = "${WORKDIR}/git"

inherit autotools pkgconfig

do_install_prepend() {
  install -d ${D}${sysconfdir}/rcS.d
  install -m 0755 ${WORKDIR}/configure ${D}${sysconfdir}/rcS.d/S40configure
}

EXTRA_OECONF += " --disable-gpg \ 
                  --disable-openssl \ 
                  --disable-ssl-curl \
                  --disable-curl \
                  --disable-sha256"
