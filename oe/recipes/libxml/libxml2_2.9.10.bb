require libxml2.inc

DEPENDS = "zlib"

SRC_URI = "http://www.xmlsoft.org/sources/libxml2-${PV}.tar.gz;name=libtar \
           http://www.w3.org/XML/Test/xmlts20080827.tar.gz;subdir=${BP};name=testtar \
           file://libxml-64bit.patch \
           file://runtest.patch \
           file://run-ptest \
           file://python-sitepackages-dir.patch \
           file://libxml-m4-use-pkgconfig.patch \
           file://0001-Make-ptest-run-the-python-tests-if-python-is-enabled.patch \
           file://fix-execution-of-ptests.patch \
           file://CVE-2020-7595.patch \
           file://CVE-2019-20388.patch \
           "

SRC_URI[libtar.md5sum] = "10942a1dc23137a8aa07f0639cbfece5"
SRC_URI[libtar.sha256sum] = "aafee193ffb8fe0c82d4afef6ef91972cbaf5feea100edc2f262750611b4be1f"
SRC_URI[testtar.md5sum] = "ae3d1ebe000a3972afa104ca7f0e1b4a"
SRC_URI[testtar.sha256sum] = "96151685cec997e1f9f3387e3626d61e6284d4d6e66e0e440c209286c03e9cc7"

BINCONFIG = "${bindir}/xml2-config"

PR = "${INC_PR}.1"
