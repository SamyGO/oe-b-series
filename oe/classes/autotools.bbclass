# use autotools_stage_all for native packages
AUTOTOOLS_NATIVE_STAGE_INSTALL = "1"

def autotools_deps(d):
	if bb.data.getVar('INHIBIT_AUTOTOOLS_DEPS', d, 1):
		return ''

	pn = bb.data.getVar('PN', d, 1)
	deps = ''

	if pn in ['autoconf-native', 'automake-native']:
		return deps
	deps += 'autoconf-native automake-native '

	if not pn in ['libtool', 'libtool-native', 'libtool-cross']:
		deps += 'libtool-native '
		if not bb.data.inherits_class('native', d) \
                        and not bb.data.inherits_class('cross', d) \
                        and not bb.data.inherits_class('sdk', d) \
                        and not bb.data.getVar('INHIBIT_DEFAULT_DEPS', d, 1):
                    deps += 'libtool-cross '

	return deps + 'gnu-config-native '

EXTRA_OEMAKE = ""

DEPENDS_prepend = "${@autotools_deps(d)}"
DEPENDS_virtclass-native_prepend = "${@autotools_deps(d)}"
DEPENDS_virtclass-nativesdk_prepend = "${@autotools_deps(d)}"

inherit siteinfo

def _autotools_get_sitefiles(d):
    def inherits(d, *classes):
        if any(bb.data.inherits_class(cls, d) for cls in classes):
            return True

    if inherits(d, "native", "nativesdk"):
        return

    sitedata = siteinfo_data(d)
    for path in d.getVar("BBPATH", True).split(":"):
        for element in sitedata:
            filename = os.path.join(path, "site", element)
            if os.path.exists(filename):
                yield filename

# Space separated list of shell scripts with variables defined to supply test
# results for autoconf tests we cannot run at build time.
export CONFIG_SITE = "${@' '.join(_autotools_get_sitefiles(d))}"

acpaths = "default"
EXTRA_AUTORECONF = "--exclude=autopoint"

def autotools_set_crosscompiling(d):
	if not bb.data.inherits_class('native', d):
		return " cross_compiling=yes"
	return ""

# EXTRA_OECONF_append = "${@autotools_set_crosscompiling(d)}"

CONFIGUREOPTS = " --build=${BUILD_SYS} \
		  --host=${HOST_SYS} \
		  --target=${TARGET_SYS} \
		  --prefix=${prefix} \
		  --exec_prefix=${exec_prefix} \
		  --bindir=${bindir} \
		  --sbindir=${sbindir} \
		  --libexecdir=${libexecdir} \
		  --datadir=${datadir} \
		  --sysconfdir=${sysconfdir} \
		  --sharedstatedir=${sharedstatedir} \
		  --localstatedir=${localstatedir} \
		  --libdir=${libdir} \
		  --includedir=${includedir} \
		  --oldincludedir=${oldincludedir} \
		  --infodir=${infodir} \
		  --mandir=${mandir}"

oe_runconf () {
	if [ -x ${S}/configure ] ; then
		${S}/configure ${CONFIGUREOPTS} ${EXTRA_OECONF} "$@"
	else
		oefatal "no configure script found"
	fi
}

autotools_do_configure() {
	case ${PN} in
	autoconf*)
	;;
	automake*)
	;;
	*)
		# WARNING: gross hack follows:
		# An autotools built package generally needs these scripts, however only
		# automake or libtoolize actually install the current versions of them.
		# This is a problem in builds that do not use libtool or automake, in the case
		# where we -need- the latest version of these scripts.  e.g. running a build
		# for a package whose autotools are old, on an x86_64 machine, which the old
		# config.sub does not support.  Work around this by installing them manually
		# regardless.
		( for ac in `find ${S} -name configure.in -o -name configure.ac`; do
			rm -f `dirname $ac`/configure
			done )
		if [ -e ${S}/configure.in -o -e ${S}/configure.ac ]; then
			olddir=`pwd`
			cd ${S}
			if [ x"${acpaths}" = xdefault ]; then
				acpaths=
				for i in `find ${S} -maxdepth 2 -name \*.m4|grep -v 'aclocal.m4'| \
					grep -v 'acinclude.m4' | sed -e 's,\(.*/\).*$,\1,'|sort -u`; do
					acpaths="$acpaths -I $i"
				done
			else
				acpaths="${acpaths}"
			fi
			AUTOV=`automake --version |head -n 1 |sed "s/.* //;s/\.[0-9]\+$//"`
			automake --version
			echo "AUTOV is $AUTOV"
			install -d ${STAGING_DATADIR}/aclocal
			install -d ${STAGING_DATADIR}/aclocal-$AUTOV
			acpaths="$acpaths -I${STAGING_DATADIR}/aclocal-$AUTOV -I ${STAGING_DATADIR}/aclocal"
			# autoreconf is too shy to overwrite aclocal.m4 if it doesn't look
			# like it was auto-generated.  Work around this by blowing it away
			# by hand, unless the package specifically asked not to run aclocal.
			if ! echo ${EXTRA_AUTORECONF} | grep -q "aclocal"; then
				rm -f aclocal.m4
			fi
			if [ -e configure.in ]; then
			  CONFIGURE_AC=configure.in
			else
			  CONFIGURE_AC=configure.ac
			fi
			if grep "^[[:space:]]*AM_GLIB_GNU_GETTEXT" $CONFIGURE_AC >/dev/null; then
			  if grep "sed.*POTFILES" $CONFIGURE_AC >/dev/null; then
			    : do nothing -- we still have an old unmodified configure.ac
			  else
			    oenote Executing glib-gettextize --force --copy
			    echo "no" | glib-gettextize --force --copy
			  fi
			else if grep "^[[:space:]]*AM_GNU_GETTEXT" $CONFIGURE_AC >/dev/null; then
			  if [ -e ${STAGING_DATADIR}/gettext/config.rpath ]; then
			    cp ${STAGING_DATADIR}/gettext/config.rpath ${S}/
			  else
			    oenote ${STAGING_DATADIR}/gettext/config.rpath not found. gettext is not installed.
			  fi
			fi

			fi
			mkdir -p m4
			oenote Executing autoreconf --verbose --install --force ${EXTRA_AUTORECONF} $acpaths
			autoreconf -Wcross --verbose --install --force ${EXTRA_AUTORECONF} $acpaths || oefatal "autoreconf execution failed."
			if grep "^[[:space:]]*[AI][CT]_PROG_INTLTOOL" $CONFIGURE_AC >/dev/null; then
			  oenote Executing intltoolize --copy --force --automake
			  intltoolize --copy --force --automake
			fi
			cd $olddir
		fi
	;;
	esac
	if [ -e ${S}/configure ]; then
		oe_runconf $@
	else
		oenote "nothing to configure"
	fi
}

autotools_do_install() {
	oe_runmake 'DESTDIR=${D}' install
}

PACKAGE_PREPROCESS_FUNCS += "autotools_prepackage_lamangler"

autotools_prepackage_lamangler () {
        for i in `find ${PKGD} -name "*.la"` ; do \
            sed -i -e 's:${STAGING_LIBDIR}:${libdir}:g;' \
                   -e 's:${D}::g;' \
                   -e 's:-I${WORKDIR}\S*: :g;' \
                   -e 's:-L${WORKDIR}\S*: :g;' \
                   $i
	done
}

# STAGE_TEMP_PREFIX is used for a speedup by packaged-staging
STAGE_TEMP="${WORKDIR}/temp-staging"
STAGE_TEMP_PREFIX = ""

autotools_stage_includes() {
	if [ "${INHIBIT_AUTO_STAGE_INCLUDES}" != "1" ]
	then
		rm -rf ${STAGE_TEMP}
		mkdir -p ${STAGE_TEMP}
		make DESTDIR="${STAGE_TEMP}" install
		cp -pPR ${STAGE_TEMP}/${includedir}/* ${STAGING_INCDIR}
		rm -rf ${STAGE_TEMP}
	fi
}

autotools_stage_dir() {
 	sysroot_stage_dir $1 ${STAGE_TEMP_PREFIX}$2
}

autotools_stage_libdir() {
	sysroot_stage_libdir $1 ${STAGE_TEMP_PREFIX}$2
}

autotools_stage_all() {
	if [ "${INHIBIT_AUTO_STAGE}" = "1" ]
	then
		return
	fi
	rm -rf ${STAGE_TEMP}
	mkdir -p ${STAGE_TEMP}
	oe_runmake DESTDIR="${STAGE_TEMP}" install
	rm -rf ${STAGE_TEMP}/${mandir} || true
	rm -rf ${STAGE_TEMP}/${infodir} || true
	sysroot_stage_dirs ${STAGE_TEMP} ${STAGE_TEMP_PREFIX}
	rm -rf ${STAGE_TEMP}
}

EXPORT_FUNCTIONS do_configure do_install

