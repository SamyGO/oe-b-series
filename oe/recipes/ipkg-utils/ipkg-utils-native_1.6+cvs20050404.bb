require ipkg-utils_${PV}.bb

RDEPENDS_${PN} = ""
PR = "r25"

inherit native

NATIVE_INSTALL_WORKS = "1"

#LocalChange: added portability patch for 'ar'
SRC_URI += "file://remove_f_from_ar_param.patch"

# Avoid circular dependencies from package_ipk.bbclass
PACKAGES = ""
FILESDIR = "${@os.path.dirname(bb.data.getVar('FILE',d,1))}/ipkg-utils"
INSTALL += "arfile.py"

do_install() {
        install -d ${D}${bindir}
        for i in ${INSTALL}; do
                install -m 0755 $i ${D}${bindir}
        done
}
