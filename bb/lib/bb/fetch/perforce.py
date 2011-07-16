# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
BitBake 'Fetch' implementations

Classes for obtaining upstream sources for the
BitBake build tools.

"""

# Copyright (C) 2003, 2004  Chris Larson
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
import bb
from   bb import data
from   bb.fetch import Fetch
from   bb.fetch import FetchError
from   bb.fetch import MissingParameterError

class Perforce(Fetch):
    def supports(self, url, ud, d):
        return ud.type in ['p4']

    def doparse(url,d):
        parm = {}
        path = url.split("://")[1]
        delim = path.find("@");
        if delim != -1:
            (user,pswd,host,port) = path.split('@')[0].split(":")
            path = path.split('@')[1]
        else:
            (host,port) = data.getVar('P4PORT', d).split(':')
            user = ""
            pswd = ""

        if path.find(";") != -1:
            keys=[]
            values=[]
            plist = path.split(';')
            for item in plist:
                if item.count('='):
                    (key,value) = item.split('=')
                    keys.append(key)
                    values.append(value)

            parm = dict(zip(keys,values))
        path = "//" + path.split(';')[0]
        host += ":%s" % (port)
        parm["cset"] = Perforce.getcset(d, path, host, user, pswd, parm)

        return host,path,user,pswd,parm
    doparse = staticmethod(doparse)

    def getcset(d, depot,host,user,pswd,parm):
        p4opt = ""
        if "cset" in parm:
            return parm["cset"];
        if user:
            p4opt += " -u %s" % (user)
        if pswd:
            p4opt += " -P %s" % (pswd)
        if host:
            p4opt += " -p %s" % (host)

        p4date = data.getVar("P4DATE", d, 1)
        if "revision" in parm:
            depot += "#%s" % (parm["revision"])
        elif "label" in parm:
            depot += "@%s" % (parm["label"])
        elif p4date:
            depot += "@%s" % (p4date)

        p4cmd = data.getVar('FETCHCOMMAND_p4', d, 1)
        bb.msg.debug(1, bb.msg.domain.Fetcher, "Running %s%s changes -m 1 %s" % (p4cmd, p4opt, depot))
        p4file = os.popen("%s%s changes -m 1 %s" % (p4cmd, p4opt, depot))
        cset = p4file.readline().strip()
        bb.msg.debug(1, bb.msg.domain.Fetcher, "READ %s" % (cset))
        if not cset:
            return -1

        return cset.split(' ')[1]
    getcset = staticmethod(getcset)

    def localpath(self, url, ud, d):        

        (host,path,user,pswd,parm) = Perforce.doparse(url,d)

        # If a label is specified, we use that as our filename

        if "label" in parm:
            ud.localfile = "%s.tar.gz" % (parm["label"])
            return os.path.join(data.getVar("DL_DIR", d, 1), ud.localfile)

        base = path
        which = path.find('/...')
        if which != -1:
            base = path[:which]

        if base[0] == "/":
            base = base[1:]

        cset = Perforce.getcset(d, path, host, user, pswd, parm)

        ud.localfile = data.expand('%s+%s+%s.tar.gz' % (host,base.replace('/', '.'), cset), d)

        return os.path.join(data.getVar("DL_DIR", d, 1), ud.localfile)

    def go(self, loc, ud, d):
        """
        Fetch urls
        """

        # try to use the tarball stash
        if Fetch.try_mirror(d, ud.localfile):
            bb.msg.debug(1, bb.msg.domain.Fetcher, "%s already exists or was mirrored, skipping perforce checkout." % ud.localpath)
            return

        (host,depot,user,pswd,parm) = Perforce.doparse(loc, d)

        if depot.find('/...') != -1:
            path = depot[:depot.find('/...')]
        else:
            path = depot

        if "module" in parm:
            module = parm["module"]
        else:
            module = os.path.basename(path)

        localdata = data.createCopy(d)
        data.setVar('OVERRIDES', "p4:%s" % data.getVar('OVERRIDES', localdata), localdata)
        data.update_data(localdata)

        # Get the p4 command
        p4opt = ""
        if user:
            p4opt += " -u %s" % (user)

        if pswd:
            p4opt += " -P %s" % (pswd)

        if host:
            p4opt += " -p %s" % (host)

        p4cmd = data.getVar('FETCHCOMMAND', localdata, 1)

        # create temp directory
        bb.msg.debug(2, bb.msg.domain.Fetcher, "Fetch: creating temporary directory")
        bb.mkdirhier(data.expand('${WORKDIR}', localdata))
        data.setVar('TMPBASE', data.expand('${WORKDIR}/oep4.XXXXXX', localdata), localdata)
        tmppipe = os.popen(data.getVar('MKTEMPDIRCMD', localdata, 1) or "false")
        tmpfile = tmppipe.readline().strip()
        if not tmpfile:
            bb.error("Fetch: unable to create temporary directory.. make sure 'mktemp' is in the PATH.")
            raise FetchError(module)

        if "label" in parm:
            depot = "%s@%s" % (depot,parm["label"])
        else:
            cset = Perforce.getcset(d, depot, host, user, pswd, parm)
            depot = "%s@%s" % (depot,cset)

        os.chdir(tmpfile)
        bb.msg.note(1, bb.msg.domain.Fetcher, "Fetch " + loc)
        bb.msg.note(1, bb.msg.domain.Fetcher, "%s%s files %s" % (p4cmd, p4opt, depot))
        p4file = os.popen("%s%s files %s" % (p4cmd, p4opt, depot))

        if not p4file:
            bb.error("Fetch: unable to get the P4 files from %s" % (depot))
            raise FetchError(module)

        count = 0

        for file in p4file: 
            list = file.split()

            if list[2] == "delete":
                continue

            dest = list[0][len(path)+1:]
            where = dest.find("#")

            os.system("%s%s print -o %s/%s %s" % (p4cmd, p4opt, module,dest[:where],list[0]))
            count = count + 1
            
        if count == 0:
            bb.error("Fetch:  No files gathered from the P4 fetch")
            raise FetchError(module)

        myret = os.system("tar -czf %s %s" % (ud.localpath, module))
        if myret != 0:
            try:
                os.unlink(ud.localpath)
            except OSError:
                pass
            raise FetchError(module)
        # cleanup
        os.system('rm -rf %s' % tmpfile)


