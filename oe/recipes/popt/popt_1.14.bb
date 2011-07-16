require popt.inc
PR = "${INC_PR}.0"

SRC_URI = "\
  http://rpm5.org/files/popt/popt-${PV}.tar.gz \
"
BBCLASSEXTEND = "native"

SRC_URI[md5sum] = "4f90a07316eb825604dd10ae4f9f3f04"
SRC_URI[sha256sum] = "175be17571e9af3ad622531b494a0738ae632c60c8c6329273778b2b6fbbad74"
