OVERRIDES .= ":${FEED_ARCH}"

ARM_KEEP_OABI = "0"
LOCALE_UTF8_ONLY = "1"

PREFERRED_VERSION_gcc-cross = "4.2.0-4.0.9"
PREFERRED_VERSION_gcc-cross-initial = "4.2.0-4.0.9"
PREFERRED_VERSION_gcc-cross-intermediate = "4.2.0-4.0.9"
PREFERRED_VERSION_binutils = "2.17.50"
PREFERRED_VERSION_binutils-cross = "2.17.50"
PREFERRED_VERSION_linux-libc-headers = "2.6.18"
PREFERRED_VERSION_glibc = "2.5.90-9.0.9"
PREFERRED_VERSION_glibc-initial = "2.5.90-9.0.9"

require conf/distro/include/sane-toolchain-glibc.inc
