#
# Creates a root filesystem out of rpm packages
#

ROOTFS_PKGMANAGE = "rpm yum"

ROOTFS_PKGMANAGE_BOOTSTRAP  = "run-postinsts"

do_rootfs[depends] += "rpm-native:do_populate_sysroot yum-native:do_populate_sysroot createrepo-native:do_populate_sysroot fakechroot-native:do_populate_sysroot"
do_rootfs[recrdeptask] += "do_package_write_rpm"

YUMCONF = "${IMAGE_ROOTFS}/etc/yum.conf"
YUMARGS = "-c ${YUMCONF} --installroot ${IMAGE_ROOTFS}"
export YUM_ARCH_FORCE = "${TARGET_ARCH}"

AWKPOSTINSTSCRIPT = "${STAGING_BINDIR_NATIVE}/extract-postinst.awk"

RPM_PREPROCESS_COMMANDS = ""
RPM_POSTPROCESS_COMMANDS = "rpm_insert_feeds_uris"

rpm_insert_feeds_uris () {

        echo "Building from feeds activated!"

	mkdir -p ${IMAGE_ROOTFS}/etc/yum/repos.d/
        for line in ${RPM_FEED_URIS}
        do
                # strip leading and trailing spaces/tabs, then split into name and uri
                line_clean="`echo "$line"|sed 's/^[ \t]*//;s/[ \t]*$//'`"
                feed_name="`echo "$line_clean" | sed -n 's/\(.*\)##\(.*\)/\1/p'`"
                feed_uri="`echo "$line_clean" | sed -n 's/\(.*\)##\(.*\)/\2/p'`"

                echo "Added $feed_name feed with URL $feed_uri"

		FEED_FILE=${IMAGE_ROOTFS}/etc/yum/repos.d/$feed_name

		echo "[${DISTRO}-feed-$feed_name]" >> $FEED_FILE
		echo "name = $feed_name" >> $FEED_FILE
		echo "baseurl = $feed_uri" >> $FEED_FILE
		echo "gpgcheck = 0" >> $FEED_FILE
        done
}

fakeroot rootfs_rpm_do_rootfs () {
	set -x

	${RPM_PREPROCESS_COMMANDS}

	mkdir -p ${IMAGE_ROOTFS}/etc/rpm/
	echo "${TARGET_ARCH}-linux" >${IMAGE_ROOTFS}/etc/rpm/platform

	# Generate an apprpriate yum.conf
	rm -rf ${YUMCONF}
	cat > ${YUMCONF} << EOF
[main]
cachedir=/var/cache2/yum
keepcache=1
debuglevel=10
logfile=/var/log2/yum.log
exactarch=0
obsoletes=1
tolerant=1

EOF

	#priority=1
	mkdir -p ${IMAGE_ROOTFS}${DEPLOY_DIR_RPM}

	for arch in ${PACKAGE_ARCHS}; do
		if [ ! -d ${DEPLOY_DIR_RPM}/$arch ]; then
			continue;
		fi
		createrepo ${DEPLOY_DIR_RPM}/$arch

		echo "[${DISTRO}-feed-$arch]" >> ${YUMCONF}
		echo "name = ${DISTRO} RPM $arch Feed" >> ${YUMCONF}
		echo "baseurl=file://${DEPLOY_DIR_RPM}/$arch" >> ${YUMCONF}
		echo "gpgcheck=0" >> ${YUMCONF}
		echo "" >> ${YUMCONF}
		#priority=$(expr $priority + 5)

		# Copy the packages into the target image
		# Ugly ugly ugly but rpm is braindead and can't see outside the chroot
		# when installing :(
		cp -r ${DEPLOY_DIR_RPM}/$arch ${IMAGE_ROOTFS}${DEPLOY_DIR_RPM}/
	done

	# Uclibc builds don't provide this stuff...
	if [ x${TARGET_OS} = "xlinux" ] || [ x${TARGET_OS} = "xlinux-gnueabi" ] ; then 
		if [ ! -z "${LINGUAS_INSTALL}" ]; then
			for i in ${LINGUAS_INSTALL}; do
				fakechroot yum ${YUMARGS} -y install $i 
			done
		fi
	fi
	if [ ! -z "${PACKAGE_INSTALL}" ]; then
		fakechroot yum ${YUMARGS} -y install ${PACKAGE_INSTALL}
	fi

	# Add any recommended packages to the image
	# (added as an extra script since yum itself doesn't support this)
	yum-install-recommends.py ${IMAGE_ROOTFS} "fakechroot yum ${YUMARGS} -y install"

	# Symlinks created under fakeroot are wrong, now we have to fix them...
	cd ${IMAGE_ROOTFS}
	for f in `find . -type l -print`
	do
		link=`readlink $f | sed -e 's#${IMAGE_ROOTFS}##'`
		rm $f
		ln -s $link $f
	done

	export D=${IMAGE_ROOTFS}
	export OFFLINE_ROOT=${IMAGE_ROOTFS}
	export IPKG_OFFLINE_ROOT=${IMAGE_ROOTFS}
	export OPKG_OFFLINE_ROOT=${IMAGE_ROOTFS}

	${ROOTFS_POSTINSTALL_COMMAND}

	mkdir -p ${IMAGE_ROOTFS}/etc/rpm-postinsts/
	rpm --root ${IMAGE_ROOTFS} -aq --queryformat 'Name: %{NAME}\n' --scripts > ${IMAGE_ROOTFS}/etc/rpm-postinsts/combined
	awk -f ${AWKPOSTINSTSCRIPT} < ${IMAGE_ROOTFS}/etc/rpm-postinsts/combined
	rm ${IMAGE_ROOTFS}/etc/rpm-postinsts/combined	

	for i in ${IMAGE_ROOTFS}/etc/rpm-postinsts/*.sh; do
		if [ -f $i ] && sh $i; then
			# rm $i
			mv $i $i.done
		fi
	done

	install -d ${IMAGE_ROOTFS}/${sysconfdir}/rcS.d
	# Stop $i getting expanded below...
	i=\$i
	cat > ${IMAGE_ROOTFS}${sysconfdir}/rcS.d/S98configure << EOF
#!/bin/sh
for i in /etc/rpm-postinsts/*.sh; do
	echo "Running postinst $i..."
	if [ -f $i ] && sh $i; then
		# rm $i
		mv $i $i.done
	else
		echo "ERROR: postinst $i failed."
	fi
done
rm -f ${sysconfdir}/rcS.d/S98configure
EOF
	chmod 0755 ${IMAGE_ROOTFS}${sysconfdir}/rcS.d/S98configure

	install -d ${IMAGE_ROOTFS}/${sysconfdir}
	echo ${BUILDNAME} > ${IMAGE_ROOTFS}/${sysconfdir}/version

	${RPM_POSTPROCESS_COMMANDS}
	${ROOTFS_POSTPROCESS_COMMAND}
	
	rm -rf ${IMAGE_ROOTFS}/var/cache2/
	rm -rf ${IMAGE_ROOTFS}/var/run2/
	rm -rf ${IMAGE_ROOTFS}/var/log2/
	rm -rf ${IMAGE_ROOTFS}${DEPLOY_DIR_RPM}/

	# remove lock files
	rm -f ${IMAGE_ROOTFS}/var/lib/rpm/__db.*

	# remove no longer used yum.conf
	rm -f ${IMAGE_ROOTFS}/etc/yum.conf

	log_check rootfs
}

rootfs_rpm_log_check() {
	target="$1"
        lf_path="$2"

	lf_txt="`cat $lf_path`"
	for keyword_die in "Cannot find package" "exit 1" ERR Fail
	do
		if (echo "$lf_txt" | grep -v log_check | grep "$keyword_die") >/dev/null 2>&1
		then
			echo "log_check: There were error messages in the logfile"
			echo -e "log_check: Matched keyword: [$keyword_die]\n"
			echo "$lf_txt" | grep -v log_check | grep -C 5 -i "$keyword_die"
			echo ""
			do_exit=1
		fi
	done
	test "$do_exit" = 1 && exit
	true
}

remove_packaging_data_files() {
# empty for now
	:
}

install_all_locales() {
# empty for now
	:
}

python () {
    import bb
    if bb.data.getVar('BUILD_IMAGES_FROM_FEEDS', d, True):
        flags = bb.data.getVarFlag('do_rootfs', 'recrdeptask', d)
        flags = flags.replace("do_package_write_rpm", "")
        flags = flags.replace("do_deploy", "")
        flags = flags.replace("do_populate_sysroot", "")
        bb.data.setVarFlag('do_rootfs', 'recrdeptask', flags, d)
        bb.data.setVar('RPM_PREPROCESS_COMMANDS', "rpm_insert_feed_uris", d)
        bb.data.setVar('RPM_POSTPROCESS_COMMANDS', '', d)
}
