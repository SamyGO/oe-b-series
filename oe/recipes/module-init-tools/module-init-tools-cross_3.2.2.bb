require module-init-tools.inc
inherit cross
DEFAULT_PREFERENCE = "0"
#LocalChange: added virtual/${TARGET_PREFIX}depmod-1.0
PROVIDES += "virtual/${TARGET_PREFIX}depmod virtual/${TARGET_PREFIX}depmod-1.0 virtual/${TARGET_PREFIX}depmod-2.6"

# Remove the RDEPENDS_${PN} we picked up from the "require";
# it's simply extraneous for the cross package
RDEPENDS_${PN} = ""

EXTRA_OECONF_append = " --program-prefix=${TARGET_PREFIX}"

do_install_append () {
        mv ${D}${bindir}/${TARGET_PREFIX}depmod ${D}${bindir}/${TARGET_PREFIX}depmod-2.6
}

#LocalChange: fixed build on Mac OS X
SRC_URI += "file://fix_build_native_nonlinux.patch"

SRC_URI[md5sum] = "a1ad0a09d3231673f70d631f3f5040e9"
SRC_URI[sha256sum] = "c080f7e42e60456eab33051026da388b5d21a360e9d2bee26ce9991427a758aa"
