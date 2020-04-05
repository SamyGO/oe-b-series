# BB Class inspired by ebuild.sh
#
# This class will test files after installation for certain
# security issues and other kind of issues.
#
# Checks we do:
#  -Check the ownership and permissions
#  -Check the RUNTIME path for the $TMPDIR
#  -Check if .la files wrongly point to workdir
#  -Check if .pc files wrongly point to workdir
#  -Check if packages contains .debug directories or .so files
#   where they should be in -dev or -dbg
#  -Check if config.log contains traces to broken autoconf tests


#
# We need to have the scanelf utility as soon as
# possible and this is contained within the pax-utils-native.
# The package.bbclass can help us here.
#
inherit package
#MobiAqua: added findutils-native
PACKAGE_DEPENDS += "pax-utils-native desktop-file-utils-native findutils-native"
PACKAGEFUNCS += " do_package_qa "


#
# dictionary for elf headers
#
# feel free to add and correct.
#
#           TARGET_OS  TARGET_ARCH   MACHINE, OSABI, ABIVERSION, Little Endian, 32bit?
def package_qa_get_machine_dict():
    return {
            "darwin9" : { 
                        "arm" :       (   40,     0,    0,          True,          True),
                      },
            "linux" : { 
                        "arm" :       (   40,    97,    0,          True,          True),
                        "armeb":      (   40,    97,    0,          False,         True),
                        "i386":       (    3,     0,    0,          True,          True),
                        "i486":       (    3,     0,    0,          True,          True),
                        "i586":       (    3,     0,    0,          True,          True),
                        "i686":       (    3,     0,    0,          True,          True),
                        "x86_64":     (   62,     0,    0,          True,          False),
                        "ia64":       (   50,     0,    0,          True,          False),
                        "alpha":      (36902,     0,    0,          True,          False),
                        "hppa":       (   15,     3,    0,          False,         True),
                        "m68k":       (    4,     0,    0,          False,         True),
                        "mips":       (    8,     0,    0,          False,         True),
                        "mipsel":     (    8,     0,    0,          True,          True),
                        "mips64":     (    8,     0,    0,          False,         False),
                        "mips64el":   (    8,     0,    0,          True,          False),
                        "nios2":      (  113,     0,    0,          True,          True),
                        "powerpc":    (   20,     0,    0,          False,         True),
                        "powerpc64":  (   21,     0,    0,          False,         False),
                        "s390":       (   22,     0,    0,          False,         True),
                        "sh4":        (   42,     0,    0,          True,          True),
                        "sparc":      (    2,     0,    0,          False,         True),
                      },
            "linux-uclibc" : { 
                        "arm" :       (   40,    97,    0,          True,          True),
                        "armeb":      (   40,    97,    0,          False,         True),
                        "avr32":      ( 6317,     0,    0,          False,         True),
                        "i386":       (    3,     0,    0,          True,          True),
                        "i486":       (    3,     0,    0,          True,          True),
                        "i586":       (    3,     0,    0,          True,          True),
                        "i686":       (    3,     0,    0,          True,          True),
                        "x86_64":     (   62,     0,    0,          True,          False),
                        "mips":       (    8,     0,    0,          False,         True),
                        "mipsel":     (    8,     0,    0,          True,          True),
                        "mips64":     (    8,     0,    0,          False,         False),
                        "mips64el":   (    8,     0,    0,          True,          False),
                        "nios2":      (  113,     0,    0,          True,          True),
                        "powerpc":    (   20,     0,    0,          False,         True),
                        "powerpc64":  (   21,     0,    0,          False,         False),
                        "sh4":        (   42,     0,    0,          True,          True),
                      },
            "uclinux-uclibc" : {
                        "bfin":       (  106,     0,    0,          True,         True),
                      }, 
            "linux-gnueabi" : {
                        "arm" :       (   40,     0,    0,          True,          True),
                        "armeb" :     (   40,     0,    0,          False,         True),
                      },
            "linux-uclibceabi" : {
                        "arm" :       (   40,     0,    0,          True,          True),
                        "armeb" :     (   40,     0,    0,          False,         True),
                      },
            "linux-gnuspe" : {
                        "powerpc":    (   20,     0,    0,          False,         True),
                      },
            "linux-uclibcspe" : {
                        "powerpc":    (   20,     0,    0,          False,         True),
                      },

       }


# Known Error classes
# 0 - non dev contains .so
# 1 - package contains a dangerous RPATH
# 2 - package depends on debug package
# 3 - non dbg contains .so
# 4 - wrong architecture
# 5 - .la contains installed=yes or reference to the workdir
# 6 - .pc contains reference to /usr/include or workdir
# 7 - the desktop file is not valid
# 8 - .la contains reference to the workdir
# 9 - LDFLAGS ignored

def package_qa_clean_path(path,d):
    """ Remove the common prefix from the path. In this case it is the TMPDIR"""
    return path.replace(bb.data.getVar('TMPDIR',d,True),"")

def package_qa_make_fatal_error(error_class, name, path,d):
    """
    decide if an error is fatal

    TODO: Load a whitelist of known errors
    """
    return not error_class in [0, 1, 5, 7]

def package_qa_write_error(error_class, name, path, d):
    """
    Log the error
    """
    if not bb.data.getVar('QA_LOG', d):
        bb.note("a QA error occured but will not be logged because QA_LOG is not set")
        return

    ERROR_NAMES =[
        "non dev contains .so",
        "package contains RPATH (security issue!)",
        "package depends on debug package",
        "non dbg contains .debug",
        "wrong architecture",
        "evil hides inside the .la",
        "evil hides inside the .pc",
        "the desktop file is not valid",
        ".la contains reference to the workdir",
        "LDFLAGS ignored",
    ]

    log_path = os.path.join( bb.data.getVar('T', d, True), "log.qa_package" )
    f = file( log_path, "a+")
    print >> f, "%s, %s, %s" % \
             (ERROR_NAMES[error_class], name, package_qa_clean_path(path,d))
    f.close()

# Returns False is there was a fatal problem and True if we did not hit a fatal
# error
def package_qa_handle_error(error_class, error_msg, name, path, d):
    fatal = package_qa_make_fatal_error(error_class, name, path, d)
    package_qa_write_error(error_class, name, path, d)
    if fatal:
        bb.error("QA Issue with %s: %s" % (name, error_msg))
    else:
        bb.warn("QA Issue with %s: %s" % (name, error_msg))
    return not fatal

def package_qa_check_rpath(file,name,d, elf):
    """
    Check for dangerous RPATHs
    """
    if not elf:
        return True

    import bb, os
    sane = True
    scanelf = os.path.join(bb.data.getVar('STAGING_BINDIR_NATIVE',d,True),'scanelf')
    bad_dirs = [bb.data.getVar('TMPDIR', d, True) + "/work", bb.data.getVar('STAGING_DIR_TARGET', d, True)]
    bad_dir_test = bb.data.getVar('TMPDIR', d, True)
    if not os.path.exists(scanelf):
        bb.fatal("Can not check RPATH, scanelf (part of pax-utils-native) not found")

    if not bad_dirs[0] in bb.data.getVar('WORKDIR', d, True):
        bb.fatal("This class assumed that WORKDIR is ${TMPDIR}/work... Not doing any check")

    output = os.popen("%s -B -F%%r#F '%s'" % (scanelf,file))
    txt    = output.readline().split()
    for line in txt:
        for dir in bad_dirs:
            if dir in line:
                error_msg = "package %s contains bad RPATH %s in file %s, this is a security issue" % (name, line, file)
                sane = package_qa_handle_error(1, error_msg, name, file, d)

    return sane

def package_qa_check_dev(path, name,d, elf):
    """
    Check for ".so" library symlinks in non-dev packages
    """

    sane = True

    # SDK packages are special.
    for s in ['sdk', 'canadian-sdk']:
        if bb.data.inherits_class(s, d):
            return True

    if not name.endswith("-dev") and path.endswith(".so") and os.path.islink(path):
        error_msg = "non -dev package contains symlink .so: %s path '%s'" % \
                 (name, package_qa_clean_path(path,d))
        sane = package_qa_handle_error(0, error_msg, name, path, d)

    return sane

def package_qa_check_dbg(path, name,d, elf):
    """
    Check for ".debug" files or directories outside of the dbg package
    """

    sane = True

    if not "-dbg" in name:
        if '.debug' in path.split(os.path.sep):
            error_msg = "non debug package contains .debug directory: %s path %s" % \
                     (name, package_qa_clean_path(path,d))
            sane = package_qa_handle_error(3, error_msg, name, path, d)

    return sane

def package_qa_check_perm(path,name,d, elf):
    """
    Check the permission of files
    """
    sane = True
    return sane

def package_qa_check_arch(path,name,d, elf):
    """
    Check if archs are compatible
    """
    if not elf:
        return True

    sane = True
    target_os   = bb.data.getVar('TARGET_OS',   d, True)
    target_arch = bb.data.getVar('TARGET_ARCH', d, True)

    # FIXME: Cross package confuse this check, so just skip them
    for s in ['cross', 'sdk', 'canadian-cross', 'canadian-sdk']:
        if bb.data.inherits_class(s, d):
            return True

    # avoid following links to /usr/bin (e.g. on udev builds)
    # we will check the files pointed to anyway...
    if os.path.islink(path):
        return True

    #if this will throw an exception, then fix the dict above
    (machine, osabi, abiversion, littleendian, bits32) \
        = package_qa_get_machine_dict()[target_os][target_arch]

    # Check the architecture and endiannes of the binary
    if not machine == elf.machine():
        error_msg = "Architecture did not match (%d to %d) on %s" % \
                 (machine, elf.machine(), package_qa_clean_path(path,d))
        sane = package_qa_handle_error(4, error_msg, name, path, d)
    elif not littleendian == elf.isLittleEndian():
        error_msg = "Endiannes did not match (%d to %d) on %s" % \
                 (littleendian, elf.isLittleEndian(), package_qa_clean_path(path,d))
        sane = package_qa_handle_error(4, error_msg, name, path, d)

    return sane

def package_qa_check_desktop(path, name, d, elf):
    """
    Run all desktop files through desktop-file-validate.
    """
    sane = True
    env_path = bb.data.getVar('PATH', d, True)

    if path.endswith(".desktop"):
        output = os.popen("PATH=%s desktop-file-validate %s" % (env_path, path))
        # This only produces output on errors
        for l in output:
            sane = package_qa_handle_error(7, l.strip(), name, path, d)

    return sane

def package_qa_hash_style(path, name, d, elf):
    """
    Check if the binary has the right hash style...
    """

    if not elf:
        return True

    if os.path.islink(path):
        return True

    gnu_hash = "--hash-style=gnu" in bb.data.getVar('LDFLAGS', d, True)
    if not gnu_hash:
        gnu_hash = "--hash-style=both" in bb.data.getVar('LDFLAGS', d, True)
    if not gnu_hash:
        return True

    objdump = bb.data.getVar('OBJDUMP', d, True)
    env_path = bb.data.getVar('PATH', d, True)

    sane = True
    elf = False
    # A bit hacky. We do not know if path is an elf binary or not
    # we will search for 'NEEDED' or 'INIT' as this should be printed...
    # and come before the HASH section (guess!!!) and works on split out
    # debug symbols too
    for line in os.popen("LC_ALL=C PATH=%s %s -p '%s' 2> /dev/null" % (env_path, objdump, path), "r"):
        if "NEEDED" in line or "INIT" in line:
            sane = False
            elf = True
        if "GNU_HASH" in line:
            sane = True
        if "[mips32]" in line or "[mips64]" in line:
	    sane = True

    if elf and not sane:
        error_msg = "No GNU_HASH in the elf binary: '%s'" % path
        return package_qa_handle_error(9, error_msg, name, path, d)

    return True

def package_qa_check_staged(path,d):
    """
    Check staged la and pc files for sanity
      -e.g. installed being false

        As this is run after every stage we should be able
        to find the one responsible for the errors easily even
        if we look at every .pc and .la file
    """

    sane = True
    tmpdir = bb.data.getVar('TMPDIR', d, True)
    workdir = os.path.join(tmpdir, "work")

    installed = "installed=yes"
    iscrossnative = False
    pkgconfigcheck = tmpdir
    for s in ['cross', 'native', 'canadian-cross', 'canadian-native']:
        if bb.data.inherits_class(s, d):
            pkgconfigcheck = workdir
            iscrossnative = True

    # Grab the lock, find all .la and .pc files, read the content and check for
    # stuff that looks wrong
    lf = bb.utils.lockfile(bb.data.expand("${STAGING_DIR}/staging.lock", d))
    for root, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(root,file)
            if file.endswith(".la"):
                file_content = open(path).read()
                # Don't check installed status for native/cross packages
                if not iscrossnative and bb.data.getVar('LIBTOOL_HAS_SYSROOT', d, True) is "no":
                    if installed in file_content:
                        error_msg = "%s failed sanity test (installed) in path %s" % (file,root)
                        sane = package_qa_handle_error(5, error_msg, "staging", path, d)
                if workdir in file_content:
                    error_msg = "%s failed sanity test (workdir) in path %s" % (file,root)
                    sane = package_qa_handle_error(8, error_msg, "staging", path, d)
            elif file.endswith(".pc"):
                file_content = open(path).read()
                if pkgconfigcheck in file_content:
                    error_msg = "%s failed sanity test (tmpdir) in path %s" % (file,root)
                    sane = package_qa_handle_error(6, error_msg, "staging", path, d)
    bb.utils.unlockfile(lf)

    return sane

# Walk over all files in a directory and call func
def package_qa_walk(path, funcs, package,d):
    import oe.qa

    #if this will throw an exception, then fix the dict above
    target_os   = bb.data.getVar('TARGET_OS',   d, True)
    target_arch = bb.data.getVar('TARGET_ARCH', d, True)
    (machine, osabi, abiversion, littleendian, bits32) \
        = package_qa_get_machine_dict()[target_os][target_arch]

    sane = True
    for root, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(root,file)
            elf = oe.qa.ELFFile(path, bits32)
            try:
                elf.open()
            except:
                elf = None
            for func in funcs:
                if not func(path, package,d, elf):
                    sane = False

    return sane

def package_qa_check_rdepends(pkg, pkgdest, d):
    sane = True
    if not "-dbg" in pkg and not "task-" in pkg and not "-image" in pkg:
        # Copied from package_ipk.bbclass
        # boiler plate to update the data
        localdata = bb.data.createCopy(d)
        root = "%s/%s" % (pkgdest, pkg)

        bb.data.setVar('ROOT', '', localdata) 
        bb.data.setVar('ROOT_%s' % pkg, root, localdata)
        pkgname = bb.data.getVar('PKG_%s' % pkg, localdata, True)
        if not pkgname:
            pkgname = pkg
        bb.data.setVar('PKG', pkgname, localdata)

        overrides = bb.data.getVar('OVERRIDES', localdata)
        if not overrides:
            raise bb.build.FuncFailed('OVERRIDES not defined')
        overrides = bb.data.expand(overrides, localdata)
        bb.data.setVar('OVERRIDES', overrides + ':' + pkg, localdata)

        bb.data.update_data(localdata)

        # Now check the RDEPENDS
        rdepends = explode_deps(bb.data.getVar('RDEPENDS', localdata, True) or "")


        # Now do the sanity check!!!
        for rdepend in rdepends:
            if "-dbg" in rdepend:
                error_msg = "%s rdepends on %s" % (pkgname,rdepend)
                sane = package_qa_handle_error(2, error_msg, pkgname, rdepend, d)

    return sane

# The PACKAGE FUNC to scan each package
python do_package_qa () {
    bb.debug(2, "DO PACKAGE QA")
    pkgdest = bb.data.getVar('PKGDEST', d, True)
    packages = bb.data.getVar('PACKAGES',d, True)

    # no packages should be scanned
    if not packages:
        return

    # MobiAqua: workaround for omap4 firmware files
    if bb.data.getVar('INSANE_SKIP', d, True):
        return

    checks = [package_qa_check_dev,
              package_qa_check_perm, package_qa_check_arch,
              package_qa_check_desktop, package_qa_hash_style,
              package_qa_check_dbg]
    walk_sane = True
    rdepends_sane = True
    for package in packages.split():
        if bb.data.getVar('INSANE_SKIP_' + package, d, True):
            bb.note("package %s skipped" % package)
            continue

        bb.debug(1, "Checking Package: %s" % package)
        path = "%s/%s" % (pkgdest, package)
        if not package_qa_walk(path, checks, package, d):
            walk_sane  = False
        if not package_qa_check_rdepends(package, pkgdest, d):
            rdepends_sane = False

    if not walk_sane or not rdepends_sane:
        bb.fatal("QA run found fatal errors. Please consider fixing them.")
    bb.debug(2, "DONE with PACKAGE QA")
}


# The Staging Func, to check all staging
addtask qa_staging after do_populate_sysroot before do_package_stage
python do_qa_staging() {
    bb.debug(2, "QA checking staging")

    if not package_qa_check_staged(bb.data.getVar('STAGING_LIBDIR',d,True), d):
        bb.fatal("QA staging was broken by the package built above")
}

# Check broken config.log files
addtask qa_configure after do_configure before do_compile
python do_qa_configure() {
    configs = []
    bb.debug(1, "Checking sanity of the config.log file")
    for root, dirs, files in os.walk(bb.data.getVar('WORKDIR', d, True)):
        if ".pc" in root:
            continue
        statement = "grep 'CROSS COMPILE Badness:' %s > /dev/null" % \
                    os.path.join(root,"config.log")
        if "config.log" in files:
            if os.system(statement) == 0:
                bb.fatal("""This autoconf log indicates errors, it looked at host includes.
Rerun configure task after fixing this. The path was '%s'""" % root)

        if "configure.ac" in files:
            configs.append(os.path.join(root,"configure.ac"))
        if "configure.in" in files:
            configs.append(os.path.join(root, "configure.in"))

    if "gettext" not in bb.data.getVar('P', d, True):
       if bb.data.inherits_class('native', d) or bb.data.inherits_class('cross', d) or bb.data.inherits_class('crosssdk', d) or bb.data.inherits_class('nativesdk', d):
          gt = "gettext-native"
       elif bb.data.inherits_class('cross-canadian', d):
          gt = "gettext-nativesdk"
       else:
          gt = "gettext"
       deps = bb.utils.explode_deps(bb.data.getVar('DEPENDS', d, True) or "")
       if gt not in deps:
          for config in configs:
              gnu = "grep \"^[[:space:]]*AM_GNU_GETTEXT\" %s >/dev/null" % config
              if os.system(gnu) == 0:
                 bb.note("""Gettext required but not in DEPENDS for file %s.
Missing 'inherit gettext' in recipe?""" % config)
}
