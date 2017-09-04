#
# This class knows how to package up [e]glibc. Its shared since prebuild binary toolchains
# may need packaging and its pointless to duplicate this code.
#
# Caller should set GLIBC_INTERNAL_USE_BINARY_LOCALE to one of:
#  "compile" - Use QEMU to generate the binary locale files
#  "precompiled" - The binary locale files are pregenerated and already present
#  "ondevice" - The device will build the locale files upon first boot through the postinst

GLIBC_INTERNAL_USE_BINARY_LOCALE ?= "ondevice"

python __anonymous () {
    enabled = bb.data.getVar("ENABLE_BINARY_LOCALE_GENERATION", d, 1)

    if enabled and int(enabled):
        import re

        target_arch = bb.data.getVar("TARGET_ARCH", d, 1)
        binary_arches = bb.data.getVar("BINARY_LOCALE_ARCHES", d, 1) or ""
        use_cross_localedef = bb.data.getVar("LOCALE_GENERATION_WITH_CROSS-LOCALEDEF", d, 1) or ""

        for regexp in binary_arches.split(" "):
            r = re.compile(regexp)

            if r.match(target_arch):
                depends = bb.data.getVar("DEPENDS", d, 1)
		if use_cross_localedef == "1" :
	                depends = "%s cross-localedef-native" % depends
		else:
	                depends = "%s qemu-native" % depends
                bb.data.setVar("DEPENDS", depends, d)
                bb.data.setVar("GLIBC_INTERNAL_USE_BINARY_LOCALE", "compile", d)
                break
}

def get_libc_fpu_setting(bb, d):
    if bb.data.getVar('TARGET_FPU', d, 1) in [ 'soft' ]:
        return "--without-fp"
    return ""

OVERRIDES_append = ":${TARGET_ARCH}-${TARGET_OS}"

do_configure_prepend() {
        sed -e "s#@BASH@#/bin/sh#" -i ${S}/elf/ldd.bash.in
}



# indentation removed on purpose
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

# indentation removed on purpose
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

do_install() {
	oe_runmake install_root=${D} \
	libdir='${libdir}' slibdir='${base_libdir}' \
	localedir='${libdir}/locale' \
	install
	for r in ${rpcsvc}; do
		h=`echo $r|sed -e's,\.x$,.h,'`
		install -m 0644 ${S}/sunrpc/rpcsvc/$h ${D}/${includedir}/rpcsvc/
	done
	install -m 0644 ${WORKDIR}/etc/ld.so.conf ${D}/${sysconfdir}/
	install -d ${D}${libdir}/locale
	make -f ${WORKDIR}/generate-supported.mk IN="${S}/localedata/SUPPORTED" OUT="${WORKDIR}/SUPPORTED"
	# get rid of some broken files...
	for i in ${GLIBC_BROKEN_LOCALES}; do
		grep -v $i ${WORKDIR}/SUPPORTED > ${WORKDIR}/SUPPORTED.tmp
		mv ${WORKDIR}/SUPPORTED.tmp ${WORKDIR}/SUPPORTED
	done
	rm -f ${D}/etc/rpc
	rm -rf ${D}${datadir}/zoneinfo
	rm -rf ${D}${libexecdir}/getconf
	rm -rf ${D}${sysconfdir}/localtime
	install -d ${D}${sysconfdir}/init.d
	install -m 0644 ${S}/nscd/nscd.conf ${D}${sysconfdir}/
	install ${S}/nscd/nscd.init ${D}${sysconfdir}/init.d/nscd
}

TMP_LOCALE="/tmp/locale${libdir}/locale"

do_prep_locale_tree() {
	treedir=${WORKDIR}/locale-tree
	rm -rf $treedir
	mkdir -p $treedir/bin $treedir/lib $treedir/${datadir} $treedir/${libdir}/locale
	cp -pPR ${PKGD}${datadir}/i18n $treedir/${datadir}/i18n
	# unzip to avoid parsing errors
	for i in $treedir/${datadir}/i18n/charmaps/*gz; do
		gunzip $i
	done
	cp -pPR ${PKGD}${base_libdir}/* $treedir/lib
	if [ -f ${STAGING_DIR_NATIVE}${prefix_native}/lib/libgcc_s.* ]; then
		cp -pPR ${STAGING_DIR_NATIVE}/${prefix_native}/lib/libgcc_s.* $treedir/lib
	fi
	install -m 0755 ${PKGD}${bindir}/localedef $treedir/bin
}

do_collect_bins_from_locale_tree() {
	treedir=${WORKDIR}/locale-tree

	mkdir -p ${PKGD}${libdir}
	cp -pPR $treedir/${libdir}/locale ${PKGD}${libdir}
}

inherit qemu

python package_do_split_gconvs () {
	import os, re
	if (bb.data.getVar('PACKAGE_NO_GCONV', d, 1) == '1'):
		bb.note("package requested not splitting gconvs")
		return

	if not bb.data.getVar('PACKAGES', d, 1):
		return

	bpn = bb.data.getVar('BPN', d, 1)
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

	def calc_gconv_deps(fn, pkg, file_regex, output_pattern, group):
		deps = []
		f = open(fn, "r")
		c_re = re.compile('^copy "(.*)"')
		i_re = re.compile('^include "(\w+)".*')
		for l in f.readlines():
			m = c_re.match(l) or i_re.match(l)
			if m:
				dp = legitimize_package_name('%s-gconv-%s' % (bpn, m.group(1)))
				if not dp in deps:
					deps.append(dp)
		f.close()
		if deps != []:
			bb.data.setVar('RDEPENDS_%s' % pkg, " ".join(deps), d)
		if bpn != 'glibc':
			bb.data.setVar('RPROVIDES_%s' % pkg, pkg.replace(bpn, 'glibc'), d)

	do_split_packages(d, gconv_libdir, file_regex='^(.*)\.so$', output_pattern=bpn+'-gconv-%s', \
		description='gconv module for character set %s', hook=calc_gconv_deps, \
		extra_depends=bpn+'-gconv')

	def calc_charmap_deps(fn, pkg, file_regex, output_pattern, group):
		deps = []
		f = open(fn, "r")
		c_re = re.compile('^copy "(.*)"')
		i_re = re.compile('^include "(\w+)".*')
		for l in f.readlines():
			m = c_re.match(l) or i_re.match(l)
			if m:
				dp = legitimize_package_name('%s-charmap-%s' % (bpn, m.group(1)))
				if not dp in deps:
					deps.append(dp)
		f.close()
		if deps != []:
			bb.data.setVar('RDEPENDS_%s' % pkg, " ".join(deps), d)
		if bpn != 'glibc':
			bb.data.setVar('RPROVIDES_%s' % pkg, pkg.replace(bpn, 'glibc'), d)

	do_split_packages(d, charmap_dir, file_regex='^(.*)\.gz$', output_pattern=bpn+'-charmap-%s', \
		description='character map for %s encoding', hook=calc_charmap_deps, extra_depends='')

	def calc_locale_deps(fn, pkg, file_regex, output_pattern, group):
		deps = []
		f = open(fn, "r")
		c_re = re.compile('^copy "(.*)"')
		i_re = re.compile('^include "(\w+)".*')
		for l in f.readlines():
			m = c_re.match(l) or i_re.match(l)
			if m:
				dp = legitimize_package_name(bpn+'-localedata-%s' % m.group(1))
				if not dp in deps:
					deps.append(dp)
		f.close()
		if deps != []:
			bb.data.setVar('RDEPENDS_%s' % pkg, " ".join(deps), d)
		if bpn != 'glibc':
			bb.data.setVar('RPROVIDES_%s' % pkg, pkg.replace(bpn, 'glibc'), d)

	do_split_packages(d, locales_dir, file_regex='(.*)', output_pattern=bpn+'-localedata-%s', \
		description='locale definition for %s', hook=calc_locale_deps, extra_depends='')
	bb.data.setVar('PACKAGES', bb.data.getVar('PACKAGES', d) + ' ' + bpn + '-gconv', d)

	use_bin = bb.data.getVar("GLIBC_INTERNAL_USE_BINARY_LOCALE", d, 1)

	dot_re = re.compile("(.*)\.(.*)")

#GLIBC_GENERATE_LOCALES var specifies which locales to be supported, empty or "all" means all locales
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
		bb.data.setVar('RDEPENDS_%s' % pkgname, 'localedef %s-localedata-%s %s-charmap-%s' % \
		(bpn, legitimize_package_name(locale), bpn, legitimize_package_name(encoding)), d)
		bb.data.setVar('pkg_postinst_%s' % pkgname, bb.data.getVar('locale_base_postinst', d, 1) \
		% (locale, encoding, locale), d)
		bb.data.setVar('pkg_postrm_%s' % pkgname, bb.data.getVar('locale_base_postrm', d, 1) % \
		(locale, encoding, locale), d)

	def output_locale_binary_rdepends(name, pkgname, locale, encoding):
		m = re.match("(.*)_(.*)", name)
		if m:
			libc_name = "%s.%s" % (m.group(1), m.group(2).lower().replace("-",""))
		else:
			libc_name = name
		bb.data.setVar('RDEPENDS_%s' % pkgname, legitimize_package_name('%s-binary-localedata-%s' \
			% (bpn, libc_name)), d)
		rprovides = (bb.data.getVar('RPROVIDES_%s' % pkgname, d, True) or "").split()
		rprovides.append(legitimize_package_name('%s-binary-localedata-%s' % (bpn, libc_name)))
		bb.data.setVar('RPROVIDES_%s' % pkgname, " ".join(rprovides), d)

	def output_locale_binary(name, pkgname, locale, encoding):
		treedir = base_path_join(bb.data.getVar("WORKDIR", d, 1), "locale-tree")
		ldlibdir = "%s/lib" % treedir
		path = bb.data.getVar("PATH", d, 1)
		i18npath = base_path_join(treedir, datadir, "i18n")
		gconvpath = base_path_join(treedir, "iconvdata")

		use_cross_localedef = bb.data.getVar("LOCALE_GENERATION_WITH_CROSS-LOCALEDEF", d, 1) or "0"
		if use_cross_localedef == "1":
	    		target_arch = bb.data.getVar('TARGET_ARCH', d, True)
			locale_arch_options = { \
				"arm":     " --uint32-align=4 --little-endian ", \
				"armeb":     " --uint32-align=4 --big-endian ", \
				"armel":     " --uint32-align=4 --little-endian ", \
				"powerpc": " --uint32-align=4 --big-endian ",    \
				"mips":    " --uint32-align=4 --big-endian ",    \
				"mipsel":    " --uint32-align=4 --little-endian ",    \
				"mips64":    " --uint32-align=4 --big-endian ",    \
				"i386":    " --uint32-align=4 --little-endian ", \
				"i486":    " --uint32-align=4 --little-endian ", \
				"i586":    " --uint32-align=4 --little-endian ", \
				"i686":    " --uint32-align=4 --little-endian ", \
				"x86_64":  " --uint32-align=4 --little-endian "  }

			if target_arch in locale_arch_options:
				localedef_opts = locale_arch_options[target_arch]
			else:
				bb.error("locale_arch_options not found for target_arch=" + target_arch)
				raise bb.build.FuncFailed("unknown arch:" + target_arch + " for locale_arch_options")

			localedef_opts += " --force --old-style --no-archive --prefix=%s \
				--inputfile=%s/%s/i18n/locales/%s --charmap=%s %s/usr/lib/locale/%s" \
				% (treedir, treedir, datadir, locale, encoding, treedir, name)

			cmd = "PATH=\"%s\" I18NPATH=\"%s\" GCONV_PATH=\"%s\" cross-localedef %s" % \
				(path, i18npath, gconvpath, localedef_opts)
		else: # earlier slower qemu way
			qemu = qemu_target_binary(d)
			localedef_opts = "--force --old-style --no-archive --prefix=%s \
				--inputfile=%s/i18n/locales/%s --charmap=%s %s" \
				% (treedir, datadir, locale, encoding, name)

			qemu_options = bb.data.getVar("QEMU_OPTIONS_%s" % bb.data.getVar('PACKAGE_ARCH', d, 1), d, 1)
			if not qemu_options:
				qemu_options = bb.data.getVar('QEMU_OPTIONS', d, 1)

			cmd = "PSEUDO_RELOADED=YES PATH=\"%s\" I18NPATH=\"%s\" %s -L %s \
				-E LD_LIBRARY_PATH=%s %s %s/bin/localedef %s" % \
				(path, i18npath, qemu, treedir, ldlibdir, qemu_options, treedir, localedef_opts)

		bb.note("generating locale %s (%s)" % (locale, encoding))
		import subprocess
		process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		if process.wait() != 0:
			bb.note("cmd:")
			bb.note(cmd)
			bb.note("stdout:")
			bb.note(process.stdout.read())
			bb.note("stderr:")
			bb.note(process.stderr.read())
			raise bb.build.FuncFailed("localedef returned an error")

	def output_locale(name, locale, encoding):
		pkgname = 'locale-base-' + legitimize_package_name(name)
		bb.data.setVar('ALLOW_EMPTY_%s' % pkgname, '1', d)
		bb.data.setVar('PACKAGES', '%s %s' % (pkgname, bb.data.getVar('PACKAGES', d, 1)), d)
		rprovides = ' virtual-locale-%s' % legitimize_package_name(name)
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
		do_split_packages(d, binary_locales_dir, file_regex='(.*)', \
			output_pattern=bpn+'-binary-localedata-%s', \
			description='binary locale definition for %s', extra_depends='', allow_dirs=True)
	elif use_bin == "precompiled":
		do_split_packages(d, binary_locales_dir, file_regex='(.*)', \
			output_pattern=bpn+'-binary-localedata-%s', \
			description='binary locale definition for %s', extra_depends='', allow_dirs=True)
	else:
		bb.note("generation of binary locales disabled. this may break i18n!")

}

# We want to do this indirection so that we can safely 'return'
# from the called function even though we're prepending
python populate_packages_prepend () {
	if bb.data.getVar('DEBIAN_NAMES', d, 1):
		bpn = bb.data.getVar('BPN', d, 1)
		bb.data.setVar('PKG_'+bpn, 'libc6', d)
		bb.data.setVar('PKG_'+bpn+'-dev', 'libc6-dev', d)
	bb.build.exec_func('package_do_split_gconvs', d)
}
