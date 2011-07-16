require glib.inc
PR = "${INC_PR}.2"

SRC_URI = "\
  http://ftp.gnome.org/pub/GNOME/sources/glib/2.22/glib-${PV}.tar.bz2 \
  file://glibconfig-sysdefs.h \
  file://configure-libtool.patch \
  file://bug-556515.patch \
  file://g_once_init_enter.patch \
  file://uclibc-res_query.patch \
"


SRC_URI_append_arm = " file://atomic-thumb.patch \
"
SRC_URI_append_armv6 = " file://gatomic_armv6.patch"
SRC_URI_append_armv7a = " file://gatomic_armv6.patch" 

SRC_URI[md5sum] = "12297a7da577321647b38ade0593cb3c"
SRC_URI[sha256sum] = "4898d340c830a5903115412ec5b95eb03b410efdfb1c5316d36f12f8be85577d"
