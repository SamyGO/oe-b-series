require flac-cl.inc

PR = "r1"

# fixes from openSUSE:
#SamyGO: don't use that patches
#SRC_URI += "file://flac-gcc43-fixes.diff;striplevel=0 \
#            file://flac-printf-format-fix.diff;striplevel=0"

SRC_URI[md5sum] = "153c8b15a54da428d1f0fadc756c22c7"
SRC_URI[sha256sum] = "9635a44bceb478bbf2ee8a785cf6986fba525afb5fad1fd4bba73cf71f2d3edf"
