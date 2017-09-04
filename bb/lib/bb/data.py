# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: nil -*-
"""
BitBake 'Data' implementations

Functions for interacting with the data structure used by the
BitBake build tools.

The expandData and update_data are the most expensive
operations. At night the cookie monster came by and
suggested 'give me cookies on setting the variables and
things will work out'. Taking this suggestion into account
applying the skills from the not yet passed 'Entwurf und
Analyse von Algorithmen' lecture and the cookie 
monster seems to be right. We will track setVar more carefully
to have faster update_data and expandKeys operations.

This is a treade-off between speed and memory again but
the speed is more critical here.
"""

# Copyright (C) 2003, 2004  Chris Larson
# Copyright (C) 2005        Holger Hans Peter Freyther
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
#Based on functions from the base bb module, Copyright 2003 Holger Schurig

import sys, os, re, types
if sys.argv[0][-5:] == "pydoc":
    path = os.path.dirname(os.path.dirname(sys.argv[1]))
else:
    path = os.path.dirname(os.path.dirname(sys.argv[0]))
sys.path.insert(0,path)

from bb import data_smart
import bb

class VarExpandError(Exception):
    pass

_dict_type = data_smart.DataSmart

def init():
    return _dict_type()

def init_db(parent = None):
    if parent:
        return parent.createCopy()
    else:
        return _dict_type()

def createCopy(source):
     """Link the source set to the destination
     If one does not find the value in the destination set,
     search will go on to the source set to get the value.
     Value from source are copy-on-write. i.e. any try to
     modify one of them will end up putting the modified value
     in the destination set.
     """
     return source.createCopy()

def initVar(var, d):
    """Non-destructive var init for data structure"""
    d.initVar(var)


def setVar(var, value, d):
    """Set a variable to a given value

    Example:
        >>> d = init()
        >>> setVar('TEST', 'testcontents', d)
        >>> print getVar('TEST', d)
        testcontents
    """
    d.setVar(var,value)


def getVar(var, d, exp = 0):
    """Gets the value of a variable

    Example:
        >>> d = init()
        >>> setVar('TEST', 'testcontents', d)
        >>> print getVar('TEST', d)
        testcontents
    """
    return d.getVar(var,exp)


def renameVar(key, newkey, d):
    """Renames a variable from key to newkey

    Example:
        >>> d = init()
        >>> setVar('TEST', 'testcontents', d)
        >>> renameVar('TEST', 'TEST2', d)
        >>> print getVar('TEST2', d)
        testcontents
    """
    d.renameVar(key, newkey)

def delVar(var, d):
    """Removes a variable from the data set

    Example:
        >>> d = init()
        >>> setVar('TEST', 'testcontents', d)
        >>> print getVar('TEST', d)
        testcontents
        >>> delVar('TEST', d)
        >>> print getVar('TEST', d)
        None
    """
    d.delVar(var)

def setVarFlag(var, flag, flagvalue, d):
    """Set a flag for a given variable to a given value

    Example:
        >>> d = init()
        >>> setVarFlag('TEST', 'python', 1, d)
        >>> print getVarFlag('TEST', 'python', d)
        1
    """
    d.setVarFlag(var,flag,flagvalue)

def getVarFlag(var, flag, d):
    """Gets given flag from given var

    Example:
        >>> d = init()
        >>> setVarFlag('TEST', 'python', 1, d)
        >>> print getVarFlag('TEST', 'python', d)
        1
    """
    return d.getVarFlag(var,flag)

def delVarFlag(var, flag, d):
    """Removes a given flag from the variable's flags

    Example:
        >>> d = init()
        >>> setVarFlag('TEST', 'testflag', 1, d)
        >>> print getVarFlag('TEST', 'testflag', d)
        1
        >>> delVarFlag('TEST', 'testflag', d)
        >>> print getVarFlag('TEST', 'testflag', d)
        None

    """
    d.delVarFlag(var,flag)

def setVarFlags(var, flags, d):
    """Set the flags for a given variable

    Note:
        setVarFlags will not clear previous
        flags. Think of this method as
        addVarFlags

    Example:
        >>> d = init()
        >>> myflags = {}
        >>> myflags['test'] = 'blah'
        >>> setVarFlags('TEST', myflags, d)
        >>> print getVarFlag('TEST', 'test', d)
        blah
    """
    d.setVarFlags(var,flags)

def getVarFlags(var, d):
    """Gets a variable's flags

    Example:
        >>> d = init()
        >>> setVarFlag('TEST', 'test', 'blah', d)
        >>> print getVarFlags('TEST', d)['test']
        blah
    """
    return d.getVarFlags(var)

def delVarFlags(var, d):
    """Removes a variable's flags

    Example:
        >>> data = init()
        >>> setVarFlag('TEST', 'testflag', 1, data)
        >>> print getVarFlag('TEST', 'testflag', data)
        1
        >>> delVarFlags('TEST', data)
        >>> print getVarFlags('TEST', data)
        None

    """
    d.delVarFlags(var)

def keys(d):
    """Return a list of keys in d

    Example:
        >>> d = init()
        >>> setVar('TEST',  1, d)
        >>> setVar('MOO' ,  2, d)
        >>> setVarFlag('TEST', 'test', 1, d)
        >>> keys(d)
        ['TEST', 'MOO']
    """
    return d.keys()

def getData(d):
    """Returns the data object used"""
    return d

def setData(newData, d):
    """Sets the data object to the supplied value"""
    d = newData


##
## Cookie Monsters' query functions
##
def _get_override_vars(d, override):
    """
    Internal!!!

    Get the Names of Variables that have a specific
    override. This function returns a iterable
    Set or an empty list
    """
    return []

def _get_var_flags_triple(d):
    """
    Internal!!!

    """
    return []

__expand_var_regexp__ = re.compile(r"\${[^{}]+}")
__expand_python_regexp__ = re.compile(r"\${@.+?}")

def expand(s, d, varname = None):
    """Variable expansion using the data store.

    Example:
        Standard expansion:
        >>> d = init()
        >>> setVar('A', 'sshd', d)
        >>> print expand('/usr/bin/${A}', d)
        /usr/bin/sshd

        Python expansion:
        >>> d = init()
        >>> print expand('result: ${@37 * 72}', d)
        result: 2664

        Shell expansion:
        >>> d = init()
        >>> print expand('${TARGET_MOO}', d)
        ${TARGET_MOO}
        >>> setVar('TARGET_MOO', 'yupp', d)
        >>> print expand('${TARGET_MOO}',d)
        yupp
        >>> setVar('SRC_URI', 'http://somebug.${TARGET_MOO}', d)
        >>> delVar('TARGET_MOO', d)
        >>> print expand('${SRC_URI}', d)
        http://somebug.${TARGET_MOO}
    """
    return d.expand(s, varname)

def expandKeys(alterdata, readdata = None):
    if readdata == None:
        readdata = alterdata

    todolist = {}
    for key in keys(alterdata):
        if not '${' in key:
            continue

        ekey = expand(key, readdata)
        if key == ekey:
            continue
        todolist[key] = ekey

    # These two for loops are split for performance to maximise the 
    # usefulness of the expand cache

    for key in todolist:
        ekey = todolist[key]
        renameVar(key, ekey, alterdata)

def expandData(alterdata, readdata = None):
    """For each variable in alterdata, expand it, and update the var contents.
       Replacements use data from readdata.

    Example:
        >>> a=init()
        >>> b=init()
        >>> setVar("dlmsg", "dl_dir is ${DL_DIR}", a)
        >>> setVar("DL_DIR", "/path/to/whatever", b)
        >>> expandData(a, b)
        >>> print getVar("dlmsg", a)
        dl_dir is /path/to/whatever
       """
    if readdata == None:
        readdata = alterdata

    for key in keys(alterdata):
        val = getVar(key, alterdata)
        if type(val) is not types.StringType:
            continue
        expanded = expand(val, readdata)
#       print "key is %s, val is %s, expanded is %s" % (key, val, expanded)
        if val != expanded:
            setVar(key, expanded, alterdata)

def inheritFromOS(d):
    """Inherit variables from the environment."""
    for s in os.environ.keys():
        try:
            setVar(s, os.environ[s], d)
            setVarFlag(s, "export", True, d)
        except TypeError:
            pass

def emit_var(var, o=sys.__stdout__, d = init(), all=False):
    """Emit a variable to be sourced by a shell."""
    if getVarFlag(var, "python", d):
        return 0

    export = getVarFlag(var, "export", d)
    unexport = getVarFlag(var, "unexport", d)
    func = getVarFlag(var, "func", d)
    if not all and not export and not unexport and not func:
        return 0

    try:
        if all:
            oval = getVar(var, d, 0)
        val = getVar(var, d, 1)
    except KeyboardInterrupt:
        raise
    except:
        excname = str(sys.exc_info()[0])
        if excname == "bb.build.FuncFailed":
            raise
        o.write('# expansion of %s threw %s\n' % (var, excname))
        return 0

    if all:
        o.write('# %s=%s\n' % (var, oval))

    if type(val) is not types.StringType:
        return 0

    if (var.find("-") != -1 or var.find(".") != -1 or var.find('{') != -1 or var.find('}') != -1 or var.find('+') != -1) and not all:
        return 0

    varExpanded = expand(var, d)

    if unexport:
        o.write('unset %s\n' % varExpanded)
        return 1

    val.rstrip()
    if not val:
        return 0

    if func:
        # NOTE: should probably check for unbalanced {} within the var
        o.write("%s() {\n%s\n}\n" % (varExpanded, val))
        return 1

    if export:
        o.write('export ')

    # if we're going to output this within doublequotes,
    # to a shell, we need to escape the quotes in the var
    alter = re.sub('"', '\\"', val.strip())
    o.write('%s="%s"\n' % (varExpanded, alter))
    return 1


def emit_env(o=sys.__stdout__, d = init(), all=False):
    """Emits all items in the data store in a format such that it can be sourced by a shell."""

    env = keys(d)

    for e in env:
        if getVarFlag(e, "func", d):
            continue
        emit_var(e, o, d, all) and o.write('\n')

    for e in env:
        if not getVarFlag(e, "func", d):
            continue
        emit_var(e, o, d) and o.write('\n')

def update_data(d):
    """Modifies the environment vars according to local overrides and commands.
    Examples:
        Appending to a variable:
        >>> d = init()
        >>> setVar('TEST', 'this is a', d)
        >>> setVar('TEST_append', ' test', d)
        >>> setVar('TEST_append', ' of the emergency broadcast system.', d)
        >>> update_data(d)
        >>> print getVar('TEST', d)
        this is a test of the emergency broadcast system.

        Prepending to a variable:
        >>> setVar('TEST', 'virtual/libc', d)
        >>> setVar('TEST_prepend', 'virtual/tmake ', d)
        >>> setVar('TEST_prepend', 'virtual/patcher ', d)
        >>> update_data(d)
        >>> print getVar('TEST', d)
        virtual/patcher virtual/tmake virtual/libc

        Overrides:
        >>> setVar('TEST_arm', 'target', d)
        >>> setVar('TEST_ramses', 'machine', d)
        >>> setVar('TEST_local', 'local', d)
        >>> setVar('OVERRIDES', 'arm', d)

        >>> setVar('TEST', 'original', d)
        >>> update_data(d)
        >>> print getVar('TEST', d)
        target

        >>> setVar('OVERRIDES', 'arm:ramses:local', d)
        >>> setVar('TEST', 'original', d)
        >>> update_data(d)
        >>> print getVar('TEST', d)
        local

        CopyMonster:
        >>> e = d.createCopy()
        >>> setVar('TEST_foo', 'foo', e)
        >>> update_data(e)
        >>> print getVar('TEST', e)
        local

        >>> setVar('OVERRIDES', 'arm:ramses:local:foo', e)
        >>> update_data(e)
        >>> print getVar('TEST', e)
        foo

        >>> f = d.createCopy()
        >>> setVar('TEST_moo', 'something', f)
        >>> setVar('OVERRIDES', 'moo:arm:ramses:local:foo', e)
        >>> update_data(e)
        >>> print getVar('TEST', e)
        foo


        >>> h = init()
        >>> setVar('SRC_URI', 'file://append.foo;patch=1 ', h)
        >>> g = h.createCopy()
        >>> setVar('SRC_URI_append_arm', 'file://other.foo;patch=1', g)
        >>> setVar('OVERRIDES', 'arm:moo', g)
        >>> update_data(g)
        >>> print getVar('SRC_URI', g)
        file://append.foo;patch=1 file://other.foo;patch=1

    """
    bb.msg.debug(2, bb.msg.domain.Data, "update_data()")

    # now ask the cookie monster for help
    #print "Cookie Monster"
    #print "Append/Prepend %s" % d._special_values
    #print "Overrides      %s" % d._seen_overrides

    overrides = (getVar('OVERRIDES', d, 1) or "").split(':') or []

    #
    # Well let us see what breaks here. We used to iterate
    # over each variable and apply the override and then
    # do the line expanding.
    # If we have bad luck - which we will have - the keys
    # where in some order that is so important for this
    # method which we don't have anymore.
    # Anyway we will fix that and write test cases this
    # time.

    #
    # First we apply all overrides
    # Then  we will handle _append and _prepend
    #

    for o in overrides:
        # calculate '_'+override
        l    = len(o)+1

        # see if one should even try
        if not d._seen_overrides.has_key(o):
            continue

        vars = d._seen_overrides[o]
        for var in vars:
            name = var[:-l]
            try:
                d[name] = d[var]
            except:
                bb.msg.note(1, bb.msg.domain.Data, "Untracked delVar")

    # now on to the appends and prepends
    if d._special_values.has_key('_append'):
        appends = d._special_values['_append'] or []
        for append in appends:
            for (a, o) in getVarFlag(append, '_append', d) or []:
                # maybe the OVERRIDE was not yet added so keep the append
                if (o and o in overrides) or not o:
                    delVarFlag(append, '_append', d)
                if o and not o in overrides:
                    continue

                sval = getVar(append,d) or ""
                sval+=a
                setVar(append, sval, d)


    if d._special_values.has_key('_prepend'):
        prepends = d._special_values['_prepend'] or []

        for prepend in prepends:
            for (a, o) in getVarFlag(prepend, '_prepend', d) or []:
                # maybe the OVERRIDE was not yet added so keep the prepend
                if (o and o in overrides) or not o:
                    delVarFlag(prepend, '_prepend', d)
                if o and not o in overrides:
                    continue

                sval = a + (getVar(prepend,d) or "")
                setVar(prepend, sval, d)


def inherits_class(klass, d):
    val = getVar('__inherit_cache', d) or []
    if os.path.join('classes', '%s.bbclass' % klass) in val:
        return True
    return False

def _test():
    """Start a doctest run on this module"""
    import doctest
    import bb
    from bb import data
    bb.msg.set_debug_level(0)
    doctest.testmod(data)

if __name__ == "__main__":
    _test()
