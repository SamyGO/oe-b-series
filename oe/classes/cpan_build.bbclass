#
# This is for perl modules that use the new Build.PL build system
#
inherit cpan-base

NATIVE_INSTALL_WORKS = "1"

#
# We also need to have built libmodule-build-perl-native for
# everything except libmodule-build-perl-native itself (which uses
# this class, but uses itself as the provider of
# libmodule-build-perl)
#
def cpan_build_deps(d):
	if bb.data.getVar('CPAN_BUILD_DEPS', d, 1):
		return ''
	pn = bb.data.getVar('PN', d, 1)
	if pn in ['libmodule-build-perl', 'libmodule-build-perl-native']:
		return ''
	return 'libmodule-build-perl-native '

DEPENDS_prepend = "${@cpan_build_deps(d)}"

cpan_build_do_configure () {
	if [ ${@is_target(d)} == "yes" ]; then
		# build for target
		. ${STAGING_LIBDIR}/perl/config.sh
		perl Build.PL --installdirs vendor \
			--destdir ${D} \
			--install_path lib="${datadir}/perl5" \
			--install_path arch="${libdir}/perl5" \
			--install_path script=${bindir} \
			--install_path bin=${bindir} \
			--install_path bindoc=${mandir}/man1 \
			--install_path libdoc=${mandir}/man3
	else
		# build for host
		perl Build.PL --installdirs site
	fi
}

cpan_build_do_compile () {
        perl Build
}

cpan_build_do_install () {
	if [ ${@is_target(d)} == "yes" ]; then
		perl Build install
	else
		perl Build install destdir="${WORKDIR}/image"
	fi
}

EXPORT_FUNCTIONS do_configure do_compile do_install
