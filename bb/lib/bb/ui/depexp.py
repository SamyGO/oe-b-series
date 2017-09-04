#
# BitBake Graphical GTK based Dependency Explorer
#
# Copyright (C) 2007        Ross Burton
# Copyright (C) 2007 - 2008 Richard Purdie
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

import gobject
import gtk
import threading
import xmlrpclib

# Package Model
(COL_PKG_NAME) = (0)

# Dependency Model
(TYPE_DEP, TYPE_RDEP) = (0, 1)
(COL_DEP_TYPE, COL_DEP_PARENT, COL_DEP_PACKAGE) = (0, 1, 2)

class PackageDepView(gtk.TreeView):
    def __init__(self, model, dep_type, label):
        gtk.TreeView.__init__(self)
        self.current = None
        self.dep_type = dep_type
        self.filter_model = model.filter_new()
        self.filter_model.set_visible_func(self._filter)
        self.set_model(self.filter_model)
        #self.connect("row-activated", self.on_package_activated, COL_DEP_PACKAGE)
        self.append_column(gtk.TreeViewColumn(label, gtk.CellRendererText(), text=COL_DEP_PACKAGE))

    def _filter(self, model, iter):
        (this_type, package) = model.get(iter, COL_DEP_TYPE, COL_DEP_PARENT)
        if this_type != self.dep_type: return False
        return package == self.current

    def set_current_package(self, package):
        self.current = package
        self.filter_model.refilter()

class PackageReverseDepView(gtk.TreeView):
    def __init__(self, model, label):
        gtk.TreeView.__init__(self)
        self.current = None
        self.filter_model = model.filter_new()
        self.filter_model.set_visible_func(self._filter)
        self.set_model(self.filter_model)
        self.append_column(gtk.TreeViewColumn(label, gtk.CellRendererText(), text=COL_DEP_PARENT))

    def _filter(self, model, iter):
        package = model.get_value(iter, COL_DEP_PACKAGE)
        return package == self.current

    def set_current_package(self, package):
        self.current = package
        self.filter_model.refilter()

class DepExplorer(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Dependency Explorer")
        self.set_default_size(500, 500)
        self.connect("delete-event", gtk.main_quit)

        # Create the data models
        self.pkg_model = gtk.ListStore(gobject.TYPE_STRING)
        self.depends_model = gtk.ListStore(gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING)

        pane = gtk.HPaned()
        pane.set_position(250)
        self.add(pane)

        # The master list of packages
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.set_shadow_type(gtk.SHADOW_IN)
        self.pkg_treeview = gtk.TreeView(self.pkg_model)
        self.pkg_treeview.get_selection().connect("changed", self.on_cursor_changed)
        self.pkg_treeview.append_column(gtk.TreeViewColumn("Package", gtk.CellRendererText(), text=COL_PKG_NAME))
        pane.add1(scrolled)
        scrolled.add(self.pkg_treeview)

        box = gtk.VBox(homogeneous=True, spacing=4)

        # Runtime Depends
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.set_shadow_type(gtk.SHADOW_IN)
        self.rdep_treeview = PackageDepView(self.depends_model, TYPE_RDEP, "Runtime Depends")
        self.rdep_treeview.connect("row-activated", self.on_package_activated, COL_DEP_PACKAGE)
        scrolled.add(self.rdep_treeview)
        box.add(scrolled)

        # Build Depends
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.set_shadow_type(gtk.SHADOW_IN)
        self.dep_treeview = PackageDepView(self.depends_model, TYPE_DEP, "Build Depends")
        self.dep_treeview.connect("row-activated", self.on_package_activated, COL_DEP_PACKAGE)
        scrolled.add(self.dep_treeview)
        box.add(scrolled)
        pane.add2(box)

        # Reverse Depends
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.set_shadow_type(gtk.SHADOW_IN)
        self.revdep_treeview = PackageReverseDepView(self.depends_model, "Reverse Depends")
        self.revdep_treeview.connect("row-activated", self.on_package_activated, COL_DEP_PARENT)
        scrolled.add(self.revdep_treeview)
        box.add(scrolled)
        pane.add2(box)

        self.show_all()

    def on_package_activated(self, treeview, path, column, data_col):
        model = treeview.get_model()
        package = model.get_value(model.get_iter(path), data_col)

        pkg_path = []
        def finder(model, path, iter, needle):
            package = model.get_value(iter, COL_PKG_NAME)
            if package == needle:
                pkg_path.append(path)
                return True
            else:
                return False
        self.pkg_model.foreach(finder, package)
        if pkg_path:
            self.pkg_treeview.get_selection().select_path(pkg_path[0])
            self.pkg_treeview.scroll_to_cell(pkg_path[0])

    def on_cursor_changed(self, selection):
        (model, it) = selection.get_selected()
        if iter is None:
            current_package = None
        else:
            current_package = model.get_value(it, COL_PKG_NAME)
        self.rdep_treeview.set_current_package(current_package)
        self.dep_treeview.set_current_package(current_package)
        self.revdep_treeview.set_current_package(current_package)


def parse(depgraph, pkg_model, depends_model):

    for package in depgraph["pn"]:
        pkg_model.set(pkg_model.append(), COL_PKG_NAME, package)

    for package in depgraph["depends"]:
        for depend in depgraph["depends"][package]:
            depends_model.set (depends_model.append(),
                              COL_DEP_TYPE, TYPE_DEP,
                              COL_DEP_PARENT, package,
                              COL_DEP_PACKAGE, depend)

    for package in depgraph["rdepends-pn"]:
        for rdepend in depgraph["rdepends-pn"][package]:
            depends_model.set (depends_model.append(),
                              COL_DEP_TYPE, TYPE_RDEP,
                              COL_DEP_PARENT, package,
                              COL_DEP_PACKAGE, rdepend)

class ProgressBar(gtk.Window):
    def __init__(self):

        gtk.Window.__init__(self)
        self.set_title("Parsing .bb files, please wait...")
        self.set_default_size(500, 0)
        self.connect("delete-event", gtk.main_quit)

        self.progress = gtk.ProgressBar()
        self.add(self.progress)
        self.show_all()

class gtkthread(threading.Thread):
    quit = threading.Event()
    def __init__(self, shutdown):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.shutdown = shutdown

    def run(self):
        gobject.threads_init()
        gtk.gdk.threads_init()
        gtk.main()
        gtkthread.quit.set()

def init(server, eventHandler):

    try:
        cmdline = server.runCommand(["getCmdLineAction"])
        if not cmdline or cmdline[0] != "generateDotGraph":
            print "This UI is only compatible with the -g option"
            return
        ret = server.runCommand(["generateDepTreeEvent", cmdline[1], cmdline[2]])
        if ret != True:
            print "Couldn't run command! %s" % ret
            return
    except xmlrpclib.Fault, x:
        print "XMLRPC Fault getting commandline:\n %s" % x
        return

    shutdown = 0

    gtkgui = gtkthread(shutdown)
    gtkgui.start()

    gtk.gdk.threads_enter()
    pbar = ProgressBar()
    dep = DepExplorer()
    gtk.gdk.threads_leave()

    while True:
        try:
            event = eventHandler.waitEvent(0.25)
            if gtkthread.quit.isSet():
                break

            if event is None:
                continue
            if isinstance(event, bb.event.ParseProgress):
                x = event.sofar
                y = event.total
                if x == y:
                    print("\nParsing finished. %d cached, %d parsed, %d skipped, %d masked, %d errors." 
                        % ( event.cached, event.parsed, event.skipped, event.masked, event.errors))
                    pbar.hide()
                gtk.gdk.threads_enter()
                pbar.progress.set_fraction(float(x)/float(y))
                pbar.progress.set_text("%d/%d (%2d %%)" % (x, y, x*100/y))
                gtk.gdk.threads_leave()
                continue

            if isinstance(event, bb.event.DepTreeGenerated):
                gtk.gdk.threads_enter()
                parse(event._depgraph, dep.pkg_model, dep.depends_model)
                gtk.gdk.threads_leave()

            if isinstance(event, bb.command.CookerCommandCompleted):
                continue
            if isinstance(event, bb.command.CookerCommandFailed):
                print "Command execution failed: %s" % event.error
                break
            if isinstance(event, bb.cooker.CookerExit):
                break

            continue

        except KeyboardInterrupt:
            if shutdown == 2:
                print "\nThird Keyboard Interrupt, exit.\n"
                break
            if shutdown == 1:
                print "\nSecond Keyboard Interrupt, stopping...\n"
                server.runCommand(["stateStop"])
            if shutdown == 0:
                print "\nKeyboard Interrupt, closing down...\n"
                server.runCommand(["stateShutdown"])
            shutdown = shutdown + 1
            pass

