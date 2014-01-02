require gmp_${PV}.bb

FILESDIR = "${@os.path.dirname(bb.data.getVar('FILE',d,1))}/gmp-${PV}"
S = "${WORKDIR}/gmp-${PV}"

inherit native

#SamyGO: attached coreutils-native as generic native depedency
DEPENDS = "coreutils-native"

# darwin 'hacks'
EXTRA_OECONF_build-darwin = " --enable-shared "
OLD_STAGING := "${STAGING_BINDIR}"
OLD_TARGET  := "${TARGET_SYS}"
OLD_HOST    := "${HOST_SYS}"
OLD_BUILD   := "${BUILD_SYS}"

PATH_prepend_build-darwin = "${OLD_STAGING}/${OLD_HOST}:${OLD_STAGING}:"

TARGET_SYS_build-darwin   = "none-apple-darwin"
HOST_SYS_build-darwin     = "none-apple-darwin"
BUILD_SYS_build-darwin    = "none-apple-darwin"

do_compile_append_build-darwin() {
    oe_runmake check
}

#SamyGO: copy files into proper path at staging, added FORCE_LEGACY_STAGING
populate_sysroot_posthook() {
	if [ -e ${STAGING_DIR}/none-apple-darwin/ ]; then
		sed -i 's:none-apple-darwin:${OLD_HOST}:' ${STAGING_DIR}/none-apple-darwin/usr/lib/libgmp.la
		cp ${STAGING_DIR}/none-apple-darwin/usr/include/* ${STAGING_DIR}/${OLD_BUILD}/usr/include/
		cp ${STAGING_DIR}/none-apple-darwin/usr/lib/* ${STAGING_DIR}/${OLD_BUILD}/usr/lib/
	fi
}
FORCE_LEGACY_STAGING = 1
