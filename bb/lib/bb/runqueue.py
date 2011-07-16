#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
BitBake 'RunQueue' implementation

Handles preparation and execution of a queue of tasks
"""

# Copyright (C) 2006-2007  Richard Purdie
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

from bb import msg, data, event, mkdirhier, utils
import bb, os, sys
import signal
import stat

class TaskFailure(Exception):
    """Exception raised when a task in a runqueue fails"""
    def __init__(self, x): 
        self.args = x


class RunQueueStats:
    """
    Holds statistics on the tasks handled by the associated runQueue
    """
    def __init__(self):
        self.completed = 0
        self.skipped = 0
        self.failed = 0

    def taskFailed(self):
        self.failed = self.failed + 1

    def taskCompleted(self, number = 1):
        self.completed = self.completed + number

    def taskSkipped(self, number = 1):
        self.skipped = self.skipped + number

class RunQueueScheduler:
    """
    Control the order tasks are scheduled in.
    """
    def __init__(self, runqueue):
        """
        The default scheduler just returns the first buildable task (the 
        priority map is sorted by task numer)
        """
        self.rq = runqueue
        numTasks = len(self.rq.runq_fnid)

        self.prio_map = []
        self.prio_map.extend(range(numTasks))

    def next(self):
        """
        Return the id of the first task we find that is buildable
        """
        for task1 in range(len(self.rq.runq_fnid)):
            task = self.prio_map[task1]
            if self.rq.runq_running[task] == 1:
                continue
            if self.rq.runq_buildable[task] == 1:
                return task

class RunQueueSchedulerSpeed(RunQueueScheduler):
    """
    A scheduler optimised for speed. The priority map is sorted by task weight,
    heavier weighted tasks (tasks needed by the most other tasks) are run first.
    """
    def __init__(self, runqueue):
        """
        The priority map is sorted by task weight.
        """
        from copy import deepcopy

        self.rq = runqueue

        sortweight = deepcopy(self.rq.runq_weight)
        sortweight.sort()
        copyweight = deepcopy(self.rq.runq_weight)
        self.prio_map = []

        for weight in sortweight:
            idx = copyweight.index(weight)
            self.prio_map.append(idx)
            copyweight[idx] = -1

        self.prio_map.reverse()

class RunQueueSchedulerCompletion(RunQueueSchedulerSpeed):
    """
    A scheduler optimised to complete .bb files are quickly as possible. The 
    priority map is sorted by task weight, but then reordered so once a given 
    .bb file starts to build, its completed as quickly as possible. This works
    well where disk space is at a premium and classes like OE's rm_work are in 
    force.
    """
    def __init__(self, runqueue):
        RunQueueSchedulerSpeed.__init__(self, runqueue)
        from copy import deepcopy

        #FIXME - whilst this groups all fnids together it does not reorder the
        #fnid groups optimally.
 
        basemap = deepcopy(self.prio_map)
        self.prio_map = []
        while (len(basemap) > 0):
            entry = basemap.pop(0)
            self.prio_map.append(entry)
            fnid = self.rq.runq_fnid[entry]
            todel = []
            for entry in basemap:
                entry_fnid = self.rq.runq_fnid[entry]
                if entry_fnid == fnid:
                    todel.append(basemap.index(entry))
                    self.prio_map.append(entry)
            todel.reverse()
            for idx in todel:
                del basemap[idx]

class RunQueue:
    """
    BitBake Run Queue implementation
    """
    def __init__(self, cooker, cfgData, dataCache, taskData, targets):
        self.reset_runqueue()
        self.cooker = cooker
        self.dataCache = dataCache
        self.taskData = taskData
        self.targets = targets

        self.cfgdata = cfgData
        self.number_tasks = int(bb.data.getVar("BB_NUMBER_THREADS", cfgData, 1) or 1)
        self.multi_provider_whitelist = (bb.data.getVar("MULTI_PROVIDER_WHITELIST", cfgData, 1) or "").split()
        self.scheduler = bb.data.getVar("BB_SCHEDULER", cfgData, 1) or "speed"
        self.stamppolicy = bb.data.getVar("BB_STAMP_POLICY", cfgData, 1) or "perfile"
        self.stampwhitelist = bb.data.getVar("BB_STAMP_WHITELIST", cfgData, 1) or ""

    def reset_runqueue(self):

        self.runq_fnid = []
        self.runq_task = []
        self.runq_depends = []
        self.runq_revdeps = []

    def get_user_idstring(self, task):
        fn = self.taskData.fn_index[self.runq_fnid[task]]
        taskname = self.runq_task[task]
        return "%s, %s" % (fn, taskname)

    def get_task_id(self, fnid, taskname):
        for listid in range(len(self.runq_fnid)):
            if self.runq_fnid[listid] == fnid and self.runq_task[listid] == taskname:
                return listid
        return None

    def circular_depchains_handler(self, tasks):
        """
        Some tasks aren't buildable, likely due to circular dependency issues.
        Identify the circular dependencies and print them in a user readable format.
        """
        from copy import deepcopy

        valid_chains = []
        explored_deps = {}
        msgs = []

        def chain_reorder(chain):
            """
            Reorder a dependency chain so the lowest task id is first
            """
            lowest = 0
            new_chain = []
            for entry in range(len(chain)):
                if chain[entry] < chain[lowest]:
                    lowest = entry
            new_chain.extend(chain[lowest:])
            new_chain.extend(chain[:lowest])
            return new_chain

        def chain_compare_equal(chain1, chain2):
            """
            Compare two dependency chains and see if they're the same
            """
            if len(chain1) != len(chain2):
                return False
            for index in range(len(chain1)):
                if chain1[index] != chain2[index]:
                    return False
            return True
            
        def chain_array_contains(chain, chain_array):
            """
            Return True if chain_array contains chain
            """
            for ch in chain_array:
                if chain_compare_equal(ch, chain):
                    return True
            return False

        def find_chains(taskid, prev_chain):
            prev_chain.append(taskid)
            total_deps = []
            total_deps.extend(self.runq_revdeps[taskid])
            for revdep in self.runq_revdeps[taskid]:
                if revdep in prev_chain:
                    idx = prev_chain.index(revdep)
                    # To prevent duplicates, reorder the chain to start with the lowest taskid
                    # and search through an array of those we've already printed
                    chain = prev_chain[idx:]
                    new_chain = chain_reorder(chain)
                    if not chain_array_contains(new_chain, valid_chains):
                        valid_chains.append(new_chain)
                        msgs.append("Dependency loop #%d found:\n" % len(valid_chains))
                        for dep in new_chain:
                            msgs.append("  Task %s (%s) (depends: %s)\n" % (dep, self.get_user_idstring(dep), self.runq_depends[dep]))
                        msgs.append("\n")
                    if len(valid_chains) > 10:
                        msgs.append("Aborted dependency loops search after 10 matches.\n")
                        return msgs
                    continue
                scan = False
                if revdep not in explored_deps:
                    scan = True
                elif revdep in explored_deps[revdep]:
                    scan = True
                else:
                    for dep in prev_chain:
                        if dep in explored_deps[revdep]:
                            scan = True
                if scan:
                    find_chains(revdep, deepcopy(prev_chain))
                for dep in explored_deps[revdep]:
                    if dep not in total_deps:
                        total_deps.append(dep)

            explored_deps[taskid] = total_deps

        for task in tasks:
            find_chains(task, [])

        return msgs

    def calculate_task_weights(self, endpoints):
        """
        Calculate a number representing the "weight" of each task. Heavier weighted tasks 
        have more dependencies and hence should be executed sooner for maximum speed.

        This function also sanity checks the task list finding tasks that its not
        possible to execute due to circular dependencies.
        """

        numTasks = len(self.runq_fnid)
        weight = []
        deps_left = []
        task_done = []

        for listid in range(numTasks):
            task_done.append(False)
            weight.append(0)
            deps_left.append(len(self.runq_revdeps[listid]))

        for listid in endpoints:
            weight[listid] = 1
            task_done[listid] = True

        while 1:
            next_points = []
            for listid in endpoints:
                for revdep in self.runq_depends[listid]:
                    weight[revdep] = weight[revdep] + weight[listid]
                    deps_left[revdep] = deps_left[revdep] - 1
                    if deps_left[revdep] == 0:
                        next_points.append(revdep)
                        task_done[revdep] = True
            endpoints = next_points
            if len(next_points) == 0:
                break      

        # Circular dependency sanity check
        problem_tasks = []
        for task in range(numTasks):
            if task_done[task] is False or deps_left[task] != 0:
                problem_tasks.append(task)
                bb.msg.debug(2, bb.msg.domain.RunQueue, "Task %s (%s) is not buildable\n" % (task, self.get_user_idstring(task)))
                bb.msg.debug(2, bb.msg.domain.RunQueue, "(Complete marker was %s and the remaining dependency count was %s)\n\n" % (task_done[task], deps_left[task]))

        if problem_tasks:
            message = "Unbuildable tasks were found.\n"
            message = message + "These are usually caused by circular dependencies and any circular dependency chains found will be printed below. Increase the debug level to see a list of unbuildable tasks.\n\n"
            message = message + "Identifying dependency loops (this may take a short while)...\n"
            bb.msg.error(bb.msg.domain.RunQueue, message)

            msgs = self.circular_depchains_handler(problem_tasks)

            message = "\n"
            for msg in msgs:
                message = message + msg
            bb.msg.fatal(bb.msg.domain.RunQueue, message)

        return weight

    def prepare_runqueue(self):
        """
        Turn a set of taskData into a RunQueue and compute data needed 
        to optimise the execution order.
        """

        depends = []
        runq_build = []
        recursive_tdepends = {}

        taskData = self.taskData

        if len(taskData.tasks_name) == 0:
            # Nothing to do
            return

        bb.msg.note(1, bb.msg.domain.RunQueue, "Preparing runqueue")

        # Step A - Work out a list of tasks to run
        #
        # Taskdata gives us a list of possible providers for a every target 
        # ordered by priority (build_targets, run_targets). It also gives
        # information on each of those providers.
        #
        # To create the actual list of tasks to execute we fix the list of 
        # providers and then resolve the dependencies into task IDs. This 
        # process is repeated for each type of dependency (tdepends, deptask, 
        # rdeptast, recrdeptask, idepends).

        for task in range(len(taskData.tasks_name)):
            fnid = taskData.tasks_fnid[task]
            fn = taskData.fn_index[fnid]
            task_deps = self.dataCache.task_deps[fn]

            if fnid not in taskData.failed_fnids:

                # Resolve task internal dependencies 
                #
                # e.g. addtask before X after Y
                depends = taskData.tasks_tdepends[task]

                # Resolve 'deptask' dependencies 
                #
                # e.g. do_sometask[deptask] = "do_someothertask"
                # (makes sure sometask runs after someothertask of all DEPENDS)
                if 'deptask' in task_deps and taskData.tasks_name[task] in task_deps['deptask']:
                    tasknames = task_deps['deptask'][taskData.tasks_name[task]].split()
                    for depid in taskData.depids[fnid]:
                        # Won't be in build_targets if ASSUME_PROVIDED
                        if depid in taskData.build_targets:
                            depdata = taskData.build_targets[depid][0]
                            if depdata is not None:
                                dep = taskData.fn_index[depdata]
                                for taskname in tasknames:
                                    depends.append(taskData.gettask_id(dep, taskname))

                # Resolve 'rdeptask' dependencies 
                #
                # e.g. do_sometask[rdeptask] = "do_someothertask"
                # (makes sure sometask runs after someothertask of all RDEPENDS)
                if 'rdeptask' in task_deps and taskData.tasks_name[task] in task_deps['rdeptask']:
                    taskname = task_deps['rdeptask'][taskData.tasks_name[task]]
                    for depid in taskData.rdepids[fnid]:
                        if depid in taskData.run_targets:
                            depdata = taskData.run_targets[depid][0]
                            if depdata is not None:
                                dep = taskData.fn_index[depdata]
                                depends.append(taskData.gettask_id(dep, taskname))

                # Resolve inter-task dependencies 
                #
                # e.g. do_sometask[depends] = "targetname:do_someothertask"
                # (makes sure sometask runs after targetname's someothertask)
                idepends = taskData.tasks_idepends[task]
                for (depid, idependtask) in idepends:
                    if depid in taskData.build_targets:
                        # Won't be in build_targets if ASSUME_PROVIDED
                        depdata = taskData.build_targets[depid][0]
                        if depdata is not None:
                            dep = taskData.fn_index[depdata]
                            depends.append(taskData.gettask_id(dep, idependtask))

                # Create a list of recursive dependent tasks (from tdepends) and cache
                def get_recursive_tdepends(task):
                    if not task:
                        return []
                    if task in recursive_tdepends:
                        return recursive_tdepends[task]

                    fnid = taskData.tasks_fnid[task]
                    taskids = taskData.gettask_ids(fnid)

                    rectdepends = taskids
                    nextdeps = taskids
                    while len(nextdeps) != 0:
                        newdeps = []
                        for nextdep in nextdeps:
                            for tdepend in taskData.tasks_tdepends[nextdep]:
                                if tdepend not in rectdepends:
                                    rectdepends.append(tdepend)
                                    newdeps.append(tdepend)
                        nextdeps = newdeps
                    recursive_tdepends[task] = rectdepends
                    return rectdepends

                # Using the list of tdepends for this task create a list of 
                # the recursive idepends we have
                def get_recursive_idepends(task):
                    if not task:
                        return []
                    rectdepends = get_recursive_tdepends(task)

                    recidepends = []
                    for tdepend in rectdepends:
                        for idepend in taskData.tasks_idepends[tdepend]:
                            recidepends.append(idepend)
                    return recidepends

                def add_recursive_build(depid, depfnid):
                    """
                    Add build depends of depid to depends
                    (if we've not see it before)
                    (calls itself recursively)
                    """
                    if str(depid) in dep_seen:
                        return
                    dep_seen.append(depid)
                    if depid in taskData.build_targets:
                        depdata = taskData.build_targets[depid][0]
                        if depdata is not None:
                            dep = taskData.fn_index[depdata]
                            # Need to avoid creating new tasks here
                            taskid = taskData.gettask_id(dep, taskname, False)
                            if taskid is not None:
                                depends.append(taskid)
                                fnid = taskData.tasks_fnid[taskid]
                                #print "Added %s (%s) due to %s" % (taskid, taskData.fn_index[fnid], taskData.fn_index[depfnid])
                            else:
                                fnid = taskData.getfn_id(dep)
                            for nextdepid in taskData.depids[fnid]:
                                if nextdepid not in dep_seen:
                                    add_recursive_build(nextdepid, fnid)
                            for nextdepid in taskData.rdepids[fnid]:
                                if nextdepid not in rdep_seen:
                                    add_recursive_run(nextdepid, fnid)
                            for (idependid, idependtask) in get_recursive_idepends(taskid):
                                if idependid not in dep_seen:
                                    add_recursive_build(idependid, fnid)

                def add_recursive_run(rdepid, depfnid):
                    """
                    Add runtime depends of rdepid to depends
                    (if we've not see it before)
                    (calls itself recursively)
                    """
                    if str(rdepid) in rdep_seen:
                        return
                    rdep_seen.append(rdepid)
                    if rdepid in taskData.run_targets:
                        depdata = taskData.run_targets[rdepid][0]
                        if depdata is not None:
                            dep = taskData.fn_index[depdata]
                            # Need to avoid creating new tasks here
                            taskid = taskData.gettask_id(dep, taskname, False)
                            if taskid is not None:
                                depends.append(taskid)
                                fnid = taskData.tasks_fnid[taskid]
                                #print "Added %s (%s) due to %s" % (taskid, taskData.fn_index[fnid], taskData.fn_index[depfnid])
                            else:
                                fnid = taskData.getfn_id(dep)
                            for nextdepid in taskData.depids[fnid]:
                                if nextdepid not in dep_seen:
                                    add_recursive_build(nextdepid, fnid)
                            for nextdepid in taskData.rdepids[fnid]:
                                if nextdepid not in rdep_seen:
                                    add_recursive_run(nextdepid, fnid)
                            for (idependid, idependtask) in get_recursive_idepends(taskid):
                                if idependid not in dep_seen:
                                    add_recursive_build(idependid, fnid)

                # Resolve recursive 'recrdeptask' dependencies 
                #
                # e.g. do_sometask[recrdeptask] = "do_someothertask"
                # (makes sure sometask runs after someothertask of all DEPENDS, RDEPENDS and intertask dependencies, recursively)
                if 'recrdeptask' in task_deps and taskData.tasks_name[task] in task_deps['recrdeptask']:
                    for taskname in task_deps['recrdeptask'][taskData.tasks_name[task]].split():
                        dep_seen = []
                        rdep_seen = []
                        idep_seen = []
                        for depid in taskData.depids[fnid]:
                            add_recursive_build(depid, fnid)
                        for rdepid in taskData.rdepids[fnid]:
                            add_recursive_run(rdepid, fnid)
                        deptaskid = taskData.gettask_id(fn, taskname, False)
                        for (idependid, idependtask) in get_recursive_idepends(deptaskid):
                            add_recursive_build(idependid, fnid)

                # Rmove all self references
                if task in depends:
                    newdep = []
                    bb.msg.debug(2, bb.msg.domain.RunQueue, "Task %s (%s %s) contains self reference! %s" % (task, taskData.fn_index[taskData.tasks_fnid[task]], taskData.tasks_name[task], depends))
                    for dep in depends:
                       if task != dep:
                          newdep.append(dep)
                    depends = newdep


            self.runq_fnid.append(taskData.tasks_fnid[task])
            self.runq_task.append(taskData.tasks_name[task])
            self.runq_depends.append(set(depends))
            self.runq_revdeps.append(set())

            runq_build.append(0)

        # Step B - Mark all active tasks
        #
        # Start with the tasks we were asked to run and mark all dependencies
        # as active too. If the task is to be 'forced', clear its stamp. Once
        # all active tasks are marked, prune the ones we don't need.

        bb.msg.note(2, bb.msg.domain.RunQueue, "Marking Active Tasks")

        def mark_active(listid, depth):
            """
            Mark an item as active along with its depends
            (calls itself recursively)
            """

            if runq_build[listid] == 1:
                return

            runq_build[listid] = 1

            depends = self.runq_depends[listid]
            for depend in depends:
                mark_active(depend, depth+1)

        self.target_pairs = []
        for target in self.targets:
            targetid = taskData.getbuild_id(target[0])

            if targetid not in taskData.build_targets:
                continue

            if targetid in taskData.failed_deps:
                continue

            fnid = taskData.build_targets[targetid][0]
            fn = taskData.fn_index[fnid]
            self.target_pairs.append((fn, target[1]))

            # Remove stamps for targets if force mode active
            if self.cooker.configuration.force:
                bb.msg.note(2, bb.msg.domain.RunQueue, "Remove stamp %s, %s" % (target[1], fn))
                bb.build.del_stamp(target[1], self.dataCache, fn)

            if fnid in taskData.failed_fnids:
                continue

            if target[1] not in taskData.tasks_lookup[fnid]:
                bb.msg.fatal(bb.msg.domain.RunQueue, "Task %s does not exist for target %s" % (target[1], target[0]))

            listid = taskData.tasks_lookup[fnid][target[1]]

            mark_active(listid, 1)

        # Step C - Prune all inactive tasks
        #
        # Once all active tasks are marked, prune the ones we don't need.

        maps = []
        delcount = 0
        for listid in range(len(self.runq_fnid)):
            if runq_build[listid-delcount] == 1:
                maps.append(listid-delcount)
            else:
                del self.runq_fnid[listid-delcount]
                del self.runq_task[listid-delcount]
                del self.runq_depends[listid-delcount]
                del runq_build[listid-delcount]
                del self.runq_revdeps[listid-delcount]
                delcount = delcount + 1
                maps.append(-1)

        #
        # Step D - Sanity checks and computation
        #

        # Check to make sure we still have tasks to run
        if len(self.runq_fnid) == 0:
            if not taskData.abort:
                bb.msg.fatal(bb.msg.domain.RunQueue, "All buildable tasks have been run but the build is incomplete (--continue mode). Errors for the tasks that failed will have been printed above.")
            else:		
                bb.msg.fatal(bb.msg.domain.RunQueue, "No active tasks and not in --continue mode?! Please report this bug.")

        bb.msg.note(2, bb.msg.domain.RunQueue, "Pruned %s inactive tasks, %s left" % (delcount, len(self.runq_fnid)))

        # Remap the dependencies to account for the deleted tasks
        # Check we didn't delete a task we depend on
        for listid in range(len(self.runq_fnid)):
            newdeps = []
            origdeps = self.runq_depends[listid]
            for origdep in origdeps:
                if maps[origdep] == -1:
                    bb.msg.fatal(bb.msg.domain.RunQueue, "Invalid mapping - Should never happen!")
                newdeps.append(maps[origdep])
            self.runq_depends[listid] = set(newdeps)

        bb.msg.note(2, bb.msg.domain.RunQueue, "Assign Weightings")

        # Generate a list of reverse dependencies to ease future calculations
        for listid in range(len(self.runq_fnid)):
            for dep in self.runq_depends[listid]:
                self.runq_revdeps[dep].add(listid)

        # Identify tasks at the end of dependency chains
        # Error on circular dependency loops (length two)
        endpoints = []
        for listid in range(len(self.runq_fnid)):
            revdeps = self.runq_revdeps[listid]
            if len(revdeps) == 0:
                endpoints.append(listid)
            for dep in revdeps:
                if dep in self.runq_depends[listid]:
                    #self.dump_data(taskData)
                    bb.msg.fatal(bb.msg.domain.RunQueue, "Task %s (%s) has circular dependency on %s (%s)" % (taskData.fn_index[self.runq_fnid[dep]], self.runq_task[dep] , taskData.fn_index[self.runq_fnid[listid]], self.runq_task[listid]))

        bb.msg.note(2, bb.msg.domain.RunQueue, "Compute totals (have %s endpoint(s))" % len(endpoints))


        # Calculate task weights 
        # Check of higher length circular dependencies
        self.runq_weight = self.calculate_task_weights(endpoints)

        # Decide what order to execute the tasks in, pick a scheduler
        #self.sched = RunQueueScheduler(self)
        if self.scheduler == "completion":
            self.sched = RunQueueSchedulerCompletion(self)
        else:
            self.sched = RunQueueSchedulerSpeed(self)

        # Sanity Check - Check for multiple tasks building the same provider
        prov_list = {}
        seen_fn = []
        for task in range(len(self.runq_fnid)):
            fn = taskData.fn_index[self.runq_fnid[task]]
            if fn in seen_fn:
                continue
            seen_fn.append(fn)
            for prov in self.dataCache.fn_provides[fn]:
                if prov not in prov_list:
                    prov_list[prov] = [fn]
                elif fn not in prov_list[prov]: 
                    prov_list[prov].append(fn)
        error = False
        for prov in prov_list:
            if len(prov_list[prov]) > 1 and prov not in self.multi_provider_whitelist:
                error = True
                bb.msg.error(bb.msg.domain.RunQueue, "Multiple .bb files are due to be built which each provide %s (%s).\n This usually means one provides something the other doesn't and should." % (prov, " ".join(prov_list[prov])))
        #if error:
        #    bb.msg.fatal(bb.msg.domain.RunQueue, "Corrupted metadata configuration detected, aborting...")


        # Create a whitelist usable by the stamp checks
        stampfnwhitelist = []
        for entry in self.stampwhitelist.split():
            entryid = self.taskData.getbuild_id(entry)
            if entryid not in self.taskData.build_targets:
                continue
            fnid = self.taskData.build_targets[entryid][0]
            fn = self.taskData.fn_index[fnid]
            stampfnwhitelist.append(fn)
        self.stampfnwhitelist = stampfnwhitelist

        #self.dump_data(taskData)

    def check_stamps(self):
        unchecked = {}
        current = []
        notcurrent = []
        buildable = []

        if self.stamppolicy == "perfile":
            fulldeptree = False
        else:
            fulldeptree = True
            stampwhitelist = []
            if self.stamppolicy == "whitelist":
                stampwhitelist = self.self.stampfnwhitelist

        for task in range(len(self.runq_fnid)):
            unchecked[task] = ""
            if len(self.runq_depends[task]) == 0:
                buildable.append(task)

        def check_buildable(self, task, buildable):
             for revdep in self.runq_revdeps[task]:
                alldeps = 1
                for dep in self.runq_depends[revdep]:
                    if dep in unchecked:
                        alldeps = 0
                if alldeps == 1:
                    if revdep in unchecked:
                        buildable.append(revdep)

        for task in range(len(self.runq_fnid)):
            if task not in unchecked:
                continue
            fn = self.taskData.fn_index[self.runq_fnid[task]]
            taskname = self.runq_task[task]
            stampfile = "%s.%s" % (self.dataCache.stamp[fn], taskname)
            # If the stamp is missing its not current
            if not os.access(stampfile, os.F_OK):
                del unchecked[task]
                notcurrent.append(task)
                check_buildable(self, task, buildable)
                continue
            # If its a 'nostamp' task, it's not current
            taskdep = self.dataCache.task_deps[fn]
            if 'nostamp' in taskdep and task in taskdep['nostamp']:
                del unchecked[task]
                notcurrent.append(task)
                check_buildable(self, task, buildable)
                continue

        while (len(buildable) > 0):
            nextbuildable = []
            for task in buildable:
                if task in unchecked:
                    fn = self.taskData.fn_index[self.runq_fnid[task]]
                    taskname = self.runq_task[task]
                    stampfile = "%s.%s" % (self.dataCache.stamp[fn], taskname)
                    iscurrent = True

                    t1 = os.stat(stampfile)[stat.ST_MTIME]
                    for dep in self.runq_depends[task]:
                        if iscurrent:
                            fn2 = self.taskData.fn_index[self.runq_fnid[dep]]
                            taskname2 = self.runq_task[dep]
                            stampfile2 = "%s.%s" % (self.dataCache.stamp[fn2], taskname2)
                            if fn == fn2 or (fulldeptree and fn2 not in stampwhitelist):
                                if dep in notcurrent:
                                    iscurrent = False
                                else:
                                    t2 = os.stat(stampfile2)[stat.ST_MTIME]
                                    if t1 < t2:
                                        iscurrent = False
                    del unchecked[task]
                    if iscurrent:
                        current.append(task)
                    else:
                        notcurrent.append(task)

                check_buildable(self, task, nextbuildable)

            buildable = nextbuildable

        #for task in range(len(self.runq_fnid)):
        #    fn = self.taskData.fn_index[self.runq_fnid[task]]
        #    taskname = self.runq_task[task]
        #    print "%s %s.%s" % (task, taskname, fn)

        #print "Unchecked: %s" % unchecked
        #print "Current: %s" % current
        #print "Not current: %s" % notcurrent

        if len(unchecked) > 0:
            bb.fatal("check_stamps fatal internal error")
        return current

    def check_stamp_task(self, task):

        if self.stamppolicy == "perfile":
            fulldeptree = False
        else:
            fulldeptree = True
            stampwhitelist = []
            if self.stamppolicy == "whitelist":
                stampwhitelist = self.stampfnwhitelist

        fn = self.taskData.fn_index[self.runq_fnid[task]]
        taskname = self.runq_task[task]
        stampfile = "%s.%s" % (self.dataCache.stamp[fn], taskname)
        # If the stamp is missing its not current
        if not os.access(stampfile, os.F_OK):
            bb.msg.debug(2, bb.msg.domain.RunQueue, "Stampfile %s not available\n" % stampfile)
            return False
        # If its a 'nostamp' task, it's not current
        taskdep = self.dataCache.task_deps[fn]
        if 'nostamp' in taskdep and taskname in taskdep['nostamp']:
            bb.msg.debug(2, bb.msg.domain.RunQueue, "%s.%s is nostamp\n" % (fn, taskname))
            return False

        iscurrent = True
        t1 =  os.stat(stampfile)[stat.ST_MTIME]
        for dep in self.runq_depends[task]:
            if iscurrent:
                fn2 = self.taskData.fn_index[self.runq_fnid[dep]]
                taskname2 = self.runq_task[dep]
                stampfile2 = "%s.%s" % (self.dataCache.stamp[fn2], taskname2)
                if fn == fn2 or (fulldeptree and fn2 not in stampwhitelist):
                    try:
                        t2 = os.stat(stampfile2)[stat.ST_MTIME]
                        if t1 < t2:
                            bb.msg.debug(2, bb.msg.domain.RunQueue, "Stampfile %s < %s" % (stampfile,stampfile2))
                            iscurrent = False
                    except:
                        bb.msg.debug(2, bb.msg.domain.RunQueue, "Exception reading %s for %s" % (stampfile2 ,stampfile))
                        iscurrent = False

        return iscurrent

    def execute_runqueue(self):
        """
        Run the tasks in a queue prepared by prepare_runqueue
        Upon failure, optionally try to recover the build using any alternate providers
        (if the abort on failure configuration option isn't set)
        """

        failures = 0
        while 1:
            failed_fnids = []
            try:
                self.execute_runqueue_internal()
            finally:
                if self.master_process:
                    failed_fnids = self.finish_runqueue()
            if len(failed_fnids) == 0:
                return failures
            if not self.taskData.tryaltconfigs:
                raise bb.runqueue.TaskFailure(failed_fnids)
            for fnid in failed_fnids:
                #print "Failure: %s %s %s" % (fnid, self.taskData.fn_index[fnid],  self.runq_task[fnid])
                self.taskData.fail_fnid(fnid)
                failures = failures + 1
            self.reset_runqueue()
            self.prepare_runqueue()

    def execute_runqueue_initVars(self):

        self.stats = RunQueueStats()

        self.active_builds = 0
        self.runq_buildable = []
        self.runq_running = []
        self.runq_complete = []
        self.build_pids = {}
        self.failed_fnids = []
        self.master_process = True

        # Mark initial buildable tasks
        for task in range(len(self.runq_fnid)):
            self.runq_running.append(0)
            self.runq_complete.append(0)
            if len(self.runq_depends[task]) == 0:
                self.runq_buildable.append(1)
            else:
                self.runq_buildable.append(0)

    def task_complete(self, task):
        """
        Mark a task as completed
        Look at the reverse dependencies and mark any task with 
        completed dependencies as buildable
        """
        self.runq_complete[task] = 1
        for revdep in self.runq_revdeps[task]:
            if self.runq_running[revdep] == 1:
                continue
            if self.runq_buildable[revdep] == 1:
                continue
            alldeps = 1
            for dep in self.runq_depends[revdep]:
                if self.runq_complete[dep] != 1:
                    alldeps = 0
            if alldeps == 1:
                self.runq_buildable[revdep] = 1
                fn = self.taskData.fn_index[self.runq_fnid[revdep]]
                taskname = self.runq_task[revdep]
                bb.msg.debug(1, bb.msg.domain.RunQueue, "Marking task %s (%s, %s) as buildable" % (revdep, fn, taskname))

    def execute_runqueue_internal(self):
        """
        Run the tasks in a queue prepared by prepare_runqueue
        """

        bb.msg.note(1, bb.msg.domain.RunQueue, "Executing runqueue")

        self.execute_runqueue_initVars()

        if len(self.runq_fnid) == 0:
            # nothing to do
            return []

        def sigint_handler(signum, frame):
            raise KeyboardInterrupt

        event.fire(bb.event.StampUpdate(self.target_pairs, self.dataCache.stamp, self.cfgdata))

        while True:
            task = self.sched.next()
            if task is not None:
                fn = self.taskData.fn_index[self.runq_fnid[task]]

                taskname = self.runq_task[task]
                if self.check_stamp_task(task):
                    bb.msg.debug(2, bb.msg.domain.RunQueue, "Stamp current task %s (%s)" % (task, self.get_user_idstring(task)))
                    self.runq_running[task] = 1
                    self.task_complete(task)
                    self.stats.taskCompleted()
                    self.stats.taskSkipped()
                    continue

                bb.msg.note(1, bb.msg.domain.RunQueue, "Running task %d of %d (ID: %s, %s)" % (self.stats.completed + self.active_builds + 1, len(self.runq_fnid), task, self.get_user_idstring(task)))
                sys.stdout.flush()
                sys.stderr.flush()
                try: 
                    pid = os.fork() 
                except OSError, e: 
                    bb.msg.fatal(bb.msg.domain.RunQueue, "fork failed: %d (%s)" % (e.errno, e.strerror))
                if pid == 0:
                    # Bypass master process' handling
                    self.master_process = False
                    # Stop Ctrl+C being sent to children
                    # signal.signal(signal.SIGINT, signal.SIG_IGN)
                    # Make the child the process group leader
                    os.setpgid(0, 0)
                    newsi = os.open('/dev/null', os.O_RDWR)
                    os.dup2(newsi, sys.stdin.fileno())
                    self.cooker.configuration.cmd = taskname[3:]
                    bb.data.setVar("__RUNQUEUE_DO_NOT_USE_EXTERNALLY", self, self.cooker.configuration.data)
                    try:
                        self.cooker.tryBuild(fn)
                    except bb.build.EventException:
                        bb.msg.error(bb.msg.domain.Build, "Build of " + fn + " " + taskname + " failed")
                        sys.exit(1)
                    except:
                        bb.msg.error(bb.msg.domain.Build, "Build of " + fn + " " + taskname + " failed")
                        raise
                    sys.exit(0)
                self.build_pids[pid] = task
                self.runq_running[task] = 1
                self.active_builds = self.active_builds + 1
                if self.active_builds < self.number_tasks:
                    continue
            if self.active_builds > 0:
                result = os.waitpid(-1, 0)
                self.active_builds = self.active_builds - 1
                task = self.build_pids[result[0]]
                if result[1] != 0:
                    del self.build_pids[result[0]]
                    bb.msg.error(bb.msg.domain.RunQueue, "Task %s (%s) failed" % (task, self.get_user_idstring(task)))
                    self.failed_fnids.append(self.runq_fnid[task])
                    self.stats.taskFailed()
                    if not self.taskData.abort:
                        continue
                    break
                self.task_complete(task)
                self.stats.taskCompleted()
                del self.build_pids[result[0]]
                continue
            return

    def finish_runqueue(self):
        try:
            while self.active_builds > 0:
                bb.msg.note(1, bb.msg.domain.RunQueue, "Waiting for %s active tasks to finish" % self.active_builds)
                tasknum = 1
                for k, v in self.build_pids.iteritems():
                     bb.msg.note(1, bb.msg.domain.RunQueue, "%s: %s (%s)" % (tasknum, self.get_user_idstring(v), k))
                     tasknum = tasknum + 1
                result = os.waitpid(-1, 0)
                task = self.build_pids[result[0]]
                if result[1] != 0:
                     bb.msg.error(bb.msg.domain.RunQueue, "Task %s (%s) failed" % (task, self.get_user_idstring(task)))
                     self.failed_fnids.append(self.runq_fnid[task])
                     self.stats.taskFailed()
                del self.build_pids[result[0]]
                self.active_builds = self.active_builds - 1
            bb.msg.note(1, bb.msg.domain.RunQueue, "Tasks Summary: Attempted %d tasks of which %d didn't need to be rerun and %d failed." % (self.stats.completed, self.stats.skipped, self.stats.failed))
            return self.failed_fnids
        except KeyboardInterrupt:
            bb.msg.note(1, bb.msg.domain.RunQueue, "Sending SIGINT to remaining %s tasks" % self.active_builds)
            for k, v in self.build_pids.iteritems():
                 try:
                     os.kill(-k, signal.SIGINT)
                 except:
                     pass
            raise

        # Sanity Checks
        for task in range(len(self.runq_fnid)):
            if self.runq_buildable[task] == 0:
                bb.msg.error(bb.msg.domain.RunQueue, "Task %s never buildable!" % task)
            if self.runq_running[task] == 0:
                bb.msg.error(bb.msg.domain.RunQueue, "Task %s never ran!" % task)
            if self.runq_complete[task] == 0:
                bb.msg.error(bb.msg.domain.RunQueue, "Task %s never completed!" % task)

        bb.msg.note(1, bb.msg.domain.RunQueue, "Tasks Summary: Attempted %d tasks of which %d didn't need to be rerun and %d failed." % (self.stats.completed, self.stats.skipped, self.stats.failed))

        return self.failed_fnids

    def dump_data(self, taskQueue):
        """
        Dump some debug information on the internal data structures
        """
        bb.msg.debug(3, bb.msg.domain.RunQueue, "run_tasks:")
        for task in range(len(self.runq_fnid)):
                bb.msg.debug(3, bb.msg.domain.RunQueue, " (%s)%s - %s: %s   Deps %s RevDeps %s" % (task, 
                        taskQueue.fn_index[self.runq_fnid[task]], 
                        self.runq_task[task], 
                        self.runq_weight[task], 
                        self.runq_depends[task], 
                        self.runq_revdeps[task]))

        bb.msg.debug(3, bb.msg.domain.RunQueue, "sorted_tasks:")
        for task1 in range(len(self.runq_fnid)):
            if task1 in self.prio_map:
                task = self.prio_map[task1]
                bb.msg.debug(3, bb.msg.domain.RunQueue, " (%s)%s - %s: %s   Deps %s RevDeps %s" % (task, 
                        taskQueue.fn_index[self.runq_fnid[task]], 
                        self.runq_task[task], 
                        self.runq_weight[task], 
                        self.runq_depends[task], 
                        self.runq_revdeps[task]))


def check_stamp_fn(fn, taskname, d):
    rq = bb.data.getVar("__RUNQUEUE_DO_NOT_USE_EXTERNALLY", d)
    fnid = rq.taskData.getfn_id(fn)
    taskid = rq.get_task_id(fnid, taskname)
    if taskid is not None:
        return rq.check_stamp_task(taskid)
    return None

