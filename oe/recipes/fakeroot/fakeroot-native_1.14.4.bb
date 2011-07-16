require fakeroot_${PV}.bb

S = "${WORKDIR}/fakeroot-${PV}"

inherit native

EXTRA_OECONF = " --program-prefix="

#LocalChange: don't depend on util-linux from native
RDEPENDS = ""

# Compatability for the rare systems not using or having SYSV
python () {
    if bb.data.getVar('HOST_NONSYSV', d, True) and bb.data.getVar('HOST_NONSYSV', d, True) != '0':
        bb.data.setVar('EXTRA_OECONF', ' --with-ipc=tcp --program-prefix= ', d)
}

do_stage_append () {
    oe_libinstall -so libfakeroot ${STAGING_LIBDIR}/libfakeroot/
}

