#
# mountnfs.sh	Now that TCP/IP is configured, mount the NFS file
#		systems in /etc/fstab if needed. If possible,
#		start the portmapper before mounting (this is needed for
#		Linux 2.1.x and up).
#
#		Also mounts SBM filesystems now, so the name of
#		this script is getting increasingly inaccurate.
#
# Version:	@(#)mountnfs.sh  2.83  05-Oct-2001  miquels@cistron.nl
#

. /etc/default/rcS

#
#	Run in a subshell because of I/O redirection.
#
test -f /etc/fstab && (

#
#	Read through fstab line by line. If it is NFS, set the flag
#	for mounting NFS filesystems. If any NFS partition is found and it
#	not mounted with the nolock option, we start the portmapper.
#
portmap=no
mount_nfs=no
mount_smb=no
mount_ncp=no
while read device mountpt fstype options
do
	case "$device" in
		""|\#*)
			continue
			;;
	esac

	case "$options" in
		*noauto*)
			continue
			;;
	esac

	if test "$fstype" = nfs
	then
		mount_nfs=yes
		case "$options" in
			*nolock*)
				;;
			*)
				portmap=yes
				;;
		esac
	fi
	if test "$fstype" = smbfs
	then
		mount_smb=yes
	fi
	if test "$fstype" = ncpfs
	then
		mount_ncp=yes
	fi
done

exec 0>&1

if test "$portmap" = yes
then
	if test -x /sbin/portmap
	then
		echo -n "Starting portmapper... "
		start-stop-daemon --start --quiet --exec /sbin/portmap
		sleep 2
	fi
fi

if test "$mount_nfs" = yes || test "$mount_smb" = yes || test "$mount_ncp" = yes
then
	echo "Mounting remote filesystems..."
	test "$mount_nfs" = yes && mount -a -t nfs
	test "$mount_smb" = yes && mount -a -t smbfs
	test "$mount_ncp" = yes && mount -a -t ncpfs
fi

) < /etc/fstab

: exit 0

