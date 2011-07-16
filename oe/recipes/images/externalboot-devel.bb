
require externalboot-common.inc

DEPENDS_append = " xserver-xorg "
INSTALL_PKGS_append = " x11vnc xserver-xorg-extension-glx xserver-xorg-extension-dri2 xserver-xorg-xvfb xterm \
	openbox openbox-theme-clearlooks binutils gcc make patch m4 gdb python perl gdbserver automake autoconf \
	bison coreutils file gawk libtool pkgconfig sed expat fakeroot gettext ncurses openssl readline grep \
	strace ltrace git subversion screen dropbear findutils mc time usbutils vim libsdl-x11 libx11-dev \
	bzip2-dev curl-dev db-dev libelf-dev libpng-dev libstdc++-dev openssl-dev ncurses-dev jpeg-dev zlib-dev \
	libusb-dev libsdl-x11-dev libsqlite-dev gcc-symlinks g++-symlinks cpp-symlinks binutils-symlinks \
	perl-module-config-heavy perl-module-threads perl-module-thread-queue fakeroot-dev perl-module-attributes \
"

IMAGE_FSTYPES = "tar.gz"
IMAGE_BASENAME = "externalboot-devel"
IMAGE_LINGUAS = ""
IMAGE_INSTALL = "${INSTALL_PKGS} "

BUILD_ALL_DEPS = "1"
