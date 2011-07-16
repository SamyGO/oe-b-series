#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
   class for handling .bb files

   Reads a .bb file and obtains its metadata

"""


#  Copyright (C) 2003, 2004  Chris Larson
#  Copyright (C) 2003, 2004  Phil Blundell
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

import re, bb, os, sys, time, string
import bb.fetch, bb.build, bb.utils
from bb import data, fetch, methodpool

from ConfHandler import include, localpath, obtain, init
from bb.parse import ParseError

__func_start_regexp__    = re.compile( r"(((?P<py>python)|(?P<fr>fakeroot))\s*)*(?P<func>[\w\.\-\+\{\}\$]+)?\s*\(\s*\)\s*{$" )
__inherit_regexp__       = re.compile( r"inherit\s+(.+)" )
__export_func_regexp__   = re.compile( r"EXPORT_FUNCTIONS\s+(.+)" )
__addtask_regexp__       = re.compile("addtask\s+(?P<func>\w+)\s*((before\s*(?P<before>((.*(?=after))|(.*))))|(after\s*(?P<after>((.*(?=before))|(.*)))))*")
__addhandler_regexp__    = re.compile( r"addhandler\s+(.+)" )
__def_regexp__           = re.compile( r"def\s+(\w+).*:" )
__python_func_regexp__   = re.compile( r"(\s+.*)|(^$)" )
__word__ = re.compile(r"\S+")

__infunc__ = ""
__inpython__ = False
__body__   = []
__classname__ = ""
classes = [ None, ]

# We need to indicate EOF to the feeder. This code is so messy that
# factoring it out to a close_parse_file method is out of question.
# We will use the IN_PYTHON_EOF as an indicator to just close the method
#
# The two parts using it are tightly integrated anyway
IN_PYTHON_EOF = -9999999999999

__parsed_methods__ = methodpool.get_parsed_dict()

def supports(fn, d):
    localfn = localpath(fn, d)
    return localfn[-3:] == ".bb" or localfn[-8:] == ".bbclass" or localfn[-4:] == ".inc"

def inherit(files, d):
    __inherit_cache = data.getVar('__inherit_cache', d) or []
    fn = ""
    lineno = 0
    files = data.expand(files, d)
    for file in files:
        if file[0] != "/" and file[-8:] != ".bbclass":
            file = os.path.join('classes', '%s.bbclass' % file)

        if not file in __inherit_cache:
            bb.msg.debug(2, bb.msg.domain.Parsing, "BB %s:%d: inheriting %s" % (fn, lineno, file))
            __inherit_cache.append( file )
            data.setVar('__inherit_cache', __inherit_cache, d)
            include(fn, file, d, "inherit")
            __inherit_cache = data.getVar('__inherit_cache', d) or []


def finalise(fn, d):
    data.expandKeys(d)
    data.update_data(d)
    anonqueue = data.getVar("__anonqueue", d, 1) or []
    body = [x['content'] for x in anonqueue]
    flag = { 'python' : 1, 'func' : 1 }
    data.setVar("__anonfunc", "\n".join(body), d)
    data.setVarFlags("__anonfunc", flag, d)
    from bb import build
    try:
        t = data.getVar('T', d)
        data.setVar('T', '${TMPDIR}/anonfunc/', d)
        anonfuncs = data.getVar('__BBANONFUNCS', d) or []
        code = ""
        for f in anonfuncs:
            code = code + "    %s(d)\n" % f
        data.setVar("__anonfunc", code, d)        
        build.exec_func("__anonfunc", d)
        data.delVar('T', d)
        if t:
            data.setVar('T', t, d)
    except Exception, e:
        bb.msg.debug(1, bb.msg.domain.Parsing, "Exception when executing anonymous function: %s" % e)
        raise
    data.delVar("__anonqueue", d)
    data.delVar("__anonfunc", d)
    data.update_data(d)

    all_handlers = {} 
    for var in data.getVar('__BBHANDLERS', d) or []:
        # try to add the handler
        handler = data.getVar(var,d)
        bb.event.register(var, handler)

    tasklist = data.getVar('__BBTASKS', d) or []
    bb.build.add_tasks(tasklist, d)


def handle(fn, d, include = 0):
    global __func_start_regexp__, __inherit_regexp__, __export_func_regexp__, __addtask_regexp__, __addhandler_regexp__, __infunc__, __body__, __residue__
    __body__ = []
    __infunc__ = ""
    __classname__ = ""
    __residue__ = []

    if include == 0:
        bb.msg.debug(2, bb.msg.domain.Parsing, "BB " + fn + ": handle(data)")
    else:
        bb.msg.debug(2, bb.msg.domain.Parsing, "BB " + fn + ": handle(data, include)")

    (root, ext) = os.path.splitext(os.path.basename(fn))
    base_name = "%s%s" % (root,ext)
    init(d)

    if ext == ".bbclass":
        __classname__ = root
        classes.append(__classname__)
        __inherit_cache = data.getVar('__inherit_cache', d) or []
        if not fn in __inherit_cache:
            __inherit_cache.append(fn)
            data.setVar('__inherit_cache', __inherit_cache, d)

    if include != 0:
        oldfile = data.getVar('FILE', d)
    else:
        oldfile = None

    fn = obtain(fn, d)
    bbpath = (data.getVar('BBPATH', d, 1) or '').split(':')
    if not os.path.isabs(fn):
        f = None
        for p in bbpath:
            j = os.path.join(p, fn)
            if os.access(j, os.R_OK):
                abs_fn = j
                f = open(j, 'r')
                break
        if f is None:
            raise IOError("file %s not found" % fn)
    else:
        f = open(fn,'r')
        abs_fn = fn

    if include:
        bb.parse.mark_dependency(d, abs_fn)

    if ext != ".bbclass":
        data.setVar('FILE', fn, d)

    lineno = 0
    while 1:
        lineno = lineno + 1
        s = f.readline()
        if not s: break
        s = s.rstrip()
        feeder(lineno, s, fn, base_name, d)
    if __inpython__:
        # add a blank line to close out any python definition
        feeder(IN_PYTHON_EOF, "", fn, base_name, d)
    if ext == ".bbclass":
        classes.remove(__classname__)
    else:
        if include == 0:
            multi = data.getVar('BBCLASSEXTEND', d, 1)
            if multi:
                based = bb.data.createCopy(d)
                finalise(fn, based)
                darray = {"": based}
                for cls in multi.split():
                    pn = data.getVar('PN', d, True)
                    based = bb.data.createCopy(d)
                    data.setVar('PN', pn + '-' + cls, based)
                    inherit([cls], based)
                    finalise(fn, based)
                    darray[cls] = based
                return darray
            else:
                finalise(fn, d)
        bbpath.pop(0)
    if oldfile:
        bb.data.setVar("FILE", oldfile, d)

    # we have parsed the bb class now
    if ext == ".bbclass" or ext == ".inc":
        __parsed_methods__[base_name] = 1

    return d

def feeder(lineno, s, fn, root, d):
    global __func_start_regexp__, __inherit_regexp__, __export_func_regexp__, __addtask_regexp__, __addhandler_regexp__, __def_regexp__, __python_func_regexp__, __inpython__,__infunc__, __body__, classes, bb, __residue__
    if __infunc__:
        if s == '}':
            __body__.append('')
            if __infunc__ == "__anonymous":
                funcname = ("__anon_%s_%s" % (lineno, fn.translate(string.maketrans('/.+-', '____'))))
                if not funcname in methodpool._parsed_fns:
                    text = "def %s(d):\n" % (funcname) + '\n'.join(__body__)
                    methodpool.insert_method(funcname, text, fn)
                anonfuncs = data.getVar('__BBANONFUNCS', d) or []
                anonfuncs.append(funcname)
                data.setVar('__BBANONFUNCS', anonfuncs, d)
            else:
                data.setVarFlag(__infunc__, "func", 1, d)
                data.setVar(__infunc__, '\n'.join(__body__), d)
            __infunc__ = ""
            __body__ = []
        else:
            __body__.append(s)
        return

    if __inpython__:
        m = __python_func_regexp__.match(s)
        if m and lineno != IN_PYTHON_EOF:
            __body__.append(s)
            return
        else:
            # Note we will add root to parsedmethods after having parse
            # 'this' file. This means we will not parse methods from
            # bb classes twice
            if not root  in __parsed_methods__:
                text = '\n'.join(__body__)
                methodpool.insert_method( root, text, fn )
                funcs = data.getVar('__functions__', d) or {}
                if not funcs.has_key( root ):
                    funcs[root] = text 
                else:
                    funcs[root] = "%s\n%s" % (funcs[root], text)

                data.setVar('__functions__', funcs, d)
            __body__ = []
            __inpython__ = False

            if lineno == IN_PYTHON_EOF:
                return

#           fall through

    if s == '' or s[0] == '#': return          # skip comments and empty lines

    if s[-1] == '\\':
        __residue__.append(s[:-1])
        return

    s = "".join(__residue__) + s
    __residue__ = []

    m = __func_start_regexp__.match(s)
    if m:
        __infunc__ = m.group("func") or "__anonymous"
        key = __infunc__
        if data.getVar(key, d):
#           clean up old version of this piece of metadata, as its
#           flags could cause problems
            data.setVarFlag(key, 'python', None, d)
            data.setVarFlag(key, 'fakeroot', None, d)
        if m.group("py") is not None:
            data.setVarFlag(key, "python", "1", d)
        else:
            data.delVarFlag(key, "python", d)
        if m.group("fr") is not None:
            data.setVarFlag(key, "fakeroot", "1", d)
        else:
            data.delVarFlag(key, "fakeroot", d)
        return

    m = __def_regexp__.match(s)
    if m:
        __body__.append(s)
        __inpython__ = True
        return

    m = __export_func_regexp__.match(s)
    if m:
        fns = m.group(1)
        n = __word__.findall(fns)
        for f in n:
            allvars = []
            allvars.append(f)
            allvars.append(classes[-1] + "_" + f)

            vars = [[ allvars[0], allvars[1] ]]
            if len(classes) > 1 and classes[-2] is not None:
                allvars.append(classes[-2] + "_" + f)
                vars = []
                vars.append([allvars[2], allvars[1]])
                vars.append([allvars[0], allvars[2]])

            for (var, calledvar) in vars:
                if data.getVar(var, d) and not data.getVarFlag(var, 'export_func', d):
                    continue

                if data.getVar(var, d):
                    data.setVarFlag(var, 'python', None, d)
                    data.setVarFlag(var, 'func', None, d)

                for flag in [ "func", "python" ]:
                    if data.getVarFlag(calledvar, flag, d):
                        data.setVarFlag(var, flag, data.getVarFlag(calledvar, flag, d), d)
                for flag in [ "dirs" ]:
                    if data.getVarFlag(var, flag, d):
                        data.setVarFlag(calledvar, flag, data.getVarFlag(var, flag, d), d)

                if data.getVarFlag(calledvar, "python", d):
                    data.setVar(var, "\tbb.build.exec_func('" + calledvar + "', d)\n", d)
                else:
                    data.setVar(var, "\t" + calledvar + "\n", d)
                data.setVarFlag(var, 'export_func', '1', d)

        return

    m = __addtask_regexp__.match(s)
    if m:
        func = m.group("func")
        before = m.group("before")
        after = m.group("after")
        if func is None:
            return
        var = "do_" + func

        data.setVarFlag(var, "task", 1, d)

        bbtasks = data.getVar('__BBTASKS', d) or []
        if not var in bbtasks:
            bbtasks.append(var)
        data.setVar('__BBTASKS', bbtasks, d)

        existing = data.getVarFlag(var, "deps", d) or []
        if after is not None:
            # set up deps for function
            for entry in after.split():
                if entry not in existing:
                    existing.append(entry)
        data.setVarFlag(var, "deps", existing, d)
        if before is not None:
            # set up things that depend on this func
            for entry in before.split():
                existing = data.getVarFlag(entry, "deps", d) or []
                if var not in existing:
                    data.setVarFlag(entry, "deps", [var] + existing, d)
        return

    m = __addhandler_regexp__.match(s)
    if m:
        fns = m.group(1)
        hs = __word__.findall(fns)
        bbhands = data.getVar('__BBHANDLERS', d) or []
        for h in hs:
            bbhands.append(h)
            data.setVarFlag(h, "handler", 1, d)
        data.setVar('__BBHANDLERS', bbhands, d)
        return

    m = __inherit_regexp__.match(s)
    if m:

        files = m.group(1)
        n = __word__.findall(files)
        inherit(n, d)
        return

    from bb.parse import ConfHandler
    return ConfHandler.feeder(lineno, s, fn, d)

__pkgsplit_cache__={}
def vars_from_file(mypkg, d):
    if not mypkg:
        return (None, None, None)
    if mypkg in __pkgsplit_cache__:
        return __pkgsplit_cache__[mypkg]

    myfile = os.path.splitext(os.path.basename(mypkg))
    parts = myfile[0].split('_')
    __pkgsplit_cache__[mypkg] = parts
    if len(parts) > 3:
        raise ParseError("Unable to generate default variables from the filename: %s (too many underscores)" % mypkg)
    exp = 3 - len(parts)
    tmplist = []
    while exp != 0:
        exp -= 1
        tmplist.append(None)
    parts.extend(tmplist)
    return parts

# Add us to the handlers list
from bb.parse import handlers
handlers.append({'supports': supports, 'handle': handle, 'init': init})
del handlers
