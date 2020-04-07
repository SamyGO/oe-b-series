require automake.inc
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe"
DEPENDS_class-native = "autoconf-native"

RDEPENDS_${PN}_class-native = "autoconf-native"

SRC_URI += "file://python-libdir.patch \
            file://buildtest.patch \
            file://performance.patch \
            file://new_rt_path_for_test-driver.patch \
            file://automake-replace-w-option-in-shebangs-with-modern-use-warnings.patch \
            file://0001-automake-Add-default-libtool_tag-to-cppasm.patch \
            file://0001-build-fix-race-in-parallel-builds.patch \
"

SRC_URI[automake.md5sum] = "83cc2463a4080efd46a72ba2c9f6b8f5"
SRC_URI[automake.sha256sum] = "608a97523f97db32f1f5d5615c98ca69326ced2054c9f82e65bade7fc4c9dea8"

BBCLASSEXTEND = "native"
