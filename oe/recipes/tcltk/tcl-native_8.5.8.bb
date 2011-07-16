inherit native
include tcl_8.5.8.bb

SRC_URI = "\
  ${SOURCEFORGE_MIRROR}/tcl/tcl${PV}-src.tar.gz \
  file://confsearch.diff;striplevel=2 \
  file://manpages.diff;striplevel=2 \
  file://non-linux.diff;striplevel=2 \
  file://rpath.diff;striplevel=2 \
  file://tcllibrary.diff;striplevel=2 \
  file://tclpackagepath.diff;striplevel=2 \
  file://tclprivate.diff;striplevel=2 \
  file://mips-tclstrtod.patch;striplevel=0 \
"

#LocalChange: added native version package
do_stage() {
	oe_libinstall -a libtclstub8.5 ${STAGING_LIBDIR}
	if [ -e libtcl8.5.dylib ]; then
		install -m 0644 libtcl8.5.dylib ${STAGING_LIBDIR}
	else
		oe_libinstall -so libtcl8.5 ${STAGING_LIBDIR}
	fi
	sed -i "s+${WORKDIR}+${STAGING_INCDIR}+g" tclConfig.sh
        sed -i "s,-L${libdir},," tclConfig.sh
	install -d ${STAGING_BINDIR}/
	install -m 0755 tclConfig.sh ${STAGING_BINDIR}
	install -m 0755 tclsh ${STAGING_BINDIR}/tclsh8.5
        ln -s -f tclsh8.4 ${STAGING_BINDIR}/tclsh
	cd ..
	for dir in compat generic unix
	do
		install -d ${STAGING_INCDIR}/tcl${PV}/$dir
		install -m 0644 $dir/*.h ${STAGING_INCDIR}/tcl${PV}/$dir/
	done
	install -m 0644 generic/tcl.h ${STAGING_INCDIR}
	install -m 0644 generic/tclDecls.h ${STAGING_INCDIR}
	install -m 0644 generic/tclPlatDecls.h ${STAGING_INCDIR}
}


#LocalChange: fixes empty packages
PACKAGES = ""
