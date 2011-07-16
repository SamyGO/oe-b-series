require mesa-common.inc
require mesa-${PV}.inc
require mesa-xlib.inc
PR = "${INC_PR}.0"

SRC_URI_append_samygo += "file://fix-compile.patch "
