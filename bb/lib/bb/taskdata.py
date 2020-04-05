#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
BitBake 'TaskData' implementation

Task data collection and handling

"""

# Copyright (C) 2006  Richard Purdie
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

import bb

def re_match_strings(target, strings):
    """
    Whether or not the string 'target' matches
    any one string of the strings which can be regular expression string
    """
    import re

    for name in strings:
        if (name==target or
                re.search(name,target)!=None):
            return True
    return False

class TaskData:
    """
    BitBake Task Data implementation
    """
    def __init__(self, abort = True, tryaltconfigs = False):
        self.build_names_index = []
        self.run_names_index = []
        self.fn_index = []

        self.build_targets = {}
        self.run_targets = {}

        self.external_targets = []

        self.tasks_fnid = []
        self.tasks_name = []
        self.tasks_tdepends = []
        self.tasks_idepends = []
        # Cache to speed up task ID lookups
        self.tasks_lookup = {}

        self.depids = {}
        self.rdepids = {}

        self.consider_msgs_cache = []

        self.failed_deps = []
        self.failed_rdeps = []
        self.failed_fnids = []

        self.abort = abort
        self.tryaltconfigs = tryaltconfigs

    def getbuild_id(self, name):
        """
        Return an ID number for the build target name.
        If it doesn't exist, create one.
        """
        if not name in self.build_names_index:
            self.build_names_index.append(name)
            return len(self.build_names_index) - 1

        return self.build_names_index.index(name)

    def getrun_id(self, name):
        """
        Return an ID number for the run target name. 
        If it doesn't exist, create one.
        """
        if not name in self.run_names_index:
            self.run_names_index.append(name)
            return len(self.run_names_index) - 1

        return self.run_names_index.index(name)

    def getfn_id(self, name):
        """
        Return an ID number for the filename. 
        If it doesn't exist, create one.
        """
        if not name in self.fn_index:
            self.fn_index.append(name)
            return len(self.fn_index) - 1

        return self.fn_index.index(name)

    def gettask_ids(self, fnid):
        """
        Return an array of the ID numbers matching a given fnid.
        """
        ids = []
        if fnid in self.tasks_lookup:
            for task in self.tasks_lookup[fnid]:
                ids.append(self.tasks_lookup[fnid][task])
        return ids

    def gettask_id(self, fn, task, create = True):
        """
        Return an ID number for the task matching fn and task.
        If it doesn't exist, create one by default.
        Optionally return None instead.
        """
        fnid = self.getfn_id(fn)

        if fnid in self.tasks_lookup:
            if task in self.tasks_lookup[fnid]:
                return self.tasks_lookup[fnid][task]

        if not create:
            return None

        self.tasks_name.append(task)
        self.tasks_fnid.append(fnid)
        self.tasks_tdepends.append([])
        self.tasks_idepends.append([])

        listid = len(self.tasks_name) - 1

        if fnid not in self.tasks_lookup:
            self.tasks_lookup[fnid] = {}
        self.tasks_lookup[fnid][task] = listid

        return listid

    def add_tasks(self, fn, dataCache):
        """
        Add tasks for a given fn to the database
        """

        task_deps = dataCache.task_deps[fn]

        fnid = self.getfn_id(fn)

        if fnid in self.failed_fnids:
            bb.msg.fatal(bb.msg.domain.TaskData, "Trying to re-add a failed file? Something is broken...")

        # Check if we've already seen this fn
        if fnid in self.tasks_fnid:
            return

        for task in task_deps['tasks']:

            # Work out task dependencies
            parentids = []
            for dep in task_deps['parents'][task]:
                parentid = self.gettask_id(fn, dep)
                parentids.append(parentid)
            taskid = self.gettask_id(fn, task)
            self.tasks_tdepends[taskid].extend(parentids)

            # Touch all intertask dependencies
            if 'depends' in task_deps and task in task_deps['depends']:
                ids = []
                for dep in task_deps['depends'][task].split():
                    if dep:
                        if ":" not in dep:
                            bb.msg.fatal(bb.msg.domain.TaskData, "Error, dependency %s does not contain ':' character\n. Task 'depends' should be specified in the form 'packagename:task'" % (dep, fn))
                        ids.append(((self.getbuild_id(dep.split(":")[0])), dep.split(":")[1]))
                self.tasks_idepends[taskid].extend(ids)

        # Work out build dependencies
        if not fnid in self.depids:
            dependids = {}
            for depend in dataCache.deps[fn]:
                bb.msg.debug(2, bb.msg.domain.TaskData, "Added dependency %s for %s" % (depend, fn))
                dependids[self.getbuild_id(depend)] = None
            self.depids[fnid] = dependids.keys()

        # Work out runtime dependencies
        if not fnid in self.rdepids:
            rdependids = {}
            rdepends = dataCache.rundeps[fn]
            rrecs = dataCache.runrecs[fn]
            for package in rdepends:
                for rdepend in bb.utils.explode_deps(rdepends[package]):
                    bb.msg.debug(2, bb.msg.domain.TaskData, "Added runtime dependency %s for %s" % (rdepend, fn))
                    rdependids[self.getrun_id(rdepend)] = None
            for package in rrecs:
                for rdepend in bb.utils.explode_deps(rrecs[package]):
                    bb.msg.debug(2, bb.msg.domain.TaskData, "Added runtime recommendation %s for %s" % (rdepend, fn))
                    rdependids[self.getrun_id(rdepend)] = None
            self.rdepids[fnid] = rdependids.keys()

        for dep in self.depids[fnid]:
            if dep in self.failed_deps:
                self.fail_fnid(fnid)
                return
        for dep in self.rdepids[fnid]:
            if dep in self.failed_rdeps:
                self.fail_fnid(fnid)
                return

    def have_build_target(self, target):
        """
        Have we a build target matching this name?
        """
        targetid = self.getbuild_id(target)

        if targetid in self.build_targets:
            return True
        return False

    def have_runtime_target(self, target):
        """
        Have we a runtime target matching this name?
        """
        targetid = self.getrun_id(target)

        if targetid in self.run_targets:
            return True
        return False

    def add_build_target(self, fn, item):
        """
        Add a build target.
        If already present, append the provider fn to the list
        """
        targetid = self.getbuild_id(item)
        fnid = self.getfn_id(fn)

        if targetid in self.build_targets:
            if fnid in self.build_targets[targetid]:
                return
            self.build_targets[targetid].append(fnid)
            return
        self.build_targets[targetid] = [fnid]

    def add_runtime_target(self, fn, item):
        """
        Add a runtime target.
        If already present, append the provider fn to the list
        """
        targetid = self.getrun_id(item)
        fnid = self.getfn_id(fn)

        if targetid in self.run_targets:
            if fnid in self.run_targets[targetid]:
                return
            self.run_targets[targetid].append(fnid)
            return
        self.run_targets[targetid] = [fnid]

    def mark_external_target(self, item):
        """
        Mark a build target as being externally requested
        """
        targetid = self.getbuild_id(item)

        if targetid not in self.external_targets:
            self.external_targets.append(targetid)

    def get_unresolved_build_targets(self, dataCache):
        """
        Return a list of build targets who's providers 
        are unknown.
        """
        unresolved = []
        for target in self.build_names_index:
            if re_match_strings(target, dataCache.ignored_dependencies):
                continue
            if self.build_names_index.index(target) in self.failed_deps:
                continue
            if not self.have_build_target(target):
                unresolved.append(target)
        return unresolved

    def get_unresolved_run_targets(self, dataCache):
        """
        Return a list of runtime targets who's providers 
        are unknown.
        """
        unresolved = []
        for target in self.run_names_index:
            if re_match_strings(target, dataCache.ignored_dependencies):
                continue
            if self.run_names_index.index(target) in self.failed_rdeps:
                continue
            if not self.have_runtime_target(target):
                unresolved.append(target)
        return unresolved

    def get_provider(self, item):
        """
        Return a list of providers of item
        """
        targetid = self.getbuild_id(item)
   
        return self.build_targets[targetid]

    def get_dependees(self, itemid):
        """
        Return a list of targets which depend on item
        """
        dependees = []
        for fnid in self.depids:
            if itemid in self.depids[fnid]:
                dependees.append(fnid)
        return dependees

    def get_dependees_str(self, item):
        """
        Return a list of targets which depend on item as a user readable string
        """
        itemid = self.getbuild_id(item)
        dependees = []
        for fnid in self.depids:
            if itemid in self.depids[fnid]:
                dependees.append(self.fn_index[fnid])
        return dependees

    def get_rdependees(self, itemid):
        """
        Return a list of targets which depend on runtime item
        """
        dependees = []
        for fnid in self.rdepids:
            if itemid in self.rdepids[fnid]:
                dependees.append(fnid)
        return dependees

    def get_rdependees_str(self, item):
        """
        Return a list of targets which depend on runtime item as a user readable string
        """
        itemid = self.getrun_id(item)
        dependees = []
        for fnid in self.rdepids:
            if itemid in self.rdepids[fnid]:
                dependees.append(self.fn_index[fnid])
        return dependees

    def add_provider(self, cfgData, dataCache, item):
        try:
            self.add_provider_internal(cfgData, dataCache, item)
        except bb.providers.NoProvider:
            if self.abort:
                if self.get_rdependees_str(item):
                    bb.msg.error(bb.msg.domain.Provider, "Nothing PROVIDES '%s' (but '%s' DEPENDS on or otherwise requires it)" % (item, self.get_dependees_str(item)))
                else:
                    bb.msg.error(bb.msg.domain.Provider, "Nothing PROVIDES '%s'" % (item))
                raise
            targetid = self.getbuild_id(item)
            self.remove_buildtarget(targetid)

        self.mark_external_target(item)

    def add_provider_internal(self, cfgData, dataCache, item):
        """
        Add the providers of item to the task data
        Mark entries were specifically added externally as against dependencies 
        added internally during dependency resolution
        """

        if re_match_strings(item, dataCache.ignored_dependencies):
            return

        if not item in dataCache.providers:
            if self.get_rdependees_str(item):
                bb.msg.note(2, bb.msg.domain.Provider, "Nothing PROVIDES '%s' (but '%s' DEPENDS on or otherwise requires it)" % (item, self.get_dependees_str(item)))
            else:
                bb.msg.note(2, bb.msg.domain.Provider, "Nothing PROVIDES '%s'" % (item))
            bb.event.fire(bb.event.NoProvider(item), cfgData)
            raise bb.providers.NoProvider(item)

        if self.have_build_target(item):
            return

        all_p = dataCache.providers[item]

        eligible, foundUnique = bb.providers.filterProviders(all_p, item, cfgData, dataCache)
        eligible = [p for p in eligible if not self.getfn_id(p) in self.failed_fnids]

        if not eligible:
            bb.msg.note(2, bb.msg.domain.Provider, "No buildable provider PROVIDES '%s' but '%s' DEPENDS on or otherwise requires it. Enable debugging and see earlier logs to find unbuildable providers." % (item, self.get_dependees_str(item)))
            bb.event.fire(bb.event.NoProvider(item), cfgData)
            raise bb.providers.NoProvider(item)

        if len(eligible) > 1 and foundUnique == False:
            if item not in self.consider_msgs_cache:
                providers_list = []
                for fn in eligible:
                    providers_list.append(dataCache.pkg_fn[fn])
                bb.msg.note(1, bb.msg.domain.Provider, "multiple providers are available for %s (%s);" % (item, ", ".join(providers_list)))
                bb.msg.note(1, bb.msg.domain.Provider, "consider defining PREFERRED_PROVIDER_%s" % item)
                bb.event.fire(bb.event.MultipleProviders(item, providers_list), cfgData)
            self.consider_msgs_cache.append(item)

        for fn in eligible:
            fnid = self.getfn_id(fn)
            if fnid in self.failed_fnids:
                continue
            bb.msg.debug(2, bb.msg.domain.Provider, "adding %s to satisfy %s" % (fn, item))
            self.add_build_target(fn, item)
            self.add_tasks(fn, dataCache)


            #item = dataCache.pkg_fn[fn]

    def add_rprovider(self, cfgData, dataCache, item):
        """
        Add the runtime providers of item to the task data
        (takes item names from RDEPENDS/PACKAGES namespace)
        """

        if re_match_strings(item, dataCache.ignored_dependencies):
            return

        if self.have_runtime_target(item):
            return

        all_p = bb.providers.getRuntimeProviders(dataCache, item)

        if not all_p:
            bb.msg.error(bb.msg.domain.Provider, "'%s' RDEPENDS/RRECOMMENDS or otherwise requires the runtime entity '%s' but it wasn't found in any PACKAGE or RPROVIDES variables" % (self.get_rdependees_str(item), item))
            bb.event.fire(bb.event.NoProvider(item, runtime=True), cfgData)
            raise bb.providers.NoRProvider(item)

        eligible, numberPreferred = bb.providers.filterProvidersRunTime(all_p, item, cfgData, dataCache)
        eligible = [p for p in eligible if not self.getfn_id(p) in self.failed_fnids]

        if not eligible:
            bb.msg.error(bb.msg.domain.Provider, "'%s' RDEPENDS/RRECOMMENDS or otherwise requires the runtime entity '%s' but it wasn't found in any PACKAGE or RPROVIDES variables of any buildable targets.\nEnable debugging and see earlier logs to find unbuildable targets." % (self.get_rdependees_str(item), item))
            bb.event.fire(bb.event.NoProvider(item, runtime=True), cfgData)
            raise bb.providers.NoRProvider(item)

        if len(eligible) > 1 and numberPreferred == 0:
            if item not in self.consider_msgs_cache:
                providers_list = []
                for fn in eligible:
                    providers_list.append(dataCache.pkg_fn[fn])
                bb.msg.note(2, bb.msg.domain.Provider, "multiple providers are available for runtime %s (%s);" % (item, ", ".join(providers_list)))
                bb.msg.note(2, bb.msg.domain.Provider, "consider defining a PREFERRED_PROVIDER entry to match runtime %s" % item)
                bb.event.fire(bb.event.MultipleProviders(item,providers_list, runtime=True), cfgData)
            self.consider_msgs_cache.append(item)

        if numberPreferred > 1:
            if item not in self.consider_msgs_cache:
                providers_list = []
                for fn in eligible:
                    providers_list.append(dataCache.pkg_fn[fn])
                bb.msg.note(2, bb.msg.domain.Provider, "multiple providers are available for runtime %s (top %s entries preferred) (%s);" % (item, numberPreferred, ", ".join(providers_list)))
                bb.msg.note(2, bb.msg.domain.Provider, "consider defining only one PREFERRED_PROVIDER entry to match runtime %s" % item)
                bb.event.fire(bb.event.MultipleProviders(item,providers_list, runtime=True), cfgData)
            self.consider_msgs_cache.append(item)

        # run through the list until we find one that we can build
        for fn in eligible:
            fnid = self.getfn_id(fn)
            if fnid in self.failed_fnids:
                continue
            bb.msg.debug(2, bb.msg.domain.Provider, "adding '%s' to satisfy runtime '%s'" % (fn, item))
            self.add_runtime_target(fn, item)
            self.add_tasks(fn, dataCache)

    def fail_fnid(self, fnid, missing_list = []):
        """
        Mark a file as failed (unbuildable)
        Remove any references from build and runtime provider lists

        missing_list, A list of missing requirements for this target
        """
        if fnid in self.failed_fnids:
            return
        bb.msg.debug(1, bb.msg.domain.Provider, "File '%s' is unbuildable, removing..." % self.fn_index[fnid])
        self.failed_fnids.append(fnid)
        for target in self.build_targets:
            if fnid in self.build_targets[target]:
                self.build_targets[target].remove(fnid)
                if len(self.build_targets[target]) == 0:
                    self.remove_buildtarget(target, missing_list)
        for target in self.run_targets:
            if fnid in self.run_targets[target]:
                self.run_targets[target].remove(fnid)
                if len(self.run_targets[target]) == 0:
                    self.remove_runtarget(target, missing_list)

    def remove_buildtarget(self, targetid, missing_list = []):
        """
        Mark a build target as failed (unbuildable)
        Trigger removal of any files that have this as a dependency
        """
        if not missing_list:
            missing_list = [self.build_names_index[targetid]]
        else:
            missing_list = [self.build_names_index[targetid]] + missing_list
        bb.msg.note(2, bb.msg.domain.Provider, "Target '%s' is unbuildable, removing...\nMissing or unbuildable dependency chain was: %s" % (self.build_names_index[targetid], missing_list))
        self.failed_deps.append(targetid)
        dependees = self.get_dependees(targetid)
        for fnid in dependees:
            self.fail_fnid(fnid, missing_list)
        for taskid in range(len(self.tasks_idepends)):
            idepends = self.tasks_idepends[taskid]
            for (idependid, idependtask) in idepends:
                if idependid == targetid:
                    self.fail_fnid(self.tasks_fnid[taskid], missing_list)

        if self.abort and targetid in self.external_targets:
            bb.msg.error(bb.msg.domain.Provider, "Required build target '%s' has no buildable providers.\nMissing or unbuildable dependency chain was: %s" % (self.build_names_index[targetid], missing_list))
            raise bb.providers.NoProvider

    def remove_runtarget(self, targetid, missing_list = []):
        """
        Mark a run target as failed (unbuildable)
        Trigger removal of any files that have this as a dependency
        """
        if not missing_list:
            missing_list = [self.run_names_index[targetid]]
        else:
            missing_list = [self.run_names_index[targetid]] + missing_list

        bb.msg.note(1, bb.msg.domain.Provider, "Runtime target '%s' is unbuildable, removing...\nMissing or unbuildable dependency chain was: %s" % (self.run_names_index[targetid], missing_list))
        self.failed_rdeps.append(targetid)
        dependees = self.get_rdependees(targetid)
        for fnid in dependees:
            self.fail_fnid(fnid, missing_list)

    def add_unresolved(self, cfgData, dataCache):
        """
        Resolve all unresolved build and runtime targets
        """
        bb.msg.note(1, bb.msg.domain.TaskData, "Resolving any missing task queue dependencies")
        while 1:
            added = 0
            for target in self.get_unresolved_build_targets(dataCache):
                try:
                    self.add_provider_internal(cfgData, dataCache, target)
                    added = added + 1
                except bb.providers.NoProvider:
                    targetid = self.getbuild_id(target)
                    if self.abort and targetid in self.external_targets:
                        if self.get_rdependees_str(target):
                            bb.msg.error(bb.msg.domain.Provider, "Nothing PROVIDES '%s' (but '%s' DEPENDS on or otherwise requires it)" % (target, self.get_dependees_str(target)))
                        else:
                            bb.msg.error(bb.msg.domain.Provider, "Nothing PROVIDES '%s'" % (target))
                        raise
                    self.remove_buildtarget(targetid)
            for target in self.get_unresolved_run_targets(dataCache):
                try:
                    self.add_rprovider(cfgData, dataCache, target)
                    added = added + 1
                except bb.providers.NoRProvider:
                    self.remove_runtarget(self.getrun_id(target))
            bb.msg.debug(1, bb.msg.domain.TaskData, "Resolved " + str(added) + " extra dependencies")
            if added == 0:
                break
        # self.dump_data()

    def dump_data(self):
        """
        Dump some debug information on the internal data structures
        """
        bb.msg.debug(3, bb.msg.domain.TaskData, "build_names:")
        bb.msg.debug(3, bb.msg.domain.TaskData, ", ".join(self.build_names_index))

        bb.msg.debug(3, bb.msg.domain.TaskData, "run_names:")
        bb.msg.debug(3, bb.msg.domain.TaskData, ", ".join(self.run_names_index))

        bb.msg.debug(3, bb.msg.domain.TaskData, "build_targets:")
        for buildid in range(len(self.build_names_index)):
            target = self.build_names_index[buildid]
            targets = "None"
            if buildid in self.build_targets:
                targets = self.build_targets[buildid]
            bb.msg.debug(3, bb.msg.domain.TaskData, " (%s)%s: %s" % (buildid, target, targets))

        bb.msg.debug(3, bb.msg.domain.TaskData, "run_targets:")
        for runid in range(len(self.run_names_index)):
            target = self.run_names_index[runid]
            targets = "None"
            if runid in self.run_targets:
                targets = self.run_targets[runid]
            bb.msg.debug(3, bb.msg.domain.TaskData, " (%s)%s: %s" % (runid, target, targets))

        bb.msg.debug(3, bb.msg.domain.TaskData, "tasks:")
        for task in range(len(self.tasks_name)):
            bb.msg.debug(3, bb.msg.domain.TaskData, " (%s)%s - %s: %s" % (
                task, 
                self.fn_index[self.tasks_fnid[task]], 
                self.tasks_name[task], 
                self.tasks_tdepends[task]))

        bb.msg.debug(3, bb.msg.domain.TaskData, "dependency ids (per fn):")
        for fnid in self.depids:
            bb.msg.debug(3, bb.msg.domain.TaskData, " %s %s: %s" % (fnid, self.fn_index[fnid], self.depids[fnid]))

        bb.msg.debug(3, bb.msg.domain.TaskData, "runtime dependency ids (per fn):")
        for fnid in self.rdepids:
            bb.msg.debug(3, bb.msg.domain.TaskData, " %s %s: %s" % (fnid, self.fn_index[fnid], self.rdepids[fnid]))


