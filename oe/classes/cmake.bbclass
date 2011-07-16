DEPENDS += " cmake-native "

# We need to unset CCACHE otherwise cmake gets too confused
CCACHE = ""

# We want the staging and installing functions from autotools
inherit autotools

# Use in-tree builds by default but allow this to be changed
# since some packages do not support them (e.g. llvm 2.5).
OECMAKE_SOURCEPATH ?= "."

# If declaring this, make sure you also set EXTRA_OEMAKE to
# "-C ${OECMAKE_BUILDPATH}". So it will run the right makefiles.
OECMAKE_BUILDPATH ?= ""

# C/C++ Compiler (without cpu arch/tune arguments)
OECMAKE_C_COMPILER ?= "`echo ${CC} | sed 's/^\([^ ]*\).*/\1/'`"
OECMAKE_CXX_COMPILER ?= "`echo ${CXX} | sed 's/^\([^ ]*\).*/\1/'`"

# Compiler flags
OECMAKE_C_FLAGS ?= "${HOST_CC_ARCH} ${TOOLCHAIN_OPTIONS} ${TARGET_CPPFLAGS}"
OECMAKE_CXX_FLAGS ?= "${HOST_CC_ARCH} ${TOOLCHAIN_OPTIONS} ${TARGET_CPPFLAGS} -fpermissive"
OECMAKE_C_FLAGS_RELEASE ?= "${SELECTED_OPTIMIZATION} -DNDEBUG"
OECMAKE_CXX_FLAGS_RELEASE ?= "${SELECTED_OPTIMIZATION} -DNDEBUG"

cmake_do_generate_toolchain_file() {
# CMake system name must be something like "Linux".
# This is important for cross-compiling.
  echo "set( CMAKE_SYSTEM_NAME" `echo ${SDK_OS} | sed 's/^./\u&/'` ")" > ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_C_COMPILER ${OECMAKE_C_COMPILER} )" >> ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_CXX_COMPILER ${OECMAKE_CXX_COMPILER} )" >> ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_C_FLAGS \"${OECMAKE_C_FLAGS}\" CACHE STRING \"OpenEmbedded CFLAGS\" )" >> ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_CXX_FLAGS \"${OECMAKE_CXX_FLAGS}\" CACHE STRING \"OpenEmbedded CXXFLAGS\" )" >> ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_C_FLAGS_RELEASE \"${OECMAKE_C_FLAGS_RELEASE}\" CACHE STRING \"CFLAGS for release\" )" >> ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_CXX_FLAGS_RELEASE \"${OECMAKE_CXX_FLAGS_RELEASE}\" CACHE STRING \"CXXFLAGS for release\" )" >> ${WORKDIR}/toolchain.cmake

# only search in the paths provided (from openembedded) so cmake doesnt pick
# up libraries and tools from the native build machine
  echo "set( CMAKE_FIND_ROOT_PATH ${STAGING_DIR_HOST} ${STAGING_DIR_NATIVE} ${STAGING_DIR_NATIVE}${prefix_native}/${BASE_PACKAGE_ARCH} )" >> ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_FIND_ROOT_PATH_MODE_PROGRAM ONLY )" >> ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY )" >> ${WORKDIR}/toolchain.cmake
  echo "set( CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY )" >> ${WORKDIR}/toolchain.cmake
# Use native cmake modules
  echo "set( CMAKE_MODULE_PATH ${STAGING_DIR_NATIVE}/usr/share/cmake-2.6/Modules/ )" >> ${WORKDIR}/toolchain.cmake
}

addtask generate_toolchain_file after do_patch before do_configure

cmake_do_configure() {
  if [ ${OECMAKE_BUILDPATH} ]
  then
    mkdir -p ${OECMAKE_BUILDPATH}
    cd ${OECMAKE_BUILDPATH}
  fi

  # Just like autotools cmake can use a site file to cache result that need generated binaries to run
  if [ -e ${WORKDIR}/site-file.cmake ] ; then
    OECMAKE_SITEFILE=" -C ${WORKDIR}/site-file.cmake"
  else 
    OECMAKE_SITEFILE=""
  fi

  cmake \
    ${OECMAKE_SITEFILE} \
    ${OECMAKE_SOURCEPATH} \
    -DCMAKE_INSTALL_PREFIX:PATH=${prefix} \
    -DCMAKE_INSTALL_SO_NO_EXE=0 \
	-DCMAKE_TOOLCHAIN_FILE=${WORKDIR}/toolchain.cmake \
	-DCMAKE_VERBOSE_MAKEFILE=1 \
    ${EXTRA_OECMAKE} \
    -Wno-dev
}

cmake_do_compile()  {
  if [ ${OECMAKE_BUILDPATH} ]
  then
     cd ${OECMAKE_BUILDPATH}
  fi
  
  base_do_compile
}

cmake_do_install() {
  if [ ${OECMAKE_BUILDPATH} ];
  then
     cd ${OECMAKE_BUILDPATH}
  fi
  
  autotools_do_install
}

EXPORT_FUNCTIONS do_configure do_compile do_install do_generate_toolchain_file
