SUMMARY = "Tool for working with series of patches"
HOMEPAGE = "http://savannah.nongnu.org/projects/quilt/"
SECTION = "devel"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=94d55d512a9ba36caa9b7df079bae19f"

SRC_URI = "http://download.savannah.gnu.org/releases/quilt/quilt-${PV}.tar.gz \
        file://run-ptest \
        file://Makefile \
        file://test.sh \
        file://0001-tests-Allow-different-output-from-mv.patch \
"

SRC_URI[md5sum] = "6800c2404a2c0598ab2eff92a636ba70"
SRC_URI[sha256sum] = "314b319a6feb13bf9d0f9ffa7ce6683b06919e734a41275087ea457cc9dc6e07"

inherit autotools

EXTRA_OECONF_darwin += "--without-date \
                        --without-getopt \
                        "

CLEANBROKEN = "1"

PACKAGES += "guards guards-doc"
FILES_${PN} = "${sysconfdir} ${datadir}/quilt \
               ${bindir}/quilt ${libdir}/quilt"
FILES_guards = "${bindir}/guards"
FILES_${PN}-doc = "${mandir}/man1/quilt.1 ${docdir}/${BPN}"
FILES_guards-doc = "${mandir}/man1/guards.1"

RDEPENDS_${PN} = "bash"

EXTRA_OE_MAKE_ARGS_darwin ?= ""
EXTRA_OE_MAKE_ARGS ?= "BUILD_ROOT=${D}"

EXTRA_OECONF = "--with-perl='${USRBINPATH}/env perl' --with-patch=patch"

CACHED_CONFIGUREVARS += "ac_cv_path_BASH=/bin/bash"

# Make sure we don't have "-w" in shebang lines: it breaks using
# "/usr/bin/env perl" as parser
do_configure_prepend () {
	find ${S} -name "*.in" -exec sed -i -e "1s,^#\!.*@PERL@ -w$,#\! @PERL@\nuse warnings;," {} \;
}

# Don't setup symlinks to host utilities, we don't need them
do_configure_append () {
	sed -e 's,^COMPAT_SYMLINKS.*:=.*,COMPAT_SYMLINKS	:=,' -i ${S}/Makefile
}

# quilt ignores DESTDIR
do_install () {
	oe_runmake ${EXTRA_OE_MAKE_ARGS} install
	# cleanup unpackaged files
	rm -rf ${D}/${datadir}/emacs
}

do_compile_ptest() {
	oe_runmake bin/patch-wrapper test/.depend
}

do_install_ptest() {
	tar -c --exclude=\*.in bin/ | ( cd ${D}${PTEST_PATH} && tar -xf - )
	tar -c --exclude=\*.in compat/ | ( cd ${D}${PTEST_PATH} && tar -xf - )
	tar -c --exclude=\*.in quilt/ | ( cd ${D}${PTEST_PATH} && tar -xf - )
	tar -c --exclude=mail.test --exclude=delete.test test/ | ( cd ${D}${PTEST_PATH} && tar -xf - && chmod 777 test)
	cp ${WORKDIR}/Makefile ${D}${PTEST_PATH}
	cp ${WORKDIR}/test.sh ${D}${PTEST_PATH}
}

RDEPENDS_${PN}-ptest = "make file sed gawk diffutils findutils ed perl \
                        perl-module-filehandle perl-module-getopt-std \
                        perl-module-posix perl-module-file-temp \
                        perl-module-text-parsewords perl-module-overloading \
                        bash util-linux-getopt \
                       "
