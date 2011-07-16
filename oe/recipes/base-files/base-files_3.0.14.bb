DESCRIPTION = "Miscellaneous files for the base system."
SECTION = "base"
PRIORITY = "required"
PR = "r96"
LICENSE = "GPL"

SRC_URI = " \
           file://nsswitch.conf \
           file://motd \
           file://inputrc \
           file://host.conf \
           file://profile \
           file://fstab \
           file://filesystems \
           file://issue.net \
           file://issue \
           file://usbd \
           file://share/dot.bashrc \
           file://share/dot.profile \
           file://licenses/BSD \
           file://licenses/GPL-2 \
           file://licenses/GPL-3 \
           file://licenses/LGPL-2 \
           file://licenses/LGPL-2.1 \
           file://licenses/LGPL-3 \
           file://licenses/GFDL-1.2 \
           file://licenses/Artistic "
S = "${WORKDIR}"

docdir_append = "/${P}"
dirs1777 = "/tmp ${localstatedir}/volatile/lock ${localstatedir}/volatile/tmp"
dirs2775 = "/home ${prefix}/src ${localstatedir}/local"
dirs755 = "/bin /boot /dev ${sysconfdir} ${sysconfdir}/default \
	   ${sysconfdir}/skel /lib /mnt /proc /home/root /sbin \
	   ${prefix} ${bindir} ${docdir} /usr/games ${includedir} \
	   ${libdir} ${sbindir} ${datadir} \
	   ${datadir}/common-licenses ${datadir}/dict ${infodir} \
	   ${mandir} ${datadir}/misc ${localstatedir} \
	   ${localstatedir}/backups ${localstatedir}/lib \
	   /sys ${localstatedir}/lib/misc ${localstatedir}/spool \
	   ${localstatedir}/volatile ${localstatedir}/volatile/cache \
	   ${localstatedir}/volatile/lock/subsys \
	   ${localstatedir}/volatile/log \
	   ${localstatedir}/volatile/run \
	   /mnt /media /media/card /media/cf /media/net /media/ram \
	   /media/union /media/realroot /media/hdd \
	   /media/mmc1"

dirs755_micro = "/dev /proc /sys ${sysconfdir}"
dirs2775_micro = ""
dirs1777_micro = "/tmp"

media = "card cf net ram"
media_micro = ""
media_samygo = ""

volatiles = "cache run log lock tmp"
conffiles = "${sysconfdir}/debian_version ${sysconfdir}/host.conf \
	     ${sysconfdir}/inputrc ${sysconfdir}/issue /${sysconfdir}/issue.net \
	     ${sysconfdir}/nsswitch.conf ${sysconfdir}/profile \
	     ${sysconfdir}/default"

#
# set standard hostname, might be a candidate for a DISTRO variable? :M:
#
hostname = "openembedded"
hostname_slugos = "nslu2"
hostname_mnci = "MNCI"
hostname_rt3000 = "MNRT"
hostname_jlime = "JLime"
hostname_samygo = "localhost"

do_install () {
	for d in ${dirs755}; do
		install -m 0755 -d ${D}$d
	done
	for d in ${dirs1777}; do
		install -m 1777 -d ${D}$d
	done
	for d in ${dirs2775}; do
		install -m 2755 -d ${D}$d
	done
	for d in ${volatiles}; do
                if [ -d ${D}${localstatedir}/volatile/$d ]; then
                        ln -sf volatile/$d ${D}/${localstatedir}/$d
                fi
	done
	for d in ${media}; do
		ln -sf /media/$d ${D}/mnt/$d
	done

	if [ -n "${MACHINE}" -a "${hostname}" = "openembedded" ]; then
		echo ${MACHINE} > ${D}${sysconfdir}/hostname
	else
		echo ${hostname} > ${D}${sysconfdir}/hostname
	fi

        if [ "${DISTRO}" != "micro" -a "${DISTRO}" != "micro-uclibc" ]; then
                install -m 644 ${WORKDIR}/issue*  ${D}${sysconfdir}  

                if [ -n "${DISTRO_NAME}" ]; then
        		echo -n "${DISTRO_NAME} " >> ${D}${sysconfdir}/issue
        		echo -n "${DISTRO_NAME} " >> ${D}${sysconfdir}/issue.net
        		if [ -n "${DISTRO_VERSION}" ]; then
        			echo -n "${DISTRO_VERSION} " >> ${D}${sysconfdir}/issue
        			echo -n "${DISTRO_VERSION} " >> ${D}${sysconfdir}/issue.net
        		fi
        		echo "\n \l" >> ${D}${sysconfdir}/issue
        		echo >> ${D}${sysconfdir}/issue
        		echo "%h"    >> ${D}${sysconfdir}/issue.net
        		echo >> ${D}${sysconfdir}/issue.net
        	else
 	                install -m 0644 ${WORKDIR}/issue ${D}${sysconfdir}/issue
                        install -m 0644 ${WORKDIR}/issue.net ${D}${sysconfdir}/issue.net
                fi

                install -m 0644 ${WORKDIR}/fstab ${D}${sysconfdir}/fstab
        	install -m 0644 ${WORKDIR}/filesystems ${D}${sysconfdir}/filesystems
        	install -m 0644 ${WORKDIR}/usbd ${D}${sysconfdir}/default/usbd
        	install -m 0644 ${WORKDIR}/profile ${D}${sysconfdir}/profile
        	install -m 0755 ${WORKDIR}/share/dot.profile ${D}${sysconfdir}/skel/.profile
        	install -m 0755 ${WORKDIR}/share/dot.bashrc ${D}${sysconfdir}/skel/.bashrc
        	install -m 0644 ${WORKDIR}/inputrc ${D}${sysconfdir}/inputrc
        	install -m 0644 ${WORKDIR}/motd ${D}${sysconfdir}/motd
        	for license in BSD GPL-2 LGPL-2 LGPL-2.1 Artistic GPL-3 LGPL-3 GFDL-1.2; do
	        	install -m 0644 ${WORKDIR}/licenses/$license ${D}${datadir}/common-licenses/
        	done

	        ln -sf /proc/mounts ${D}${sysconfdir}/mtab
        	install -m 0644 ${WORKDIR}/host.conf ${D}${sysconfdir}/host.conf
        fi

	install -m 0644 ${WORKDIR}/nsswitch.conf ${D}${sysconfdir}/nsswitch.conf
}


do_install_append_mnci () {
	rmdir ${D}/tmp
	ln -s var/tmp ${D}/tmp
}

do_install_append_nylon() {
	printf "" "" >${D}${sysconfdir}/resolv.conf
	rm -r ${D}/mnt/*
	rm -r ${D}/media
	rm -rf ${D}/tmp
	ln -sf /var/tmp ${D}/tmp
}

do_install_append_slugos() {
	printf "" "" >${D}${sysconfdir}/resolv.conf
	rm -r ${D}/mnt/*
	rmdir ${D}/home/root
	install -m 0755 -d ${D}/root
	ln -s ../root ${D}/home/root
}

do_install_append_netbook-pro () {
	mkdir -p ${D}/initrd
}

PACKAGES = "${PN}-dbg ${PN}-doc ${PN}"
FILES_${PN} = "/*"
FILES_${PN}-doc = "${docdir} ${datadir}/common-licenses"

# M&N specific packaging
PACKAGE_ARCH_mnci = "mnci"
PACKAGE_ARCH_rt3000 = "rt3000"

PACKAGE_ARCH = "${MACHINE_ARCH}"

CONFFILES_${PN} = "${sysconfdir}/fstab ${sysconfdir}/hostname"
CONFFILES_${PN}_micro = ""
CONFFILES_${PN}_nylon = "${sysconfdir}/resolv.conf ${sysconfdir}/fstab ${sysconfdir}/hostname"
CONFFILES_${PN}_slugos = "${sysconfdir}/resolv.conf ${sysconfdir}/fstab ${sysconfdir}/hostname"

