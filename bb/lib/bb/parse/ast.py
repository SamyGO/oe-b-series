# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
 AbstractSyntaxTree classes for the Bitbake language
"""

# Copyright (C) 2003, 2004 Chris Larson
# Copyright (C) 2003, 2004 Phil Blundell
# Copyright (C) 2009 Holger Hans Peter Freyther
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import bb, re, string
from itertools import chain

__word__ = re.compile(r"\S+")
__parsed_methods__ = bb.methodpool.get_parsed_dict()
_bbversions_re = re.compile(r"\[(?P<from>[0-9]+)-(?P<to>[0-9]+)\]")

class StatementGroup(list):
    def eval(self, data):
        map(lambda x: x.eval(data), self)

class AstNode(object):
    pass

class IncludeNode(AstNode):
    def __init__(self, what_file, fn, lineno, force):
        self.what_file = what_file
        self.from_fn = fn
        self.from_lineno = lineno
        self.force = force

    def eval(self, data):
        """
        Include the file and evaluate the statements
        """
        s = bb.data.expand(self.what_file, data)
        bb.msg.debug(3, bb.msg.domain.Parsing, "CONF %s:%d: including %s" % (self.from_fn, self.from_lineno, s))

        # TODO: Cache those includes... maybe not here though
        if self.force:
            bb.parse.ConfHandler.include(self.from_fn, s, data, "include required")
        else:
            bb.parse.ConfHandler.include(self.from_fn, s, data, False)

class ExportNode(AstNode):
    def __init__(self, var):
        self.var = var

    def eval(self, data):
        bb.data.setVarFlag(self.var, "export", 1, data)

class DataNode(AstNode):
    """
    Various data related updates. For the sake of sanity
    we have one class doing all this. This means that all
    this need to be re-evaluated... we might be able to do
    that faster with multiple classes.
    """
    def __init__(self, groupd):
        self.groupd = groupd

    def getFunc(self, key, data):
        if 'flag' in self.groupd and self.groupd['flag'] != None:
            return bb.data.getVarFlag(key, self.groupd['flag'], data)
        else:
            return bb.data.getVar(key, data)

    def eval(self, data):
        groupd = self.groupd
        key = groupd["var"]
        if "exp" in groupd and groupd["exp"] != None:
            bb.data.setVarFlag(key, "export", 1, data)
        if "ques" in groupd and groupd["ques"] != None:
            val = self.getFunc(key, data)
            if val == None:
                val = groupd["value"]
        elif "colon" in groupd and groupd["colon"] != None:
            e = data.createCopy()
            bb.data.update_data(e)
            val = bb.data.expand(groupd["value"], e)
        elif "append" in groupd and groupd["append"] != None:
            val = "%s %s" % ((self.getFunc(key, data) or ""), groupd["value"])
        elif "prepend" in groupd and groupd["prepend"] != None:
            val = "%s %s" % (groupd["value"], (self.getFunc(key, data) or ""))
        elif "postdot" in groupd and groupd["postdot"] != None:
            val = "%s%s" % ((self.getFunc(key, data) or ""), groupd["value"])
        elif "predot" in groupd and groupd["predot"] != None:
            val = "%s%s" % (groupd["value"], (self.getFunc(key, data) or ""))
        else:
            val = groupd["value"]

        if 'flag' in groupd and groupd['flag'] != None:
            bb.msg.debug(3, bb.msg.domain.Parsing, "setVarFlag(%s, %s, %s, data)" % (key, groupd['flag'], val))
            bb.data.setVarFlag(key, groupd['flag'], val, data)
        elif groupd["lazyques"]:
            assigned = bb.data.getVar("__lazy_assigned", data) or []
            assigned.append(key)
            bb.data.setVar("__lazy_assigned", assigned, data)
            bb.data.setVarFlag(key, "defaultval", val, data)
        else:
            bb.data.setVar(key, val, data)

class MethodNode:
    def __init__(self, func_name, body, lineno, fn):
        self.func_name = func_name
        self.body = body
        self.fn = fn
        self.lineno = lineno

    def eval(self, data):
        if self.func_name == "__anonymous":
            funcname = ("__anon_%s_%s" % (self.lineno, self.fn.translate(string.maketrans('/.+-', '____'))))
            if not funcname in bb.methodpool._parsed_fns:
                text = "def %s(d):\n" % (funcname) + '\n'.join(self.body)
                bb.methodpool.insert_method(funcname, text, self.fn)
            anonfuncs = bb.data.getVar('__BBANONFUNCS', data) or []
            anonfuncs.append(funcname)
            bb.data.setVar('__BBANONFUNCS', anonfuncs, data)
        else:
            bb.data.setVarFlag(self.func_name, "func", 1, data)
            bb.data.setVar(self.func_name, '\n'.join(self.body), data)

class PythonMethodNode(AstNode):
    def __init__(self, root, body, fn):
        self.root = root
        self.body = body
        self.fn = fn

    def eval(self, data):
        # Note we will add root to parsedmethods after having parse
        # 'this' file. This means we will not parse methods from
        # bb classes twice
        if not bb.methodpool.parsed_module(self.root):
            text = '\n'.join(self.body)
            bb.methodpool.insert_method(self.root, text, self.fn)

class MethodFlagsNode(AstNode):
    def __init__(self, key, m):
        self.key = key
        self.m = m

    def eval(self, data):
        if bb.data.getVar(self.key, data):
            # clean up old version of this piece of metadata, as its
            # flags could cause problems
            bb.data.setVarFlag(self.key, 'python', None, data)
            bb.data.setVarFlag(self.key, 'fakeroot', None, data)
        if self.m.group("py") is not None:
            bb.data.setVarFlag(self.key, "python", "1", data)
        else:
            bb.data.delVarFlag(self.key, "python", data)
        if self.m.group("fr") is not None:
            bb.data.setVarFlag(self.key, "fakeroot", "1", data)
        else:
            bb.data.delVarFlag(self.key, "fakeroot", data)

class ExportFuncsNode(AstNode):
    def __init__(self, fns, classes):
        self.n = __word__.findall(fns)
        self.classes = classes

    def eval(self, data):
        for f in self.n:
            allvars = []
            allvars.append(f)
            allvars.append(self.classes[-1] + "_" + f)

            vars = [[ allvars[0], allvars[1] ]]
            if len(self.classes) > 1 and self.classes[-2] is not None:
                allvars.append(self.classes[-2] + "_" + f)
                vars = []
                vars.append([allvars[2], allvars[1]])
                vars.append([allvars[0], allvars[2]])

            for (var, calledvar) in vars:
                if bb.data.getVar(var, data) and not bb.data.getVarFlag(var, 'export_func', data):
                    continue

                if bb.data.getVar(var, data):
                    bb.data.setVarFlag(var, 'python', None, data)
                    bb.data.setVarFlag(var, 'func', None, data)

                for flag in [ "func", "python" ]:
                    if bb.data.getVarFlag(calledvar, flag, data):
                        bb.data.setVarFlag(var, flag, bb.data.getVarFlag(calledvar, flag, data), data)
                for flag in [ "dirs" ]:
                    if bb.data.getVarFlag(var, flag, data):
                        bb.data.setVarFlag(calledvar, flag, bb.data.getVarFlag(var, flag, data), data)

                if bb.data.getVarFlag(calledvar, "python", data):
                    bb.data.setVar(var, "\tbb.build.exec_func('" + calledvar + "', d)\n", data)
                else:
                    bb.data.setVar(var, "\t" + calledvar + "\n", data)
                bb.data.setVarFlag(var, 'export_func', '1', data)

class AddTaskNode(AstNode):
    def __init__(self, func, before, after):
        self.func = func
        self.before = before
        self.after = after

    def eval(self, data):
        var = self.func
        if self.func[:3] != "do_":
            var = "do_" + self.func

        bb.data.setVarFlag(var, "task", 1, data)
        bbtasks = bb.data.getVar('__BBTASKS', data) or []
        if not var in bbtasks:
            bbtasks.append(var)
        bb.data.setVar('__BBTASKS', bbtasks, data)

        existing = bb.data.getVarFlag(var, "deps", data) or []
        if self.after is not None:
            # set up deps for function
            for entry in self.after.split():
                if entry not in existing:
                    existing.append(entry)
        bb.data.setVarFlag(var, "deps", existing, data)
        if self.before is not None:
            # set up things that depend on this func
            for entry in self.before.split():
                existing = bb.data.getVarFlag(entry, "deps", data) or []
                if var not in existing:
                    bb.data.setVarFlag(entry, "deps", [var] + existing, data)

class BBHandlerNode(AstNode):
    def __init__(self, fns):
        self.hs = __word__.findall(fns)

    def eval(self, data):
        bbhands = bb.data.getVar('__BBHANDLERS', data) or []
        for h in self.hs:
            bbhands.append(h)
            bb.data.setVarFlag(h, "handler", 1, data)
        bb.data.setVar('__BBHANDLERS', bbhands, data)

class InheritNode(AstNode):
    def __init__(self, files):
        self.n = __word__.findall(files)

    def eval(self, data):
        bb.parse.BBHandler.inherit(self.n, data)
 
def handleInclude(statements, m, fn, lineno, force):
    statements.append(IncludeNode(m.group(1), fn, lineno, force))

def handleExport(statements, m):
    statements.append(ExportNode(m.group(1)))

def handleData(statements, groupd):
    statements.append(DataNode(groupd))

def handleMethod(statements, func_name, lineno, fn, body):
    statements.append(MethodNode(func_name, body, lineno, fn))

def handlePythonMethod(statements, root, body, fn):
    statements.append(PythonMethodNode(root, body, fn))

def handleMethodFlags(statements, key, m):
    statements.append(MethodFlagsNode(key, m))

def handleExportFuncs(statements, m, classes):
    statements.append(ExportFuncsNode(m.group(1), classes))

def handleAddTask(statements, m):
    func = m.group("func")
    before = m.group("before")
    after = m.group("after")
    if func is None:
        return

    statements.append(AddTaskNode(func, before, after))

def handleBBHandlers(statements, m):
    statements.append(BBHandlerNode(m.group(1)))

def handleInherit(statements, m):
    files = m.group(1)
    n = __word__.findall(files)
    statements.append(InheritNode(m.group(1)))

def finalise(fn, d):
    for lazykey in bb.data.getVar("__lazy_assigned", d) or ():
        if bb.data.getVar(lazykey, d) is None:
            val = bb.data.getVarFlag(lazykey, "defaultval", d)
            bb.data.setVar(lazykey, val, d)

    bb.data.expandKeys(d)
    bb.data.update_data(d)
    code = []
    for funcname in bb.data.getVar("__BBANONFUNCS", d) or []:
        code.append("%s(d)" % funcname)
    bb.utils.simple_exec("\n".join(code), {"d": d})
    bb.data.update_data(d)

    all_handlers = {}
    for var in bb.data.getVar('__BBHANDLERS', d) or []:
        # try to add the handler
        handler = bb.data.getVar(var,d)
        bb.event.register(var, handler)

    tasklist = bb.data.getVar('__BBTASKS', d) or []
    bb.build.add_tasks(tasklist, d)

    bb.event.fire(bb.event.RecipeParsed(fn), d)

def _create_variants(datastores, names, function):
    def create_variant(name, orig_d, arg = None):
        new_d = bb.data.createCopy(orig_d)
        function(arg or name, new_d)
        datastores[name] = new_d

    for variant, variant_d in datastores.items():
        for name in names:
            if not variant:
                # Based on main recipe
                create_variant(name, variant_d)
            else:
                create_variant("%s-%s" % (variant, name), variant_d, name)

def _expand_versions(versions):
    def expand_one(version, start, end):
        for i in xrange(start, end + 1):
            ver = _bbversions_re.sub(str(i), version, 1)
            yield ver

    versions = iter(versions)
    while True:
        try:
            version = versions.next()
        except StopIteration:
            break

        range_ver = _bbversions_re.search(version)
        if not range_ver:
            yield version
        else:
            newversions = expand_one(version, int(range_ver.group("from")),
                                     int(range_ver.group("to")))
            versions = chain(newversions, versions)

def multi_finalize(fn, d):
    safe_d = d

    d = bb.data.createCopy(safe_d)
    try:
        finalise(fn, d)
    except bb.parse.SkipPackage:
        bb.data.setVar("__SKIPPED", True, d)
    datastores = {"": safe_d}

    versions = (d.getVar("BBVERSIONS", True) or "").split()
    if versions:
        pv = orig_pv = d.getVar("PV", True)
        baseversions = {}

        def verfunc(ver, d, pv_d = None):
            if pv_d is None:
                pv_d = d

            overrides = d.getVar("OVERRIDES", True).split(":")
            pv_d.setVar("PV", ver)
            overrides.append(ver)
            bpv = baseversions.get(ver) or orig_pv
            pv_d.setVar("BPV", bpv)
            overrides.append(bpv)
            d.setVar("OVERRIDES", ":".join(overrides))

        versions = list(_expand_versions(versions))
        for pos, version in enumerate(list(versions)):
            try:
                pv, bpv = version.split(":", 2)
            except ValueError:
                pass
            else:
                versions[pos] = pv
                baseversions[pv] = bpv

        if pv in versions and not baseversions.get(pv):
            versions.remove(pv)
        else:
            pv = versions.pop()

            # This is necessary because our existing main datastore
            # has already been finalized with the old PV, we need one
            # that's been finalized with the new PV.
            d = bb.data.createCopy(safe_d)
            verfunc(pv, d, safe_d)
            try:
                finalise(fn, d)
            except bb.parse.SkipPackage:
                bb.data.setVar("__SKIPPED", True, d)

        _create_variants(datastores, versions, verfunc)

    extended = d.getVar("BBCLASSEXTEND", True) or ""
    if extended:
        pn = d.getVar("PN", True)
        def extendfunc(name, d):
            d.setVar("PN", "%s-%s" % (pn, name))
            bb.parse.BBHandler.inherit([name], d)

        safe_d.setVar("BBCLASSEXTEND", extended)
        _create_variants(datastores, extended.split(), extendfunc)

    for variant, variant_d in datastores.items():
        if variant:
            try:
                finalise(fn, variant_d)
            except bb.parse.SkipPackage:
                bb.data.setVar("__SKIPPED", True, variant_d)

    if len(datastores) > 1:
        variants = filter(None, datastores.keys())
        safe_d.setVar("__VARIANTS", " ".join(variants))

    datastores[""] = d
    return datastores
