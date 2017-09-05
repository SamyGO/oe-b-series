require libxml2.inc

DEPENDS = "zlib"

SRC_URI = "ftp://xmlsoft.org/libxml2/libxml2-${PV}.tar.gz;name=libtar \
           http://www.w3.org/XML/Test/xmlts20080827.tar.gz;name=testtar \
           file://libxml-64bit.patch \
           file://ansidecl.patch \
           file://runtest.patch \
           file://run-ptest \
           file://python-sitepackages-dir.patch \
           file://libxml-m4-use-pkgconfig.patch \
           file://libxml2-fix_node_comparison.patch \
           file://libxml2-CVE-2016-5131.patch \
           file://libxml2-CVE-2016-4658.patch \
           file://libxml2-fix_NULL_pointer_derefs.patch \
           file://CVE-2016-9318.patch \
          "

SRC_URI[libtar.md5sum] = "ae249165c173b1ff386ee8ad676815f5"
SRC_URI[libtar.sha256sum] = "ffb911191e509b966deb55de705387f14156e1a56b21824357cdf0053233633c"
SRC_URI[testtar.md5sum] = "ae3d1ebe000a3972afa104ca7f0e1b4a"
SRC_URI[testtar.sha256sum] = "96151685cec997e1f9f3387e3626d61e6284d4d6e66e0e440c209286c03e9cc7"

BINCONFIG = "${bindir}/xml2-config"

PR = "${INC_PR}.1"
