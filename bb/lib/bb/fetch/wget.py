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

import os
import bb
from   bb import data
from   bb.fetch import Fetch
from   bb.fetch import FetchError

class Wget(Fetch):
    """Class to fetch urls via 'wget'"""
    def supports(self, url, ud, d):
        """
        Check to see if a given url can be fetched with wget.
        """
        return ud.type in ['http','https','ftp']

    def localpath(self, url, ud, d):

        url = bb.encodeurl([ud.type, ud.host, ud.path, ud.user, ud.pswd, {}])
        ud.basename = os.path.basename(ud.path)
        ud.localfile = data.expand(os.path.basename(url), d)

        return os.path.join(data.getVar("DL_DIR", d, True), ud.localfile)

    def go(self, uri, ud, d, checkonly = False):
        """Fetch urls"""

        def fetch_uri(uri, ud, d):
            if checkonly:
                fetchcmd = data.getVar("CHECKCOMMAND", d, 1)
            elif os.path.exists(ud.localpath):
                # file exists, but we didnt complete it.. trying again..
                fetchcmd = data.getVar("RESUMECOMMAND", d, 1)
            else:
                fetchcmd = data.getVar("FETCHCOMMAND", d, 1)

            uri = uri.split(";")[0]
            uri_decoded = list(bb.decodeurl(uri))
            uri_type = uri_decoded[0]
            uri_host = uri_decoded[1]

            bb.msg.note(1, bb.msg.domain.Fetcher, "fetch " + uri)
            fetchcmd = fetchcmd.replace("${URI}", uri.split(";")[0])
            fetchcmd = fetchcmd.replace("${FILE}", ud.basename)
            httpproxy = None
            ftpproxy = None
            if uri_type == 'http':
                httpproxy = data.getVar("HTTP_PROXY", d, True)
                httpproxy_ignore = (data.getVar("HTTP_PROXY_IGNORE", d, True) or "").split()
                for p in httpproxy_ignore:
                    if uri_host.endswith(p):
                        httpproxy = None
                        break
            if uri_type == 'ftp':
                ftpproxy = data.getVar("FTP_PROXY", d, True)
                ftpproxy_ignore = (data.getVar("HTTP_PROXY_IGNORE", d, True) or "").split()
                for p in ftpproxy_ignore:
                    if uri_host.endswith(p):
                        ftpproxy = None
                        break
            if httpproxy:
                fetchcmd = "http_proxy=" + httpproxy + " " + fetchcmd
            if ftpproxy:
                fetchcmd = "ftp_proxy=" + ftpproxy + " " + fetchcmd
            bb.msg.debug(2, bb.msg.domain.Fetcher, "executing " + fetchcmd)
            ret = os.system(fetchcmd)
            if ret != 0:
                return False

            # Sanity check since wget can pretend it succeed when it didn't
            # Also, this used to happen if sourceforge sent us to the mirror page
            if not os.path.exists(ud.localpath) and not checkonly:
                bb.msg.debug(2, bb.msg.domain.Fetcher, "The fetch command for %s returned success but %s doesn't exist?..." % (uri, ud.localpath))
                return False

            return True

        localdata = data.createCopy(d)
        data.setVar('OVERRIDES', "wget:" + data.getVar('OVERRIDES', localdata), localdata)
        data.update_data(localdata)

        if fetch_uri(uri, ud, localdata):
            return True

        raise FetchError(uri)


    def checkstatus(self, uri, ud, d):
        return self.go(uri, ud, d, True)
