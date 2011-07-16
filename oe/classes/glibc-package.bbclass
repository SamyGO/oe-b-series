#
# This class knows how to package up glibc. Its shared since prebuild binary toolchains
# may need packaging and its pointless to duplicate this code.
#
# Caller should set GLIBC_INTERNAL_USE_BINARY_LOCALE to one of:
#  "compile" - Use QEMU to generate the binary locale files
#  "precompiled" - The binary locale files are pregenerated and already present
#  "ondevice" - The device will build the locale files upon first boot through the postinst

inherit qemu

GLIBC_INTERNAL_USE_BINARY_LOCALE ?= "ondevice"

PACKAGES = "glibc-dbg glibc catchsegv sln nscd ldd localedef glibc-utils glibc-pic glibc-dev glibc-static glibc-doc glibc-locale libcidn libmemusage libsegfault glibc-extra-nss glibc-thread-db glibc-pcprofile"
PACKAGES_DYNAMIC = "glibc-gconv-* glibc-charmap-* glibc-localedata-* locale-base-* glibc-binary-localedata-*"

INSANE_SKIP_glibc-dbg = True

libc_baselibs = "${base_libdir}/libcrypt*.so.* ${base_libdir}/libcrypt-*.so ${base_libdir}/libc*.so.* ${base_libdir}/libc-*.so ${base_libdir}/libm*.so.* ${base_libdir}/libm-*.so ${base_libdir}/ld*.so.* ${base_libdir}/ld-*.so ${base_libdir}/libpthread*.so.* ${base_libdir}/libpthread-*.so ${base_libdir}/libresolv*.so.* ${base_libdir}/libresolv-*.so ${base_libdir}/librt*.so.* ${base_libdir}/librt-*.so ${base_libdir}/libutil*.so.* ${base_libdir}/libutil-*.so ${base_libdir}/libnsl*.so.* ${base_libdir}/libnsl-*.so ${base_libdir}/libnss_files*.so.* ${base_libdir}/libnss_files-*.so ${base_libdir}/libnss_compat*.so.* ${base_libdir}/libnss_compat-*.so ${base_libdir}/libnss_dns*.so.* ${base_libdir}/libnss_dns-*.so ${base_libdir}/libdl*.so.* ${base_libdir}/libdl-*.so ${base_libdir}/libanl*.so.* ${base_libdir}/libanl-*.so ${base_libdir}/libBrokenLocale*.so.* ${base_libdir}/libBrokenLocale-*.so"

# The problem is that if PN = "glibc", FILES_${PN} will overwrite FILES_glibc
# Solution: Make them both the same thing, then it doesn't matter

glibcfiles = "${libc_baselibs} ${libexecdir}/* ${datadir}/zoneinfo ${@base_conditional('USE_LDCONFIG', '1', '${base_sbindir}/ldconfig', '', d)}"
glibcdbgfiles = "${bindir}/.debug ${sbindir}/.debug ${libdir}/.debug \
                  ${base_bindir}/.debug ${base_sbindir}/.debug ${base_libdir}/.debug \
                  ${libdir}/gconv/.debug ${libexecdir}/*/.debug"
glibcpicfiles = "${libdir}/*_pic.a ${libdir}/*_pic.map ${libdir}/libc_pic/"
glibcdevfiles = "${bindir}/rpcgen ${includedir} ${libdir}/lib*${SOLIBSDEV} ${libdir}/*.la \
                ${libdir}/*.a ${libdir}/*.o ${libdir}/pkgconfig ${libdir}/*nonshared.a \
                ${base_libdir}/*.a ${base_libdir}/*.o ${datadir}/aclocal"

FILES_glibc = "${glibcfiles}"
FILES_${PN} = "${glibcfiles}"
FILES_ldd = "${bindir}/ldd"
FILES_libsegfault = "${base_libdir}/libSegFault*"
FILES_libcidn = "${base_libdir}/libcidn*.so"
FILES_libmemusage = "${base_libdir}/libmemusage.so"
FILES_glibc-extra-nss = "${base_libdir}/libnss*"
FILES_sln = "${base_sbindir}/sln"
FILES_glibc-pic = "${glibcpicfiles}"
FILES_${PN}-pic = "${glibcpicfiles}"
FILES_glibc-dev = "${glibcdevfiles}"
FILES_${PN}-dev = "${glibcdevfiles}"
FILES_glibc-dbg = "${glibcdbgfiles}"
FILES_${PN}-dbg = "${glibcdbgfiles}"
FILES_nscd = "${sbindir}/nscd* ${sysconfdir}/nscd* ${sysconfdir}/init.d/nscd*"
FILES_glibc-utils = "${bindir}/* ${sbindir}/*"
FILES_glibc-gconv = "${libdir}/gconv/*"
FILES_catchsegv = "${bindir}/catchsegv"
RDEPENDS_catchsegv = "libsegfault"
FILES_glibc-pcprofile = "${base_libdir}/libpcprofile.so"
FILES_glibc-thread-db = "${base_libdir}/libthread_db*"
FILES_localedef = "${bindir}/localedef"
RPROVIDES_glibc-dev += "libc-dev"

DESCRIPTION_sln = "glibc: create symbolic links between files"
DESCRIPTION_nscd = "glibc: name service cache daemon for passwd, group, and hosts"
DESCRIPTION_glibc-extra-nss = "glibc: nis, nisplus and hesiod search services"
DESCRIPTION_ldd = "glibc: print shared library dependencies"
DESCRIPTION_localedef = "glibc: compile locale definition files"
DESCRIPTION_glibc-utils = "glibc: misc utilities like iconf, local, gencat, tzselect, rpcinfo, ..."

TMP_LOCALE="/tmp/locale${libdir}/locale"

locale_base_postinst() {
#!/bin/sh

if [ "x$D" != "x" ]; then
  exit 1
fi

rm -rf ${TMP_LOCALE}
mkdir -p ${TMP_LOCALE}
if [ -f ${libdir}/locale/locale-archive ]; then
        cp ${libdir}/locale/locale-archive ${TMP_LOCALE}/
fi
localedef --inputfile=${datadir}/i18n/locales/%s --charmap=%s --prefix=/tmp/locale %s
mkdir -p ${libdir}/locale/
mv ${TMP_LOCALE}/locale-archive ${libdir}/locale/
rm -rf ${TMP_LOCALE}
}

locale_base_postrm() {
#!/bin/sh

rm -rf ${TMP_LOCALE}
mkdir -p ${TMP_LOCALE}
if [ -f ${libdir}/locale/locale-archive ]; then
	cp ${libdir}/locale/locale-archive ${TMP_LOCALE}/
fi
localedef --delete-from-archive --inputfile=${datadir}/locales/%s --charmap=%s --prefix=/tmp/locale %s
mv ${TMP_LOCALE}/locale-archive ${libdir}/locale/
rm -rf ${TMP_LOCALE}
}

do_prep_locale_tree() {
	treedir=${WORKDIR}/locale-tree
	rm -rf $treedir
	mkdir -p $treedir/bin $treedir/lib $treedir/${datadir} $treedir/${libdir}/locale
	cp -pPR ${PKGD}${datadir}/i18n $treedir/${datadir}/i18n
	# unzip to avoid parsing errors
	for i in $treedir/${datadir}/i18n/charmaps/*gz; do 
		gunzip $i
	done
	ls -d ${PKGD}${base_libdir}/* | xargs -iBLAH cp -pPR BLAH $treedir/lib
	if [ -f ${STAGING_DIR_NATIVE}${prefix_native}/lib/libgcc_s.so ]; then
		cp -pPR ${STAGING_DIR_NATIVE}${prefix_native}/lib/libgcc_s.so $treedir/lib
	fi
	if [ -f ${STAGING_DIR_NATIVE}${prefix_native}/lib/libgcc_s.so.* ]; then
		cp -pPR ${STAGING_DIR_NATIVE}${prefix_native}/lib/libgcc_s.so.* $treedir/lib
	fi
	install -m 0755 ${PKGD}${bindir}/localedef $treedir/bin
}

do_collect_bins_from_locale_tree() {
	treedir=${WORKDIR}/locale-tree

	mkdir -p ${PKGD}${libdir}
	cp -pPR $treedir/${libdir}/locale ${PKGD}${libdir}
}

python package_do_split_gconvs () {
	import os, re
	if (bb.data.getVar('PACKAGE_NO_GCONV', d, 1) == '1'):
		bb.note("package requested not splitting gconvs")
		return

	if not bb.data.getVar('PACKAGES', d, 1):
		return

	libdir = bb.data.getVar('libdir', d, 1)
	if not libdir:
		bb.error("libdir not defined")
		return
	datadir = bb.data.getVar('datadir', d, 1)
	if not datadir:
		bb.error("datadir not defined")
		return

	gconv_libdir = base_path_join(libdir, "gconv")
	charmap_dir = base_path_join(datadir, "i18n", "charmaps")
	locales_dir = base_path_join(datadir, "i18n", "locales")
	binary_locales_dir = base_path_join(libdir, "locale")

	do_split_packages(d, gconv_libdir, file_regex='^(.*)\.so$', output_pattern='glibc-gconv-%s', description='gconv module for character set %s', extra_depends='glibc-gconv')

	do_split_packages(d, charmap_dir, file_regex='^(.*)\.gz$', output_pattern='glibc-charmap-%s', description='character map for %s encoding', extra_depends='')

	def calc_locale_deps(fn, pkg, file_regex, output_pattern, group):
		deps = []
		f = open(fn, "r")
		c_re = re.compile('^copy "(.*)"')
		i_re = re.compile('^include "(\w+)".*')
		for l in f.readlines():
			m = c_re.match(l) or i_re.match(l)
			if m:
				dp = legitimize_package_name('glibc-localedata-%s' % m.group(1))
				if not dp in deps:
					deps.append(dp)
		f.close()
		if deps != []:
			bb.data.setVar('RDEPENDS_%s' % pkg, " ".join(deps), d)

	do_split_packages(d, locales_dir, file_regex='(.*)', output_pattern='glibc-localedata-%s', description='locale definition for %s', hook=calc_locale_deps, extra_depends='')
	bb.data.setVar('PACKAGES', bb.data.getVar('PACKAGES', d) + ' glibc-gconv', d)

	use_bin = bb.data.getVar("GLIBC_INTERNAL_USE_BINARY_LOCALE", d, 1)

	dot_re = re.compile("(.*)\.(.*)")

	if use_bin != "precompiled":
		supported = bb.data.getVar('GLIBC_GENERATE_LOCALES', d, 1)
		if not supported or supported == "all":
		    f = open(base_path_join(bb.data.getVar('WORKDIR', d, 1), "SUPPORTED"), "r")
		    supported = f.readlines()
		    f.close()
		else:
		    supported = supported.split()
		    supported = map(lambda s:s.replace(".", " ") + "\n", supported)
	else:
		supported = []
		full_bin_path = bb.data.getVar('PKGD', d, True) + binary_locales_dir
		for dir in os.listdir(full_bin_path):
			dbase = dir.split(".")
			d2 = "  "
			if len(dbase) > 1:
				d2 = "." + dbase[1].upper() + "  "
			supported.append(dbase[0] + d2)

	# Collate the locales by base and encoding
	utf8_only = int(bb.data.getVar('LOCALE_UTF8_ONLY', d, 1) or 0)
	encodings = {}
	for l in supported:
		l = l[:-1]
		(locale, charset) = l.split(" ")
		if utf8_only and charset != 'UTF-8':
			continue
		m = dot_re.match(locale)
		if m:
			locale = m.group(1)
		if not encodings.has_key(locale):
			encodings[locale] = []
		encodings[locale].append(charset)

	def output_locale_source(name, pkgname, locale, encoding):
		bb.data.setVar('RDEPENDS_%s' % pkgname, 'localedef glibc-localedata-%s glibc-charmap-%s' % (legitimize_package_name(locale), legitimize_package_name(encoding)), d)
		bb.data.setVar('pkg_postinst_%s' % pkgname, bb.data.getVar('locale_base_postinst', d, 1) % (locale, encoding, locale), d)
		bb.data.setVar('pkg_postrm_%s' % pkgname, bb.data.getVar('locale_base_postrm', d, 1) % (locale, encoding, locale), d)

	def output_locale_binary_rdepends(name, pkgname, locale, encoding):
		m = re.match("(.*)\.(.*)", name)
		if m:
			glibc_name = "%s.%s" % (m.group(1), m.group(2).lower().replace("-",""))
		else:
			glibc_name = name
		bb.data.setVar('RDEPENDS_%s' % pkgname, legitimize_package_name('glibc-binary-localedata-%s' % glibc_name), d)

	def output_locale_binary(name, pkgname, locale, encoding):
		# This is a hack till linux-libc-headers gets patched for the missing arm syscalls and all arm device kernels as well
		if bb.data.getVar("DISTRO_NAME", d, 1) == "Angstrom":
			kernel_ver = "2.6.24"
		elif bb.data.getVar("DISTRO_NAME", d, 1) == "KaeilOS":
			kernel_ver = "2.6.24"
		else:
			kernel_ver = bb.data.getVar("OLDEST_KERNEL", d, 1)

		qemu = qemu_target_binary(d) + " -s 1048576"
		if kernel_ver:
			qemu += " -r %s" % (kernel_ver)
		pkgname = 'locale-base-' + legitimize_package_name(name)

		treedir = base_path_join(bb.data.getVar("WORKDIR", d, 1), "locale-tree")
		ldlibdir = "%s/lib" % treedir
		path = bb.data.getVar("PATH", d, 1)
		i18npath = base_path_join(treedir, datadir, "i18n")

		localedef_opts = "--force --old-style --no-archive --prefix=%s --inputfile=%s/i18n/locales/%s --charmap=%s %s" % (treedir, datadir, locale, encoding, name)

		qemu_options = bb.data.getVar("QEMU_OPTIONS_%s" % bb.data.getVar('PACKAGE_ARCH', d, 1), d, 1)
		if not qemu_options:
			qemu_options = bb.data.getVar('QEMU_OPTIONS', d, 1)
		
		cmd = "PATH=\"%s\" I18NPATH=\"%s\" %s -L %s -E LD_LIBRARY_PATH=%s %s %s/bin/localedef %s" % (path, i18npath, qemu, treedir, ldlibdir, qemu_options, treedir, localedef_opts)
		bb.note("generating locale %s (%s)" % (locale, encoding))
		if os.system(cmd):
			raise bb.build.FuncFailed("localedef returned an error (command was %s)." % cmd)

	def output_locale(name, locale, encoding):
		pkgname = 'locale-base-' + legitimize_package_name(name)
		bb.data.setVar('ALLOW_EMPTY_%s' % pkgname, '1', d)
		bb.data.setVar('PACKAGES', '%s %s' % (pkgname, bb.data.getVar('PACKAGES', d, 1)), d)
		rprovides = 'virtual-locale-%s' % legitimize_package_name(name)
		m = re.match("(.*)_(.*)", name)
		if m:
			rprovides += ' virtual-locale-%s' % m.group(1)
		bb.data.setVar('RPROVIDES_%s' % pkgname, rprovides, d)
		if use_bin == "compile":
			output_locale_binary_rdepends(name, pkgname, locale, encoding)
			output_locale_binary(name, pkgname, locale, encoding)
		elif use_bin == "precompiled":
			output_locale_binary_rdepends(name, pkgname, locale, encoding)
		else:
			output_locale_source(name, pkgname, locale, encoding)

	if use_bin == "compile":
		bb.note("preparing tree for binary locale generation")
		bb.build.exec_func("do_prep_locale_tree", d)

	# Reshuffle names so that UTF-8 is preferred over other encodings
	non_utf8 = []
	for l in encodings.keys():
		if len(encodings[l]) == 1:
			output_locale(l, l, encodings[l][0])
			if encodings[l][0] != "UTF-8":
				non_utf8.append(l)
		else:
			if "UTF-8" in encodings[l]:
				output_locale(l, l, "UTF-8")
				encodings[l].remove("UTF-8")
			else:
				non_utf8.append(l)
			for e in encodings[l]:
				output_locale('%s.%s' % (l, e), l, e)

	if non_utf8 != [] and use_bin != "precompiled":
		bb.note("the following locales are supported only in legacy encodings:")
		bb.note("  " + " ".join(non_utf8))

	if use_bin == "compile":
		bb.note("collecting binary locales from locale tree")
		bb.build.exec_func("do_collect_bins_from_locale_tree", d)
		do_split_packages(d, binary_locales_dir, file_regex='(.*)', output_pattern='glibc-binary-localedata-%s', description='binary locale definition for %s', extra_depends='', allow_dirs=True)
	elif use_bin == "precompiled":
		do_split_packages(d, binary_locales_dir, file_regex='(.*)', output_pattern='glibc-binary-localedata-%s', description='binary locale definition for %s', extra_depends='', allow_dirs=True)
	else:
		bb.note("generation of binary locales disabled. this may break i18n!")

}

# We want to do this indirection so that we can safely 'return'
# from the called function even though we're prepending
python populate_packages_prepend () {
	if bb.data.getVar('DEBIAN_NAMES', d, 1):
		bb.data.setVar('PKG_glibc', 'libc6', d)
		bb.data.setVar('PKG_glibc-dev', 'libc6-dev', d)
	bb.build.exec_func('package_do_split_gconvs', d)
}
