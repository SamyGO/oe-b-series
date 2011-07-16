DEPLOY_DIR_SRC ?= "${DEPLOY_DIR}/sources"
EXCLUDE_FROM ?= ".pc patches autom4te.cache"

# used as part of a path. make sure it's set
DISTRO ?= "openembedded"

def get_src_tree(d):

	workdir = bb.data.getVar('WORKDIR', d, 1)
	if not workdir:
		bb.error("WORKDIR not defined, unable to find source tree.")
		return

	s = bb.data.getVar('S', d, 0)
	if not s:
		bb.error("S not defined, unable to find source tree.")
		return

	s_tree_raw = s.split('/')[1]
	s_tree = bb.data.expand(s_tree_raw, d)

	src_tree_path = os.path.join(workdir, s_tree)
	try:
		os.listdir(src_tree_path)
	except OSError:
		bb.fatal("Expected to find source tree in '%s' which doesn't exist." % src_tree_path)
	bb.debug("Assuming source tree is '%s'" % src_tree_path)

	return s_tree

sourcepkg_do_create_orig_tgz(){

	mkdir -p ${DEPLOY_DIR_SRC}/${PN}/${PACKAGE_ARCH}
	cd ${WORKDIR}
	for i in ${EXCLUDE_FROM}; do
		echo $i >> temp/exclude-from-file
	done

	src_tree=$(basename ${S})
	
	echo $src_tree
	oenote "Creating .orig.tar.gz in ${DEPLOY_DIR_SRC}/${PN}/${P}.orig.tar.gz"
	tar cvzf ${DEPLOY_DIR_SRC}/${PN}/${P}.orig.tar.gz --exclude-from temp/exclude-from-file $src_tree
	cp -pPR $src_tree $src_tree.orig
}

sourcepkg_do_archive_bb() {

	src_tree=$(basename ${S})
	dest=${WORKDIR}/$src_tree/${DISTRO}
	mkdir -p $dest

	cp ${FILE} $dest
}

python sourcepkg_do_dumpdata() {

	workdir = bb.data.getVar('WORKDIR', d, 1)
	distro = bb.data.getVar('DISTRO', d, 1)
	s_tree = get_src_tree(d)
	openembeddeddir = os.path.join(workdir, s_tree, distro)
	dumpfile = os.path.join(openembeddeddir, bb.data.expand("${P}-${PR}.showdata.dump",d))
	
	try:
		os.mkdir(openembeddeddir)
	except OSError:
		# dir exists
		pass

	bb.note("Dumping metadata into '%s'" % dumpfile)
	f = open(dumpfile, "w")
	# emit variables and shell functions
        bb.data.emit_env(f, d, True)
	# emit the metadata which isnt valid shell
	for e in d.keys():
		if bb.data.getVarFlag(e, 'python', d):
			f.write("\npython %s () {\n%s}\n" % (e, bb.data.getVar(e, d, 1)))
	f.close()
}

sourcepkg_do_create_diff_gz(){

	cd ${WORKDIR}
	for i in ${EXCLUDE_FROM}; do
		echo $i >> temp/exclude-from-file
	done


	src_tree=$(basename ${S})

	for i in `find . -maxdepth 1 -type f`; do
		mkdir -p $src_tree/${DISTRO}/files
		cp $i $src_tree/${DISTRO}/files
	done
	
	oenote "Creating .diff.gz in ${DEPLOY_DIR_SRC}/${PN}/${PACKAGE_ARCH}/${P}-${PR}.diff.gz"
	LC_ALL=C TZ=UTC0 diff --exclude-from=temp/exclude-from-file -Naur $src_tree.orig $src_tree | gzip -c > ${DEPLOY_DIR_SRC}/${PN}/${PACKAGE_ARCH}/${P}-${PR}.diff.gz
	rm -rf $src_tree.orig
}

EXPORT_FUNCTIONS do_create_orig_tgz do_archive_bb do_dumpdata do_create_diff_gz

do_create_orig_tgz[deptask] = "do_unpack"
do_create_diff_gz[deptask] = "do_configure"
do_archive_bb[deptask] = "do_patch"
do_dumpdata[deptask] = "do_unpack"

addtask create_orig_tgz after do_unpack before do_patch
addtask archive_bb after do_patch before do_dumpdata
addtask dumpdata after do_archive_bb before do_create_diff_gz
addtask create_diff_gz after do_configure before do_compile

