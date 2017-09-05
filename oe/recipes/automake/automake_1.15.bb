require automake.inc
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=751419260aa954499f7abaabaa882bbe"
DEPENDS_class-native = "autoconf-native"

RDEPENDS_${PN}_class-native = "autoconf-native"

SRC_URI += " file://python-libdir.patch \
            file://buildtest.patch \
            file://performance.patch \
            file://new_rt_path_for_test-driver.patch \
            file://0001-automake-port-to-Perl-5.22-and-later.patch \
            "

SRC_URI[automake.md5sum] = "716946a105ca228ab545fc37a70df3a3"
SRC_URI[automake.sha256sum] = "7946e945a96e28152ba5a6beb0625ca715c6e32ac55f2e353ef54def0c8ed924"

BBCLASSEXTEND = "native"
