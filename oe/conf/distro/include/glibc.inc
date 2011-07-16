# Add glibc to the overrides.
OVERRIDES .= ":libc-glibc"

PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}binutils = "binutils-cross"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}libc-for-gcc = "glibc"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}libc-initial = "glibc-initial"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}gcc-initial = "gcc-cross-initial"
PREFERRED_PROVIDER_virtual/${TARGET_PREFIX}gcc-intermediate = "gcc-cross-intermediate"
PREFERRED_PROVIDER_virtual/libc     = "glibc"
PREFERRED_PROVIDER_virtual/libiconv = "glibc"
PREFERRED_PROVIDER_virtual/libintl  = "glibc"
PREFERRED_PROVIDER_linux-libc-headers = "linux-libc-headers"
