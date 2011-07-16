DESCRIPTION = "ltrace shows runtime library call information for dynamically linked executables."
HOMEPAGE = "http://ltrace.alioth.debian.org"
SECTION = "devel"
DEPENDS = "libelf binutils"
LICENSE = "GPLv2"

PR = "r2"

#LocalChange: use newer patch
SRC_URI = "\
  ${DEBIAN_MIRROR}/main/l/ltrace/ltrace_${PV}.orig.tar.gz;name=archive \
  ${DEBIAN_MIRROR}/main/l/ltrace/ltrace_${PV}-2.1.diff.gz;name=patch \
  file://add-sysdep.patch \
  file://ltrace-compile.patch \
  file://ltrace-mips-remove-CP.patch \
  file://ltrace-mips.patch \
  file://ltrace-ppc.patch \
"
inherit autotools

export TARGET_CFLAGS = "${SELECTED_OPTIMIZATION} -isystem ${STAGING_INCDIR}"
TARGET_CC_ARCH += "${LDFLAGS}"

do_configure_prepend() {
	case ${TARGET_ARCH} in
		arm*)  ln -sf ./linux-gnu sysdeps/linux-gnueabi ;;
		mips*)  ln -sf ./mipsel sysdeps/linux-gnu/mips ;;
	esac
	#LocalChange: proper fixes to Makefile.in, Makefile; fixed events.c
	sed -e 's:uname -m:echo arm-linux-gnueabi:g' \
		sysdeps/linux-gnu/Makefile > sysdeps/linux-gnu/Makefile.in
	sed -i -e 's:uname -m:echo arm-linux-gnueabi:g' \
		sysdeps/linux-gnu/Makefile
	sed -i -e 's:@HOST_OS@:linux-gnueabi:g' \
		Makefile.in
	sed -i -e 's:sys/ptrace.h:linux/ptrace.h:g' \
		sysdeps/linux-gnu/events.c
}

do_compile() {
	case ${TARGET_ARCH} in
		alpha*)   LTRACE_ARCH=alpha ;;
		arm*)     LTRACE_ARCH=arm ;;
		cris*)    LTRACE_ARCH=cris ;;
		hppa*)    LTRACE_ARCH=parisc ;;
		i*86*)    LTRACE_ARCH=i386 ;;
		ia64*)    LTRACE_ARCH=ia64 ;;
		mips*)    LTRACE_ARCH=mips ;;
		m68k*)    LTRACE_ARCH=m68k ;;
		powerpc*) LTRACE_ARCH=ppc ;;
		s390*)    LTRACE_ARCH=s390 ;;
		sh*)      LTRACE_ARCH=sh ;;
		sparc64*) LTRACE_ARCH=sparc64 ;;
		sparc*)   LTRACE_ARCH=sparc ;;
		x86_64*)  LTRACE_ARCH=x86_64 ;;
	esac
	oe_runmake LDFLAGS=${TARGET_LDFLAGS} LIBS="-lsupc++ -liberty -Wl,-Bstatic -lelf -Wl,-Bdynamic" ${EXTRA_OEMAKE} ARCH=${LTRACE_ARCH}
}

do_install() {
	case ${TARGET_ARCH} in
		alpha*)   LTRACE_ARCH=alpha ;;
		arm*)     LTRACE_ARCH=arm ;;
		cris*)    LTRACE_ARCH=cris ;;
		hppa*)    LTRACE_ARCH=parisc ;;
		i*86*)    LTRACE_ARCH=i386 ;;
		ia64*)    LTRACE_ARCH=ia64 ;;
		mips*)    LTRACE_ARCH=mips ;;
		m68k*)    LTRACE_ARCH=m68k ;;
		powerpc*) LTRACE_ARCH=ppc ;;
		s390*)    LTRACE_ARCH=s390 ;;
		sh*)      LTRACE_ARCH=sh ;;
		sparc64*) LTRACE_ARCH=sparc64 ;;
		sparc*)   LTRACE_ARCH=sparc ;;
		x86_64*)  LTRACE_ARCH=x86_64 ;;
	esac
	oe_runmake install ${EXTRA_OEMAKE} ARCH=${LTRACE_ARCH} DESTDIR=${D}
}

SRC_URI[archive.md5sum] = "3fa7fe715ab879db08bd06d1d59fd90f"
SRC_URI[archive.sha256sum] = "5c6627d6d5a98a92ca4661cfc16378b182cc46a9ec479ebf7e6121ee3fe2be32"
SRC_URI[patch.md5sum] = "38bc944c53ab602a7854aa4fa71c1f46"
SRC_URI[patch.sha256sum] = "4c57df94020f2bed90d948f757ca7786796ca9218274764b24f61c502d9ef4f6"
