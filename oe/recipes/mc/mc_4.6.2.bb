require mc.inc
PR = "${INC_PR}.0"
HOMEPAGE = "http://www.midnight-commander.org/"

# most of these fixes were copied from openSUSE Factory.
SRC_URI = "http://www.midnight-commander.org/downloads/${P}.tar.gz \
	   file://mhl-stdbool.patch \
	   file://mc-utf8.patch \
	   file://00-70-utf8-common.patch \
	   file://00-73-utf8-bottom-buttons-width.patch \
	   file://00-75-utf8-cmdline-help.patch \
	   file://00-76-utf8-hotlist-highlight.patch \
	   file://00-77-utf8-filename-search-highlight.patch \
	   file://mc-utf8-nlink.patch \
	   file://mc-utf8-look-and-feel.patch \
	   file://mc-utf8-slang-codeset.patch \
	   file://99_regexp-replace-fixed.patch \
	   file://99b_fix-regex-pattern-lengths.patch \
	   file://multi-press-f-keys.patch \
	   file://cross-compile.patch \
	   file://01_ftpfs_symlink.patch \
	   file://02_ignore_ftp_chmod_error.patch \
	   file://mc-cursor-appearance.patch \
	   file://mc-esc-seq.patch"

EXTRA_OECONF = "--without-x --without-samba \
--without-nfs --without-gpm-mouse --enable-charset \
ac_cv_path_PERL=${bindir}/perl \
ac_cv_path_ZIP=${bindir}/zip \
ac_cv_path_UNZIP=${bindir}/unzip \
"

do_unpack_append() {
        bb.build.exec_func('do_utf8_conversion', d)
}
do_utf8_conversion() {
	pwd
	pushd lib
	iconv -f iso8859-1 -t utf-8 -o mc.hint.tmp mc.hint && mv mc.hint.tmp mc.hint
	iconv -f iso8859-1 -t utf-8 -o mc.hint.es.tmp mc.hint.es && mv mc.hint.es.tmp mc.hint.es
	iconv -f iso8859-1 -t utf-8 -o mc.hint.it.tmp mc.hint.it && mv mc.hint.it.tmp mc.hint.it
	iconv -f iso8859-1 -t utf-8 -o mc.hint.nl.tmp mc.hint.nl && mv mc.hint.nl.tmp mc.hint.nl
	iconv -f iso8859-2 -t utf-8 -o mc.hint.cs.tmp mc.hint.cs && mv mc.hint.cs.tmp mc.hint.cs
	iconv -f iso8859-2 -t utf-8 -o mc.hint.hu.tmp mc.hint.hu && mv mc.hint.hu.tmp mc.hint.hu
	iconv -f iso8859-2 -t utf-8 -o mc.hint.pl.tmp mc.hint.pl && mv mc.hint.pl.tmp mc.hint.pl
	iconv -f iso8859-5 -t utf-8 -o mc.hint.sr.tmp mc.hint.sr && mv mc.hint.sr.tmp mc.hint.sr
	iconv -f koi8-r -t utf8 -o mc.hint.ru.tmp mc.hint.ru && mv mc.hint.ru.tmp mc.hint.ru
	iconv -f koi8-u -t utf8 -o mc.hint.uk.tmp mc.hint.uk && mv mc.hint.uk.tmp mc.hint.uk
	iconv -f big5 -t utf8 -o mc.hint.zh.tmp mc.hint.zh && mv mc.hint.zh.tmp mc.hint.zh
	iconv -f iso8859-5 -t utf-8 -o mc.menu.sr.tmp mc.menu.sr && mv mc.menu.sr.tmp mc.menu.sr
	popd
	# convert docs to utf-8
	pushd doc
	pushd es
	iconv -f iso8859-1 -t utf-8 -o mc.1.in.tmp mc.1.in && mv mc.1.in.tmp mc.1.in
	iconv -f iso8859-1 -t utf-8 -o xnc.hlp.tmp xnc.hlp && mv xnc.hlp.tmp xnc.hlp
	popd
	pushd hu
	iconv -f iso8859-2 -t utf-8 -o mc.1.in.tmp mc.1.in && mv mc.1.in.tmp mc.1.in
	iconv -f iso8859-2 -t utf-8 -o xnc.hlp.tmp xnc.hlp && mv xnc.hlp.tmp xnc.hlp
	popd
	pushd it
	iconv -f iso8859-1 -t utf-8 -o mc.1.in.tmp mc.1.in && mv mc.1.in.tmp mc.1.in
	iconv -f iso8859-1 -t utf-8 -o xnc.hlp.tmp xnc.hlp && mv xnc.hlp.tmp xnc.hlp
	popd
	pushd pl
	iconv -f iso8859-2 -t utf-8 -o mc.1.in.tmp mc.1.in && mv mc.1.in.tmp mc.1.in
	iconv -f iso8859-2 -t utf-8 -o xnc.hlp.tmp xnc.hlp && mv xnc.hlp.tmp xnc.hlp
	popd
	pushd ru
	iconv -f koi8-r -t utf-8 -o mc.1.in.tmp mc.1.in && mv mc.1.in.tmp mc.1.in
	iconv -f koi8-r -t utf-8 -o xnc.hlp.tmp xnc.hlp && mv xnc.hlp.tmp xnc.hlp
	popd
	pushd sr
	iconv -f iso8859-5 -t utf-8 -o mc.1.in.tmp mc.1.in && mv mc.1.in.tmp mc.1.in
	iconv -f iso8859-5 -t utf-8 -o xnc.hlp.tmp xnc.hlp && mv xnc.hlp.tmp xnc.hlp
	iconv -f iso8859-5 -t utf-8 -o mcserv.8.in.tmp mcserv.8.in && mv mcserv.8.in.tmp mcserv.8.in
	popd
	popd
}

#LocalChange: do not mess with target flags
export CPPFLAGS=""
export CFLAGS=""

do_configure_prepend() {

AUTOFOO="config.guess config.sub depcomp install-sh missing mkinstalldirs"

         for i in ${AUTOFOO}; do
           rm config/${i}
         done
}

SRC_URI[md5sum] = "ec92966f4d0c8b50c344fe901859ae2a"
SRC_URI[sha256sum] = "d34c913e7fff4ea61cf8640b10f9118829cc5359045a1821b6510f3c8b1be26e"
