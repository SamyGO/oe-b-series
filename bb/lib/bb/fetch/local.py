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

class Local(Fetch):
    def supports(self, url, urldata, d):
        """
        Check to see if a given url represents a local fetch.
        """
        return urldata.type in ['file']

    def localpath(self, url, urldata, d):
        """
        Return the local filename of a given url assuming a successful fetch.
        """
        path = url.split("://")[1]
        path = path.split(";")[0]
        newpath = path
        if path[0] != "/":
            filespath = data.getVar('FILESPATH', d, 1)
            if filespath:
                newpath = bb.which(filespath, path)
            if not newpath:
                filesdir = data.getVar('FILESDIR', d, 1)
                if filesdir:
                    newpath = os.path.join(filesdir, path)
        # We don't set localfile as for this fetcher the file is already local!
        return newpath

    def go(self, url, urldata, d):
        """Fetch urls (no-op for Local method)"""
        # no need to fetch local files, we'll deal with them in place.
        return 1

    def checkstatus(self, url, urldata, d):
        """
        Check the status of the url
        """
        if urldata.localpath.find("*") != -1:
            bb.msg.note(1, bb.msg.domain.Fetcher, "URL %s looks like a glob and was therefore not checked." % url)	
	    return True
        if os.path.exists(urldata.localpath):
           return True
        return False
