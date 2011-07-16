#!/usr/bin/env python
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

import sys, os, getopt, glob, copy, os.path, re, time
import bb
from bb import utils, data, parse, event, cache, providers, taskdata, runqueue
import itertools, sre_constants

parsespin = itertools.cycle( r'|/-\\' )

#============================================================================#
# BBCooker
#============================================================================#
class BBCooker:
    """
    Manages one bitbake build run
    """

    def __init__(self, configuration):
        self.status = None

        self.cache = None
        self.bb_cache = None

        self.configuration = configuration

        if self.configuration.verbose:
            bb.msg.set_verbose(True)

        if self.configuration.debug:
            bb.msg.set_debug_level(self.configuration.debug)
        else:
            bb.msg.set_debug_level(0)

        if self.configuration.debug_domains:
            bb.msg.set_debug_domains(self.configuration.debug_domains)

        self.configuration.data = bb.data.init()

    def parseConfiguration(self):

        bb.data.inheritFromOS(self.configuration.data)

        for f in self.configuration.file:
            self.parseConfigurationFile( f )

        self.parseConfigurationFile( os.path.join( "conf", "bitbake.conf" ) )

        if not self.configuration.cmd:
            self.configuration.cmd = bb.data.getVar("BB_DEFAULT_TASK", self.configuration.data) or "build"

        bbpkgs = bb.data.getVar('BBPKGS', self.configuration.data, True)
        if bbpkgs and len(self.configuration.pkgs_to_build) == 0:
            self.configuration.pkgs_to_build.extend(bbpkgs.split())

        #
        # Special updated configuration we use for firing events
        #
        self.configuration.event_data = bb.data.createCopy(self.configuration.data)
        bb.data.update_data(self.configuration.event_data)

        #
        # TOSTOP must not be set or our children will hang when they output
        #
        fd = sys.stdout.fileno()
        if os.isatty(fd):
            import termios
            tcattr = termios.tcgetattr(fd)
            if tcattr[3] & termios.TOSTOP:
                bb.msg.note(1, bb.msg.domain.Build, "The terminal had the TOSTOP bit set, clearing...")
                tcattr[3] = tcattr[3] & ~termios.TOSTOP
                termios.tcsetattr(fd, termios.TCSANOW, tcattr)

        # Change nice level if we're asked to
        nice = bb.data.getVar("BB_NICE_LEVEL", self.configuration.data, True)
        if nice:
            curnice = os.nice(0)
            nice = int(nice) - curnice
            bb.msg.note(2, bb.msg.domain.Build, "Renice to %s " % os.nice(nice))
 

    def tryBuildPackage(self, fn, item, task, the_data):
        """
        Build one task of a package, optionally build following task depends
        """
        bb.event.fire(bb.event.PkgStarted(item, the_data))
        try:
            if not self.configuration.dry_run:
                bb.build.exec_task('do_%s' % task, the_data)
            bb.event.fire(bb.event.PkgSucceeded(item, the_data))
            return True
        except bb.build.FuncFailed:
            bb.msg.error(bb.msg.domain.Build, "task stack execution failed")
            bb.event.fire(bb.event.PkgFailed(item, the_data))
            raise
        except bb.build.EventException, e:
            event = e.args[1]
            bb.msg.error(bb.msg.domain.Build, "%s event exception, aborting" % bb.event.getName(event))
            bb.event.fire(bb.event.PkgFailed(item, the_data))
            raise

    def tryBuild(self, fn):
        """
        Build a provider and its dependencies. 
        build_depends is a list of previous build dependencies (not runtime)
        If build_depends is empty, we're dealing with a runtime depends
        """
        the_data = self.bb_cache.loadDataFull(fn, self.configuration.data)

        item = self.status.pkg_fn[fn]

        #if bb.build.stamp_is_current('do_%s' % self.configuration.cmd, the_data):
        #    return True

        return self.tryBuildPackage(fn, item, self.configuration.cmd, the_data)

    def showVersions(self):
        pkg_pn = self.status.pkg_pn
        preferred_versions = {}
        latest_versions = {}

        # Sort by priority
        for pn in pkg_pn.keys():
            (last_ver,last_file,pref_ver,pref_file) = bb.providers.findBestProvider(pn, self.configuration.data, self.status)
            preferred_versions[pn] = (pref_ver, pref_file)
            latest_versions[pn] = (last_ver, last_file)

        pkg_list = pkg_pn.keys()
        pkg_list.sort()

        for p in pkg_list:
            pref = preferred_versions[p]
            latest = latest_versions[p]

            if pref != latest:
                prefstr = pref[0][0] + ":" + pref[0][1] + '-' + pref[0][2]
            else:
                prefstr = ""

            print "%-30s %20s %20s" % (p, latest[0][0] + ":" + latest[0][1] + "-" + latest[0][2],
                                        prefstr)


    def showEnvironment(self , buildfile = None, pkgs_to_build = []):
        """
        Show the outer or per-package environment
        """
        fn = None
        envdata = None

        if 'world' in pkgs_to_build:
            print "'world' is not a valid target for --environment."
            sys.exit(1)

        if len(pkgs_to_build) > 1:
            print "Only one target can be used with the --environment option."
            sys.exit(1)

        if buildfile:
            if len(pkgs_to_build) > 0:
                print "No target should be used with the --environment and --buildfile options."
                sys.exit(1)
            self.cb = None
            self.bb_cache = bb.cache.init(self)
            fn = self.matchFile(buildfile)
            if not fn:
                sys.exit(1)
        elif len(pkgs_to_build) == 1:
            self.updateCache()

            localdata = data.createCopy(self.configuration.data)
            bb.data.update_data(localdata)
            bb.data.expandKeys(localdata)

            taskdata = bb.taskdata.TaskData(self.configuration.abort, self.configuration.tryaltconfigs)

            try:
                taskdata.add_provider(localdata, self.status, pkgs_to_build[0])
                taskdata.add_unresolved(localdata, self.status)
            except bb.providers.NoProvider:
                sys.exit(1)

            targetid = taskdata.getbuild_id(pkgs_to_build[0])
            fnid = taskdata.build_targets[targetid][0]
            fn = taskdata.fn_index[fnid]
        else:
            envdata = self.configuration.data

        if fn:
            try:
                envdata = self.bb_cache.loadDataFull(fn, self.configuration.data)
            except IOError, e:
                bb.msg.fatal(bb.msg.domain.Parsing, "Unable to read %s: %s" % (fn, e))
            except Exception, e:
                bb.msg.fatal(bb.msg.domain.Parsing, "%s" % e)

        # emit variables and shell functions
        try:
            data.update_data( envdata )
            data.emit_env(sys.__stdout__, envdata, True)
        except Exception, e:
            bb.msg.fatal(bb.msg.domain.Parsing, "%s" % e)
        # emit the metadata which isnt valid shell
        data.expandKeys( envdata )
        for e in envdata.keys():
            if data.getVarFlag( e, 'python', envdata ):
                sys.__stdout__.write("\npython %s () {\n%s}\n" % (e, data.getVar(e, envdata, 1)))

    def generateDotGraph( self, pkgs_to_build, ignore_deps ):
        """
        Generate a task dependency graph. 

        pkgs_to_build A list of packages that needs to be built
        ignore_deps   A list of names where processing of dependencies
                      should be stopped. e.g. dependencies that get
        """

        for dep in ignore_deps:
            self.status.ignored_dependencies.add(dep)

        localdata = data.createCopy(self.configuration.data)
        bb.data.update_data(localdata)
        bb.data.expandKeys(localdata)
        taskdata = bb.taskdata.TaskData(self.configuration.abort, self.configuration.tryaltconfigs)

        runlist = []
        try:
            for k in pkgs_to_build:
                taskdata.add_provider(localdata, self.status, k)
                runlist.append([k, "do_%s" % self.configuration.cmd])
            taskdata.add_unresolved(localdata, self.status)
        except bb.providers.NoProvider:
            sys.exit(1)
        rq = bb.runqueue.RunQueue(self, self.configuration.data, self.status, taskdata, runlist)
        rq.prepare_runqueue()

        seen_fnids = []  
        depends_file = file('depends.dot', 'w' )
        tdepends_file = file('task-depends.dot', 'w' )
        print >> depends_file, "digraph depends {"
        print >> tdepends_file, "digraph depends {"

        for task in range(len(rq.runq_fnid)):
            taskname = rq.runq_task[task]
            fnid = rq.runq_fnid[task]
            fn = taskdata.fn_index[fnid]
            pn = self.status.pkg_fn[fn]
            version  = "%s:%s-%s" % self.status.pkg_pepvpr[fn]
            print >> tdepends_file, '"%s.%s" [label="%s %s\\n%s\\n%s"]' % (pn, taskname, pn, taskname, version, fn)
            for dep in rq.runq_depends[task]:
                depfn = taskdata.fn_index[rq.runq_fnid[dep]]
                deppn = self.status.pkg_fn[depfn]
                print >> tdepends_file, '"%s.%s" -> "%s.%s"' % (pn, rq.runq_task[task], deppn, rq.runq_task[dep])
            if fnid not in seen_fnids:
                seen_fnids.append(fnid)
                packages = []
                print >> depends_file, '"%s" [label="%s %s\\n%s"]' % (pn, pn, version, fn)
                for depend in self.status.deps[fn]:
                    print >> depends_file, '"%s" -> "%s"' % (pn, depend)
                rdepends = self.status.rundeps[fn]
                for package in rdepends:
                    for rdepend in re.findall("([\w.-]+)(\ \(.+\))?", rdepends[package]):
                        print >> depends_file, '"%s" -> "%s%s" [style=dashed]' % (package, rdepend[0], rdepend[1])
                    packages.append(package)
                rrecs = self.status.runrecs[fn]
                for package in rrecs:
                    for rdepend in re.findall("([\w.-]+)(\ \(.+\))?", rrecs[package]):
                        print >> depends_file, '"%s" -> "%s%s" [style=dashed]' % (package, rdepend[0], rdepend[1])
                    if not package in packages:
                        packages.append(package)
                for package in packages:
                    if package != pn:
                        print >> depends_file, '"%s" [label="%s(%s) %s\\n%s"]' % (package, package, pn, version, fn)
                        for depend in self.status.deps[fn]:
                            print >> depends_file, '"%s" -> "%s"' % (package, depend)
                # Prints a flattened form of the above where subpackages of a package are merged into the main pn
                #print >> depends_file, '"%s" [label="%s %s\\n%s\\n%s"]' % (pn, pn, taskname, version, fn)
                #for rdep in taskdata.rdepids[fnid]:
                #    print >> depends_file, '"%s" -> "%s" [style=dashed]' % (pn, taskdata.run_names_index[rdep])
                #for dep in taskdata.depids[fnid]:
                #    print >> depends_file, '"%s" -> "%s"' % (pn, taskdata.build_names_index[dep])
        print >> depends_file,  "}"
        print >> tdepends_file,  "}"
        bb.msg.note(1, bb.msg.domain.Collection, "Dependencies saved to 'depends.dot'")
        bb.msg.note(1, bb.msg.domain.Collection, "Task dependencies saved to 'task-depends.dot'")

    def buildDepgraph( self ):
        all_depends = self.status.all_depends
        pn_provides = self.status.pn_provides

        localdata = data.createCopy(self.configuration.data)
        bb.data.update_data(localdata)
        bb.data.expandKeys(localdata)

        def calc_bbfile_priority(filename):
            for (regex, pri) in self.status.bbfile_config_priorities:
                if regex.match(filename):
                    return pri
            return 0

        # Handle PREFERRED_PROVIDERS
        for p in (bb.data.getVar('PREFERRED_PROVIDERS', localdata, 1) or "").split():
            try:
                (providee, provider) = p.split(':')
            except:
                bb.msg.error(bb.msg.domain.Provider, "Malformed option in PREFERRED_PROVIDERS variable: %s" % p)
                continue
            if providee in self.status.preferred and self.status.preferred[providee] != provider:
                bb.msg.error(bb.msg.domain.Provider, "conflicting preferences for %s: both %s and %s specified" % (providee, provider, self.status.preferred[providee]))
            self.status.preferred[providee] = provider

        # Calculate priorities for each file
        for p in self.status.pkg_fn.keys():
            self.status.bbfile_priority[p] = calc_bbfile_priority(p)

    def buildWorldTargetList(self):
        """
         Build package list for "bitbake world"
        """
        all_depends = self.status.all_depends
        pn_provides = self.status.pn_provides
        bb.msg.debug(1, bb.msg.domain.Parsing, "collating packages for \"world\"")
        for f in self.status.possible_world:
            terminal = True
            pn = self.status.pkg_fn[f]

            for p in pn_provides[pn]:
                if p.startswith('virtual/'):
                    bb.msg.debug(2, bb.msg.domain.Parsing, "World build skipping %s due to %s provider starting with virtual/" % (f, p))
                    terminal = False
                    break
                for pf in self.status.providers[p]:
                    if self.status.pkg_fn[pf] != pn:
                        bb.msg.debug(2, bb.msg.domain.Parsing, "World build skipping %s due to both us and %s providing %s" % (f, pf, p))
                        terminal = False
                        break
            if terminal:
                self.status.world_target.add(pn)

            # drop reference count now
            self.status.possible_world = None
            self.status.all_depends    = None

    def myProgressCallback( self, x, y, f, from_cache ):
        """Update any tty with the progress change"""
        if os.isatty(sys.stdout.fileno()):
            sys.stdout.write("\rNOTE: Handling BitBake files: %s (%04d/%04d) [%2d %%]" % ( parsespin.next(), x, y, x*100/y ) )
            sys.stdout.flush()
        else:
            if x == 1:
                sys.stdout.write("Parsing .bb files, please wait...")
                sys.stdout.flush()
            if x == y:
                sys.stdout.write("done.")
                sys.stdout.flush()

    def interactiveMode( self ):
        """Drop off into a shell"""
        try:
            from bb import shell
        except ImportError, details:
            bb.msg.fatal(bb.msg.domain.Parsing, "Sorry, shell not available (%s)" % details )
        else:
            shell.start( self )
            sys.exit( 0 )

    def parseConfigurationFile( self, afile ):
        try:
            self.configuration.data = bb.parse.handle( afile, self.configuration.data )

            # Handle any INHERITs and inherit the base class
            inherits  = ["base"] + (bb.data.getVar('INHERIT', self.configuration.data, True ) or "").split()
            for inherit in inherits:
                self.configuration.data = bb.parse.handle(os.path.join('classes', '%s.bbclass' % inherit), self.configuration.data, True )

            # Nomally we only register event handlers at the end of parsing .bb files
            # We register any handlers we've found so far here...
            for var in data.getVar('__BBHANDLERS', self.configuration.data) or []:
                bb.event.register(var,bb.data.getVar(var, self.configuration.data))

            bb.fetch.fetcher_init(self.configuration.data)

            bb.event.fire(bb.event.ConfigParsed(self.configuration.data))

        except IOError, e:
            bb.msg.fatal(bb.msg.domain.Parsing, "IO Error: %s" % str(e) )
        except bb.parse.ParseError, details:
            bb.msg.fatal(bb.msg.domain.Parsing, "Unable to parse %s (%s)" % (afile, details) )

    def handleCollections( self, collections ):
        """Handle collections"""
        if collections:
            collection_list = collections.split()
            for c in collection_list:
                regex = bb.data.getVar("BBFILE_PATTERN_%s" % c, self.configuration.data, 1)
                if regex == None:
                    bb.msg.error(bb.msg.domain.Parsing, "BBFILE_PATTERN_%s not defined" % c)
                    continue
                priority = bb.data.getVar("BBFILE_PRIORITY_%s" % c, self.configuration.data, 1)
                if priority == None:
                    bb.msg.error(bb.msg.domain.Parsing, "BBFILE_PRIORITY_%s not defined" % c)
                    continue
                try:
                    cre = re.compile(regex)
                except re.error:
                    bb.msg.error(bb.msg.domain.Parsing, "BBFILE_PATTERN_%s \"%s\" is not a valid regular expression" % (c, regex))
                    continue
                try:
                    pri = int(priority)
                    self.status.bbfile_config_priorities.append((cre, pri))
                except ValueError:
                    bb.msg.error(bb.msg.domain.Parsing, "invalid value for BBFILE_PRIORITY_%s: \"%s\"" % (c, priority))

    def buildSetVars(self):
        """
        Setup any variables needed before starting a build
        """
        if not bb.data.getVar("BUILDNAME", self.configuration.data):
            bb.data.setVar("BUILDNAME", os.popen('date +%Y%m%d%H%M').readline().strip(), self.configuration.data)
        bb.data.setVar("BUILDSTART", time.strftime('%m/%d/%Y %H:%M:%S',time.gmtime()),self.configuration.data)

    def matchFile(self, buildfile):
        """
        Convert the fragment buildfile into a real file
        Error if there are too many matches
        """
        bf = os.path.abspath(buildfile)
        try:
            os.stat(bf)
            return bf
        except OSError:
            (filelist, masked) = self.collect_bbfiles()
            regexp = re.compile(buildfile)
            matches = []
            for f in filelist:
                if regexp.search(f) and os.path.isfile(f):
                    bf = f
                    matches.append(f)
            if len(matches) != 1:
                bb.msg.error(bb.msg.domain.Parsing, "Unable to match %s (%s matches found):" % (buildfile, len(matches)))
                for f in matches:
                    bb.msg.error(bb.msg.domain.Parsing, "    %s" % f)
                return False
            return matches[0]

    def buildFile(self, buildfile):
        """
        Build the file matching regexp buildfile
        """

        # Make sure our target is a fully qualified filename
        fn = self.matchFile(buildfile)
        if not fn:
            return False

        # Load data into the cache for fn and parse the loaded cache data
        self.bb_cache = bb.cache.init(self)
        self.status = bb.cache.CacheData()
        self.bb_cache.loadData(fn, self.configuration.data, self.status)

        # Tweak some variables
        item = self.bb_cache.getVar('PN', fn, True)
        self.status.ignored_dependencies = set()
        self.status.bbfile_priority[fn] = 1

        # Remove external dependencies
        self.status.task_deps[fn]['depends'] = {}
        self.status.deps[fn] = []
        self.status.rundeps[fn] = []
        self.status.runrecs[fn] = []

        # Remove stamp for target if force mode active
        if self.configuration.force:
            bb.msg.note(2, bb.msg.domain.RunQueue, "Remove stamp %s, %s" % (self.configuration.cmd, fn))
            bb.build.del_stamp('do_%s' % self.configuration.cmd, self.configuration.data)

        # Setup taskdata structure
        taskdata = bb.taskdata.TaskData(self.configuration.abort, self.configuration.tryaltconfigs)
        taskdata.add_provider(self.configuration.data, self.status, item)

        buildname = bb.data.getVar("BUILDNAME", self.configuration.data)
        bb.event.fire(bb.event.BuildStarted(buildname, [item], self.configuration.event_data))

        # Execute the runqueue
        runlist = [[item, "do_%s" % self.configuration.cmd]]
        rq = bb.runqueue.RunQueue(self, self.configuration.data, self.status, taskdata, runlist)
        rq.prepare_runqueue()
        try:
            failures = rq.execute_runqueue()
        except runqueue.TaskFailure, fnids:
            failures = 0
            for fnid in fnids:
                bb.msg.error(bb.msg.domain.Build, "'%s' failed" % taskdata.fn_index[fnid])
                failures = failures + 1
            bb.event.fire(bb.event.BuildCompleted(buildname, [item], self.configuration.event_data, failures))
            return False
        bb.event.fire(bb.event.BuildCompleted(buildname, [item], self.configuration.event_data, failures))
        return True

    def buildTargets(self, targets):
        """
        Attempt to build the targets specified
        """

        buildname = bb.data.getVar("BUILDNAME", self.configuration.data)
        bb.event.fire(bb.event.BuildStarted(buildname, targets, self.configuration.event_data))

        localdata = data.createCopy(self.configuration.data)
        bb.data.update_data(localdata)
        bb.data.expandKeys(localdata)

        taskdata = bb.taskdata.TaskData(self.configuration.abort, self.configuration.tryaltconfigs)

        runlist = []
        try:
            for k in targets:
                taskdata.add_provider(localdata, self.status, k)
                runlist.append([k, "do_%s" % self.configuration.cmd])
            taskdata.add_unresolved(localdata, self.status)
        except bb.providers.NoProvider:
            sys.exit(1)

        rq = bb.runqueue.RunQueue(self, self.configuration.data, self.status, taskdata, runlist)
        rq.prepare_runqueue()
        try:
            failures = rq.execute_runqueue()
        except runqueue.TaskFailure, fnids:
            failures = 0
            for fnid in fnids:
                bb.msg.error(bb.msg.domain.Build, "'%s' failed" % taskdata.fn_index[fnid])
                failures = failures + 1
            bb.event.fire(bb.event.BuildCompleted(buildname, targets, self.configuration.event_data, failures))
            sys.exit(1)
        bb.event.fire(bb.event.BuildCompleted(buildname, targets, self.configuration.event_data, failures))

        sys.exit(0)

    def updateCache(self):
	# SamyGO: remove suport Psyco, we use builded native python
        self.status = bb.cache.CacheData()

        ignore = bb.data.getVar("ASSUME_PROVIDED", self.configuration.data, 1) or ""
        self.status.ignored_dependencies = set( ignore.split() )

        self.handleCollections( bb.data.getVar("BBFILE_COLLECTIONS", self.configuration.data, 1) )

        bb.msg.debug(1, bb.msg.domain.Collection, "collecting .bb files")
        (filelist, masked) = self.collect_bbfiles()
        bb.data.renameVar("__depends", "__base_depends", self.configuration.data)
        self.parse_bbfiles(filelist, masked, self.myProgressCallback)
        bb.msg.debug(1, bb.msg.domain.Collection, "parsing complete")

        self.buildDepgraph()

    def cook(self):
        """
        We are building stuff here. We do the building
        from here. By default we try to execute task
        build.
        """

        # Wipe the OS environment
        bb.utils.empty_environment()

        if self.configuration.show_environment:
            self.showEnvironment(self.configuration.buildfile, self.configuration.pkgs_to_build)
            sys.exit( 0 )

        self.buildSetVars()

        if self.configuration.interactive:
            self.interactiveMode()

        if self.configuration.buildfile is not None:
            if not self.buildFile(self.configuration.buildfile):
                sys.exit(1)
            sys.exit(0)

        # initialise the parsing status now we know we will need deps
        self.updateCache()

        if self.configuration.parse_only:
            bb.msg.note(1, bb.msg.domain.Collection, "Requested parsing .bb files only.  Exiting.")
            return 0

        pkgs_to_build = self.configuration.pkgs_to_build

        if len(pkgs_to_build) == 0 and not self.configuration.show_versions:
                print "Nothing to do.  Use 'bitbake world' to build everything, or run 'bitbake --help'"
                print "for usage information."
                sys.exit(0)

        try:
            if self.configuration.show_versions:
                self.showVersions()
                sys.exit( 0 )
            if 'world' in pkgs_to_build:
                self.buildWorldTargetList()
                pkgs_to_build.remove('world')
                for t in self.status.world_target:
                    pkgs_to_build.append(t)

            if self.configuration.dot_graph:
                self.generateDotGraph( pkgs_to_build, self.configuration.ignored_dot_deps )
                sys.exit( 0 )

            return self.buildTargets(pkgs_to_build)

        except KeyboardInterrupt:
            bb.msg.note(1, bb.msg.domain.Collection, "KeyboardInterrupt - Build not completed.")
            sys.exit(1)

    def get_bbfiles( self, path = os.getcwd() ):
        """Get list of default .bb files by reading out the current directory"""
        contents = os.listdir(path)
        bbfiles = []
        for f in contents:
            (root, ext) = os.path.splitext(f)
            if ext == ".bb":
                bbfiles.append(os.path.abspath(os.path.join(os.getcwd(),f)))
        return bbfiles

    def find_bbfiles( self, path ):
        """Find all the .bb files in a directory"""
        from os.path import join

        found = []
        for dir, dirs, files in os.walk(path):
            for ignored in ('SCCS', 'CVS', '.svn'):
                if ignored in dirs:
                    dirs.remove(ignored)
            found += [join(dir,f) for f in files if f.endswith('.bb')]

        return found

    def collect_bbfiles( self ):
        """Collect all available .bb build files"""
        parsed, cached, skipped, masked = 0, 0, 0, 0
        self.bb_cache = bb.cache.init(self)

        files = (data.getVar( "BBFILES", self.configuration.data, 1 ) or "").split()
        data.setVar("BBFILES", " ".join(files), self.configuration.data)

        if not len(files):
            files = self.get_bbfiles()

        if not len(files):
            bb.msg.error(bb.msg.domain.Collection, "no files to build.")

        newfiles = []
        for f in files:
            if os.path.isdir(f):
                dirfiles = self.find_bbfiles(f)
                if dirfiles:
                    newfiles += dirfiles
                    continue
            else:
                globbed = glob.glob(f)
                if not globbed and os.path.exists(f):
                    globbed = [f]
                newfiles += globbed

        bbmask = bb.data.getVar('BBMASK', self.configuration.data, 1)

        if not bbmask:
            return (newfiles, 0)

        try:
            bbmask_compiled = re.compile(bbmask)
        except sre_constants.error:
            bb.msg.fatal(bb.msg.domain.Collection, "BBMASK is not a valid regular expression.")

        finalfiles = []
        for f in newfiles:
            if bbmask_compiled.search(f):
                bb.msg.debug(1, bb.msg.domain.Collection, "skipping masked file %s" % f)
                masked += 1
                continue
            finalfiles.append(f)

        return (finalfiles, masked)

    def parse_bbfiles(self, filelist, masked, progressCallback = None):
        parsed, cached, skipped, error = 0, 0, 0, 0
        for i in xrange( len( filelist ) ):
            f = filelist[i]

            #bb.msg.debug(1, bb.msg.domain.Collection, "parsing %s" % f)

            # read a file's metadata
            try:
                fromCache, skip = self.bb_cache.loadData(f, self.configuration.data, self.status)
                if skip:
                    skipped += 1
                    bb.msg.debug(2, bb.msg.domain.Collection, "skipping %s" % f)
                    self.bb_cache.skip(f)
                    continue
                elif fromCache: cached += 1
                else: parsed += 1

                # Disabled by RP as was no longer functional
                # allow metadata files to add items to BBFILES
                #data.update_data(self.pkgdata[f])
                #addbbfiles = self.bb_cache.getVar('BBFILES', f, False) or None
                #if addbbfiles:
                #    for aof in addbbfiles.split():
                #        if not files.count(aof):
                #            if not os.path.isabs(aof):
                #                aof = os.path.join(os.path.dirname(f),aof)
                #            files.append(aof)

                # now inform the caller
                if progressCallback is not None:
                    progressCallback( i + 1, len( filelist ), f, fromCache )

            except IOError, e:
                self.bb_cache.remove(f)
                bb.msg.error(bb.msg.domain.Collection, "opening %s: %s" % (f, e))
                pass
            except KeyboardInterrupt:
                self.bb_cache.sync()
                raise
            except Exception, e:
                error += 1
                self.bb_cache.remove(f)
                bb.msg.error(bb.msg.domain.Collection, "%s while parsing %s" % (e, f))
            except:
                self.bb_cache.remove(f)
                raise

        if progressCallback is not None:
            print "\r" # need newline after Handling Bitbake files message
            bb.msg.note(1, bb.msg.domain.Collection, "Parsing finished. %d cached, %d parsed, %d skipped, %d masked." % ( cached, parsed, skipped, masked ))

        self.bb_cache.sync()

        if error > 0:
            bb.msg.fatal(bb.msg.domain.Collection, "Parsing errors found, exiting...")
