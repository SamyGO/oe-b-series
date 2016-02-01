include zlib.inc

PR = "${INC_PR}.0"

SRC_URI += "	file://visibility.patch \
		file://autotools.patch "

SRC_URI[md5sum] = "debc62758716a169df9f62e6ab2bc634"
SRC_URI[sha256sum] = "1795c7d067a43174113fdf03447532f373e1c6c57c08d61d9e4e9be5e244b05e"
