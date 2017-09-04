# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
#
# Copyright (C) 2003, 2004  Chris Larson
# Copyright (C) 2003, 2004  Phil Blundell
# Copyright (C) 2003 - 2005 Michael 'Mickey' Lauer
# Copyright (C) 2005        Holger Hans Peter Freyther
# Copyright (C) 2005        ROAD GmbH
# Copyright (C) 2006        Richard Purdie
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

import re
from bb import data, utils
import bb

class NoProvider(Exception):
    """Exception raised when no provider of a build dependency can be found"""

class NoRProvider(Exception):
    """Exception raised when no provider of a runtime dependency can be found"""


def sortPriorities(pn, dataCache, pkg_pn = None):
    """
    Reorder pkg_pn by file priority and default preference
    """

    if not pkg_pn:
        pkg_pn = dataCache.pkg_pn

    files = pkg_pn[pn]
    priorities = {}
    for f in files:
        priority = dataCache.bbfile_priority[f]
        preference = dataCache.pkg_dp[f]
        if priority not in priorities:
            priorities[priority] = {}
        if preference not in priorities[priority]:
            priorities[priority][preference] = []
        priorities[priority][preference].append(f)
    tmp_pn = []
    for pri in sorted(priorities, lambda a, b: a - b):
        tmp_pref = []
        for pref in sorted(priorities[pri], lambda a, b: b - a):
            tmp_pref.extend(priorities[pri][pref])
        tmp_pn = [tmp_pref] + tmp_pn

    return tmp_pn

def preferredVersionMatch(pe, pv, pr, preferred_e, preferred_v, preferred_r):
    """
    Check if the version pe,pv,pr is the preferred one.
    If there is preferred version defined and ends with '%', then pv has to start with that version after removing the '%' 
    """
    if (pr == preferred_r or preferred_r == None):
        if (pe == preferred_e or preferred_e == None):
            if preferred_v == pv:
                return True
            if preferred_v != None and preferred_v.endswith('%') and pv.startswith(preferred_v[:len(preferred_v)-1]):
                return True
    return False

def findPreferredProvider(pn, cfgData, dataCache, pkg_pn = None, item = None):
    """
    Find the first provider in pkg_pn with a PREFERRED_VERSION set.
    """

    preferred_file = None
    preferred_ver = None

    localdata = data.createCopy(cfgData)
    bb.data.setVar('OVERRIDES', "pn-%s:%s:%s" % (pn, pn, data.getVar('OVERRIDES', localdata)), localdata)
    bb.data.update_data(localdata)

    preferred_v = bb.data.getVar('PREFERRED_VERSION_%s' % pn, localdata, True)
    if preferred_v:
        m = re.match('(\d+:)*(.*)(_.*)*', preferred_v)
        if m:
            if m.group(1):
                preferred_e = int(m.group(1)[:-1])
            else:
                preferred_e = None
            preferred_v = m.group(2)
            if m.group(3):
                preferred_r = m.group(3)[1:]
            else:
                preferred_r = None
        else:
            preferred_e = None
            preferred_r = None

        for file_set in pkg_pn:
            for f in file_set:
                pe,pv,pr = dataCache.pkg_pepvpr[f]
                if preferredVersionMatch(pe, pv, pr, preferred_e, preferred_v, preferred_r):
                    preferred_file = f
                    preferred_ver = (pe, pv, pr)
                    break
            if preferred_file:
                break;
        if preferred_r:
            pv_str = '%s-%s' % (preferred_v, preferred_r)
        else:
            pv_str = preferred_v
        if not (preferred_e is None):
            pv_str = '%s:%s' % (preferred_e, pv_str)
        itemstr = ""
        if item:
            itemstr = " (for item %s)" % item
        if preferred_file is None:
            bb.msg.note(1, bb.msg.domain.Provider, "preferred version %s of %s not available%s" % (pv_str, pn, itemstr))
        else:
            bb.msg.debug(1, bb.msg.domain.Provider, "selecting %s as PREFERRED_VERSION %s of package %s%s" % (preferred_file, pv_str, pn, itemstr))

    return (preferred_ver, preferred_file)


def findLatestProvider(pn, cfgData, dataCache, file_set):
    """
    Return the highest version of the providers in file_set.
    Take default preferences into account.
    """
    latest = None
    latest_p = 0
    latest_f = None
    for file_name in file_set:
        pe,pv,pr = dataCache.pkg_pepvpr[file_name]
        dp = dataCache.pkg_dp[file_name]

        if (latest is None) or ((latest_p == dp) and (utils.vercmp(latest, (pe, pv, pr)) < 0)) or (dp > latest_p):
            latest = (pe, pv, pr)
            latest_f = file_name
            latest_p = dp

    return (latest, latest_f)


def findBestProvider(pn, cfgData, dataCache, pkg_pn = None, item = None):
    """
    If there is a PREFERRED_VERSION, find the highest-priority bbfile
    providing that version.  If not, find the latest version provided by
    an bbfile in the highest-priority set.
    """

    sortpkg_pn = sortPriorities(pn, dataCache, pkg_pn)
    # Find the highest priority provider with a PREFERRED_VERSION set
    (preferred_ver, preferred_file) = findPreferredProvider(pn, cfgData, dataCache, sortpkg_pn, item)
    # Find the latest version of the highest priority provider
    (latest, latest_f) = findLatestProvider(pn, cfgData, dataCache, sortpkg_pn[0])

    if preferred_file is None:
        preferred_file = latest_f
        preferred_ver = latest

    return (latest, latest_f, preferred_ver, preferred_file)


def _filterProviders(providers, item, cfgData, dataCache):
    """
    Take a list of providers and filter/reorder according to the 
    environment variables and previous build results
    """
    eligible = []
    preferred_versions = {}
    sortpkg_pn = {}

    # The order of providers depends on the order of the files on the disk 
    # up to here. Sort pkg_pn to make dependency issues reproducible rather
    # than effectively random.
    providers.sort()

    # Collate providers by PN
    pkg_pn = {}
    for p in providers:
        pn = dataCache.pkg_fn[p]
        if pn not in pkg_pn:
            pkg_pn[pn] = []
        pkg_pn[pn].append(p)

    bb.msg.debug(1, bb.msg.domain.Provider, "providers for %s are: %s" % (item, pkg_pn.keys()))

    # First add PREFERRED_VERSIONS
    for pn in pkg_pn:
        sortpkg_pn[pn] = sortPriorities(pn, dataCache, pkg_pn)
        preferred_versions[pn] = findPreferredProvider(pn, cfgData, dataCache, sortpkg_pn[pn], item)
        if preferred_versions[pn][1]:
            eligible.append(preferred_versions[pn][1])

    # Now add latest versions
    for pn in sortpkg_pn:
        if pn in preferred_versions and preferred_versions[pn][1]:
            continue
        preferred_versions[pn] = findLatestProvider(pn, cfgData, dataCache, sortpkg_pn[pn][0])
        eligible.append(preferred_versions[pn][1])

    if len(eligible) == 0:
        bb.msg.error(bb.msg.domain.Provider, "no eligible providers for %s" % item)
        return 0

    # If pn == item, give it a slight default preference
    # This means PREFERRED_PROVIDER_foobar defaults to foobar if available
    for p in providers:
        pn = dataCache.pkg_fn[p]
        if pn != item:
            continue
        (newvers, fn) = preferred_versions[pn]
        if not fn in eligible:
            continue
        eligible.remove(fn)
        eligible = [fn] + eligible

    return eligible


def filterProviders(providers, item, cfgData, dataCache):
    """
    Take a list of providers and filter/reorder according to the 
    environment variables and previous build results
    Takes a "normal" target item
    """

    eligible = _filterProviders(providers, item, cfgData, dataCache)

    prefervar = bb.data.getVar('PREFERRED_PROVIDER_%s' % item, cfgData, 1)
    if prefervar:
        dataCache.preferred[item] = prefervar

    foundUnique = False
    if item in dataCache.preferred:
        for p in eligible:
            pn = dataCache.pkg_fn[p]
            if dataCache.preferred[item] == pn:
                bb.msg.note(2, bb.msg.domain.Provider, "selecting %s to satisfy %s due to PREFERRED_PROVIDERS" % (pn, item))
                eligible.remove(p)
                eligible = [p] + eligible
                foundUnique = True
                break

    bb.msg.debug(1, bb.msg.domain.Provider, "sorted providers for %s are: %s" % (item, eligible))

    return eligible, foundUnique

def filterProvidersRunTime(providers, item, cfgData, dataCache):
    """
    Take a list of providers and filter/reorder according to the 
    environment variables and previous build results
    Takes a "runtime" target item
    """

    eligible = _filterProviders(providers, item, cfgData, dataCache)

    # Should use dataCache.preferred here?
    preferred = []
    preferred_vars = []
    for p in eligible:
        pn = dataCache.pkg_fn[p]
        provides = dataCache.pn_provides[pn]
        for provide in provides:
            bb.msg.note(2, bb.msg.domain.Provider, "checking PREFERRED_PROVIDER_%s" % (provide))
            prefervar = bb.data.getVar('PREFERRED_PROVIDER_%s' % provide, cfgData, 1)
            if prefervar == pn:
                var = "PREFERRED_PROVIDER_%s = %s" % (provide, prefervar)
                bb.msg.note(2, bb.msg.domain.Provider, "selecting %s to satisfy runtime %s due to %s" % (pn, item, var))
                preferred_vars.append(var)
                eligible.remove(p)
                eligible = [p] + eligible
                preferred.append(p)
                break

    numberPreferred = len(preferred)

    if numberPreferred > 1:
        bb.msg.error(bb.msg.domain.Provider, "Conflicting PREFERRED_PROVIDER entries were found which resulted in an attempt to select multiple providers (%s) for runtime dependecy %s\nThe entries resulting in this conflict were: %s" % (preferred, item, preferred_vars))

    bb.msg.debug(1, bb.msg.domain.Provider, "sorted providers for %s are: %s" % (item, eligible))

    return eligible, numberPreferred

regexp_cache = {}

def getRuntimeProviders(dataCache, rdepend):
    """
    Return any providers of runtime dependency
    """
    rproviders = []

    if rdepend in dataCache.rproviders:
       rproviders += dataCache.rproviders[rdepend]

    if rdepend in dataCache.packages:
        rproviders += dataCache.packages[rdepend]

    if rproviders:
        return rproviders

    # Only search dynamic packages if we can't find anything in other variables
    for pattern in dataCache.packages_dynamic:
        pattern = pattern.replace('+', "\+")
        if pattern in regexp_cache:
            regexp = regexp_cache[pattern]
        else:
            try:
                regexp = re.compile(pattern)
            except:
                bb.msg.error(bb.msg.domain.Provider, "Error parsing re expression: %s" % pattern)
                raise
            regexp_cache[pattern] = regexp
        if regexp.match(rdepend):
            rproviders += dataCache.packages_dynamic[pattern]

    return rproviders
