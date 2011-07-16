# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
BitBake 'Fetch' implementation for mercurial DRCS (hg).

"""

# Copyright (C) 2003, 2004  Chris Larson
# Copyright (C) 2004        Marcin Juszkiewicz
# Copyright (C) 2007        Robert Schuster
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Based on functions from the base bb module, Copyright 2003 Holger Schurig

import os, re
import sys
import bb
from bb import data
from bb.fetch import Fetch
from bb.fetch import FetchError
from bb.fetch import MissingParameterError
from bb.fetch import runfetchcmd

class Hg(Fetch):
    """Class to fetch a from mercurial repositories"""
    def supports(self, url, ud, d):
        """
        Check to see if a given url can be fetched with mercurial.
        """
        return ud.type in ['hg']

    def localpath(self, url, ud, d):
        if not "module" in ud.parm:
            raise MissingParameterError("hg method needs a 'module' parameter")

        ud.module = ud.parm["module"]

        # Create paths to mercurial checkouts
        relpath = ud.path
        if relpath.startswith('/'):
            # Remove leading slash as os.path.join can't cope
            relpath = relpath[1:]
        ud.pkgdir = os.path.join(data.expand('${HGDIR}', d), ud.host, relpath)
        ud.moddir = os.path.join(ud.pkgdir, ud.module)

        if 'rev' in ud.parm:
            ud.revision = ud.parm['rev']

        ud.localfile = data.expand('%s_%s_%s_%s.tar.gz' % (ud.module.replace('/', '.'), ud.host, ud.path.replace('/', '.'), ud.revision), d)

        return os.path.join(data.getVar("DL_DIR", d, True), ud.localfile)

    def _buildhgcommand(self, ud, d, command):
        """
        Build up an hg commandline based on ud
        command is "fetch", "update", "info"
        """

        basecmd = data.expand('${FETCHCMD_hg}', d)

        proto = "http"
        if "proto" in ud.parm:
            proto = ud.parm["proto"]

        host = ud.host
        if proto == "file":
            host = "/"
            ud.host = "localhost"

        if not ud.user:
            hgroot = host + ud.path
        else:
            hgroot = ud.user + "@" + host + ud.path

        if command is "info":
            return "%s identify -i %s://%s/%s" % (basecmd, proto, hgroot, ud.module)

        options = [];
        if ud.revision:
            options.append("-r %s" % ud.revision)

        if command is "fetch":
            cmd = "%s clone %s %s://%s/%s %s" % (basecmd, " ".join(options), proto, hgroot, ud.module, ud.module)
        elif command is "pull":
            # do not pass options list; limiting pull to rev causes the local
            # repo not to contain it and immediately following "update" command
            # will crash
            cmd = "%s pull" % (basecmd)
        elif command is "update":
            cmd = "%s update -C %s" % (basecmd, " ".join(options))
        else:
            raise FetchError("Invalid hg command %s" % command)

        return cmd

    def go(self, loc, ud, d):
        """Fetch url"""

        # try to use the tarball stash
        if Fetch.try_mirror(d, ud.localfile):
            bb.msg.debug(1, bb.msg.domain.Fetcher, "%s already exists or was mirrored, skipping hg checkout." % ud.localpath)
            return

        bb.msg.debug(2, bb.msg.domain.Fetcher, "Fetch: checking for module directory '" + ud.moddir + "'")

        if os.access(os.path.join(ud.moddir, '.hg'), os.R_OK):
            updatecmd = self._buildhgcommand(ud, d, "pull")
            bb.msg.note(1, bb.msg.domain.Fetcher, "Update " + loc)
            # update sources there
            os.chdir(ud.moddir)
            bb.msg.debug(1, bb.msg.domain.Fetcher, "Running %s" % updatecmd)
            runfetchcmd(updatecmd, d)

        else:
            fetchcmd = self._buildhgcommand(ud, d, "fetch")
            bb.msg.note(1, bb.msg.domain.Fetcher, "Fetch " + loc)
            # check out sources there
            bb.mkdirhier(ud.pkgdir)
            os.chdir(ud.pkgdir)
            bb.msg.debug(1, bb.msg.domain.Fetcher, "Running %s" % fetchcmd)
            runfetchcmd(fetchcmd, d)
	
	# Even when we clone (fetch), we still need to update as hg's clone
	# won't checkout the specified revision if its on a branch
        updatecmd = self._buildhgcommand(ud, d, "update")
        bb.msg.debug(1, bb.msg.domain.Fetcher, "Running %s" % updatecmd)
        runfetchcmd(updatecmd, d)

        os.chdir(ud.pkgdir)
        try:
            runfetchcmd("tar -czf %s %s" % (ud.localpath, ud.module), d)
        except:
            t, v, tb = sys.exc_info()
            try:
                os.unlink(ud.localpath)
            except OSError:
                pass
            raise t, v, tb
