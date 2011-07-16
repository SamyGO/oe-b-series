# mtools OE build file
# Copyright (C) 2004-2006, Advanced Micro Devices, Inc.  All Rights Reserved
# Copyright (C) 2009, O.S. Systems Software Ltda. All Rights Reserved
# Released under the MIT license (see packages/COPYING)

DESCRIPTION="Mtools is a collection of utilities for accessing MS-DOS disks from Unix without mounting them."
HOMEPAGE="http://mtools.linux.lu"
LICENSE="GPL"

SRC_URI="http://ftp.gnu.org/gnu/mtools/mtools-${PV}.tar.bz2 \
	file://m486.patch \
	file://mtools-makeinfo.patch \
	file://plainio.patch \
	file://use-sg_io.patch"

PR = "r1"

inherit autotools

#LocalChange: fixed path
S = "${WORKDIR}/mtools-${PV}"

EXTRA_OECONF = "--without-x"

# Don't try to run install-info -- it'll fail on non-Debian build systems.
EXTRA_OEMAKE = "INSTALL_INFO="
#LocalChange: fixed build on OS X
EXTRA_OEMAKE_append_darwin = " LIBS=-liconv"

do_fix_perms() {
	chmod 644 ${S}/*.c ${S}/*.h
}

addtask fix_perms after do_unpack before do_patch

SRC_URI[md5sum] = "0ee77a14e5f113ad8136a867f8ed4c3a"
SRC_URI[sha256sum] = "53cf808eed9b396070a12c6e53479800a5b9038e9d70c79277e762246ba07a13"
